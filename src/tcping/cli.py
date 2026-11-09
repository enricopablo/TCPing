import socket
import sys
import threading
import time
from datetime import datetime

import click

from tcping import __version__
from tcping.output import make_output
from tcping.probe import check_tcp_port
from tcping.target import build_targets, parse_targets

# Exit codes (same meaning as ping, generalized to multiple targets)
EXIT_OK = 0  # every target had at least one successful connection
EXIT_NO_REPLY = 1  # some target had no successful connection
EXIT_ERROR = 2  # usage error, host not found or unexpected error

JOIN_POLL_S = 0.1  # wait in short slices so Ctrl+C is handled promptly (Windows too)

EXAMPLES = """\b
Examples:
  tcping google.com 443             Run until Ctrl+C
  tcping 1.1.1.1 80 -c 10           10 attempts
  tcping 1.1.1.1 80 -c 10 -i 0.5    10 attempts, 0.5s interval
  tcping my-server 22 -t 5          5s timeout per attempt
  tcping -6 google.com 443          Force IPv6
  tcping google.com 443 -c 5 -r     Final report only
  tcping google.com 443 -c 5 --json JSON output (one line per event)
  tcping web1 web2 443              Several hosts, same port
  tcping google.com 80 443          Several ports, same host
  tcping web1 web2 80 443           Every combination (4 targets)
"""


class _Probe(threading.Thread):
    """Tests one target in the background.

    Daemon thread: on Ctrl+C the program exits right away instead of waiting
    for connections that are still pending (up to the timeout).
    """

    def __init__(self, target, timeout):
        super().__init__(daemon=True)
        self.target = target
        self.timeout = timeout
        self.result = None  # (success, latency, error, finished_at)
        self.exception = None

    def run(self):
        try:
            success, latency, error = check_tcp_port(
                self.target.family, self.target.sockaddr, self.timeout
            )
            self.result = (success, latency, error, datetime.now())
        except Exception as e:  # reported by the main thread
            self.exception = e


def _run_round(seq, targets, timeout, out):
    """Tests every target at the same time and records the results in order.

    If interrupted (Ctrl+C), attempts that already finished are still recorded.
    """
    probes = [_Probe(t, timeout) for t in targets]
    for p in probes:
        p.start()

    pending = list(probes)

    def record(p):
        if p.exception:
            raise p.exception
        success, latency, error, when = p.result
        p.target.record(success, latency, error)
        out.attempt(seq, when, p.target, success, latency, error)

    try:
        while pending:
            p = pending[0]
            while p.is_alive():
                p.join(JOIN_POLL_S)
            record(pending.pop(0))
    except KeyboardInterrupt:
        for p in pending:
            if not p.is_alive() and p.result:
                record(p)
        raise


@click.command(epilog=EXAMPLES, context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("args", nargs=-1, required=True, metavar="HOST... PORT...")
@click.option(
    "--count",
    "-c",
    default=0,
    type=click.IntRange(min=0),
    help="Number of attempts per target (0 = infinite).",
    show_default=True,
)
@click.option(
    "--interval",
    "-i",
    default=1.0,
    type=click.FloatRange(min=0),
    help="Interval between rounds (seconds).",
    show_default=True,
)
@click.option(
    "--timeout",
    "-t",
    default=2.0,
    type=click.FloatRange(min=0, min_open=True),
    help="Timeout per attempt (seconds).",
    show_default=True,
)
@click.option("-4", "ipv4", is_flag=True, help="Force IPv4.")
@click.option("-6", "ipv6", is_flag=True, help="Force IPv6.")
@click.option(
    "--report", "-r", is_flag=True, help="Show only the final report, not each attempt."
)
@click.option(
    "--json", "as_json", is_flag=True, help="JSON output (one line per event)."
)
@click.version_option(__version__, "--version", "-V", prog_name="tcping")
def main(args, count, interval, timeout, ipv4, ipv6, report, as_json):
    """TCPING - TCP connectivity testing tool."""

    if ipv4 and ipv6:
        raise click.UsageError("Use only one of -4 or -6.")
    family = (
        socket.AF_INET if ipv4 else socket.AF_INET6 if ipv6 else socket.AF_UNSPEC
    )

    try:
        hosts, ports = parse_targets(args)
    except ValueError as e:
        raise click.UsageError(str(e)) from e

    targets = build_targets(hosts, ports, family)
    out = make_output(as_json, report, multi=len(targets) > 1)

    unresolved = [t for t in targets if t.error]
    for t in unresolved:
        out.error(t)

    active = [t for t in targets if not t.error]
    if not active:
        sys.exit(EXIT_ERROR)

    out.start(datetime.now(), active, count)

    start_run = time.monotonic()
    unexpected_error = False
    current_round = 0

    try:
        while count == 0 or current_round < count:
            current_round += 1
            round_start = time.monotonic()
            _run_round(current_round, active, timeout, out)

            if count == 0 or current_round < count:
                # Interval counted from the start of the round (like ping):
                # a round longer than the interval starts the next one right away.
                elapsed = time.monotonic() - round_start
                time.sleep(max(0.0, interval - elapsed))

    except KeyboardInterrupt:
        pass
    except Exception as e:
        out.critical(str(e))
        unexpected_error = True

    out.finish(active, time.monotonic() - start_run)

    if unexpected_error or unresolved:
        sys.exit(EXIT_ERROR)
    sys.exit(EXIT_OK if all(t.success_count for t in active) else EXIT_NO_REPLY)
