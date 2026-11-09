"""Option validation, interval timing and Ctrl+C handling."""

import _thread
import json
import subprocess
import sys
import textwrap
import time

import pytest
from click.testing import CliRunner

from tcping.cli import main


def run(*args):
    return CliRunner().invoke(main, [str(a) for a in args], env={"COLUMNS": "200"})


def json_lines(output):
    return [json.loads(line) for line in output.splitlines() if line.strip()]


# --- Validation ------------------------------------------------------------


@pytest.mark.parametrize(
    "option, value",
    [
        ("-c", -1),
        ("-c", "abc"),
        ("-i", -1),
        ("-t", 0),
        ("-t", -2),
    ],
)
def test_invalid_option_values_are_usage_errors(option, value, monkeypatch):
    called = []
    monkeypatch.setattr("tcping.cli.check_tcp_port", lambda *a: called.append(a))
    result = run("127.0.0.1", 80, option, value)
    assert result.exit_code == 2
    assert "Invalid value" in result.output
    assert not called  # nothing is tested


@pytest.mark.parametrize("option, value", [("-i", 0), ("-t", 0.5)])
def test_boundary_values_are_accepted(option, value, open_port):
    result = run("127.0.0.1", open_port, "-c", 2, option, value)
    assert result.exit_code == 0, result.output


def test_count_zero_runs_until_ctrl_c(monkeypatch):
    attempts = []

    def probe(*_):
        attempts.append(1)
        if len(attempts) == 3:
            _thread.interrupt_main()
        return True, 1.0, None

    monkeypatch.setattr("tcping.cli.check_tcp_port", probe)
    result = run("127.0.0.1", 80, "-c", 0, "-i", 0, "--json", "-r")
    assert result.exit_code == 0
    assert json_lines(result.output)[0]["attempts"] >= 2  # the 3rd may be cut short


# --- Interval counted from the start of each round ------------------------


def test_interval_counts_from_round_start(monkeypatch):
    """3 rounds of 0.3s with -i 0.5: ~1.3s (start to start), not ~1.9s."""

    def slow(*_):
        time.sleep(0.3)
        return True, 300.0, None

    monkeypatch.setattr("tcping.cli.check_tcp_port", slow)
    start = time.perf_counter()
    result = run("127.0.0.1", 80, "-c", 3, "-i", 0.5, "-r")
    elapsed = time.perf_counter() - start
    assert result.exit_code == 0
    assert 1.2 < elapsed < 1.6


def test_round_longer_than_interval_starts_next_right_away(monkeypatch):
    sleeps = []
    monkeypatch.setattr("tcping.cli.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(
        "tcping.cli.check_tcp_port",
        lambda *_: (True, 1.0, None),
    )
    real_monotonic = time.monotonic
    clock = iter(range(0, 1000, 5))  # every call advances 5s: rounds "take" > -i
    monkeypatch.setattr("tcping.cli.time.monotonic", lambda: next(clock))
    run("127.0.0.1", 80, "-c", 3, "-i", 1, "-r")
    monkeypatch.setattr("tcping.cli.time.monotonic", real_monotonic)
    assert sleeps == [0.0, 0.0]


# --- Ctrl+C ----------------------------------------------------------------


def test_ctrl_c_mid_round_keeps_finished_attempts(monkeypatch):
    """The slow target (port 1) is still pending; the fast one (port 2) is kept."""

    def probe(family, sockaddr, timeout):
        if sockaddr[1] == 1:
            time.sleep(0.2)  # port 2 has finished by now
            _thread.interrupt_main()
            time.sleep(5)
            return True, 1.0, None
        return True, 2.0, None

    monkeypatch.setattr("tcping.cli.check_tcp_port", probe)
    start = time.perf_counter()
    result = run("127.0.0.1", 1, 2, "-c", 3, "--json", "-r")
    assert time.perf_counter() - start < 2
    summaries = {s["port"]: s for s in json_lines(result.output)}
    assert summaries[1]["attempts"] == 0
    assert summaries[2]["attempts"] == 1
    assert result.exit_code == 1  # port 1 had no reply


def test_ctrl_c_exits_without_waiting_for_pending_connections():
    """In a real process, pending probes must not hold the exit for the timeout."""
    script = textwrap.dedent(
        """
        import _thread, time
        import tcping.cli

        def probe(*_):
            _thread.interrupt_main()
            time.sleep(10)  # a connection stuck until the timeout

        tcping.cli.check_tcp_port = probe
        tcping.cli.main(["127.0.0.1", "80", "-c", "1"])
        """
    )
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=30
    )
    assert time.perf_counter() - start < 5, proc.stderr
    assert proc.returncode == 1
