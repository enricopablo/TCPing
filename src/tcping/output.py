"""Ways to display results: terminal (rich) or JSON (NDJSON).

The loop in cli.py only measures; the chosen output decides what is shown.
Every output has the same interface: error, critical, start, attempt, finish.
"""

import json
import socket

from rich.console import Console
from rich.live import Live
from rich.markup import escape
from rich.table import Table


def _header(console, when, text, count, per_target=False):
    header = f"\n🚀 [{when:%Y-%m-%d %H:%M:%S}] Testing TCP: {text}"
    if count > 0:
        noun = "attempt" if count == 1 else "attempts"
        header += f" ({count} {noun}{' per target' if per_target else ''})"
    console.print(header, style="bold cyan")


def _status_text(success, error):
    if success:
        return "[bold green]OPEN[/bold green]"
    return f"[bold red]CLOSED[/bold red] ({escape(error)})"


def _min_avg_max(stats):
    if not stats:
        return "-"
    avg, mn, mx, _ = stats
    return f"{mn:.2f} / {avg:.2f} / {mx:.2f} ms"


class _RichBase:
    def __init__(self, report=False, console=None):
        self.console = console or Console()
        self.report = report

    def error(self, target):
        self.console.print(
            f"❌ {escape(target.label)}: {escape(target.error)}", style="bold red"
        )

    def critical(self, message):
        self.console.print(f"\n❌ Unexpected error: {escape(message)}", style="bold red")


class RichOutput(_RichBase):
    """Terminal, one target: table on the first attempt, then one line per attempt."""

    def __init__(self, report=False, console=None):
        super().__init__(report, console)
        self._first_attempt = True

    def start(self, when, targets, count):
        t = targets[0]
        if t.ip == t.host:
            text = f"[bold green]{escape(t.address)}[/bold green]"
        else:
            text = (
                f"[bold green]{escape(t.host)}[/bold green] ({escape(t.ip)}):"
                f"[underline]{t.port}[/underline]"
            )
        _header(self.console, when, text, count)

    def attempt(self, seq, when, target, success, latency, error):
        if self.report:
            return
        timestamp = f"{when:%Y-%m-%d %H:%M:%S}"
        label = escape(target.label)
        status = _status_text(success, error)
        latency_text = f"{latency:.2f}ms" if success else "-"

        if self._first_attempt:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Timestamp", style="dim")
            table.add_column("Host:Port")
            table.add_column("Status", justify="center")
            table.add_column("Latency", justify="right")
            table.add_row(timestamp, label, status, latency_text)
            self.console.print(table)
            self._first_attempt = False
        else:
            icon = "🟢" if success else "🔴"
            self.console.print(f"{icon} {timestamp} | {label} | {status} | {latency_text}")

    def finish(self, targets, duration_s):
        s = targets[0].summary(duration_s)
        if s["attempts"] == 0:
            return
        lat = s["latency_ms"]
        if lat:
            lat_text = f"[bold]{lat['min']:.2f} / {lat['avg']:.2f} / {lat['max']:.2f} ms[/]"
            jitter_text = f"[bold magenta]{lat['jitter']:.2f} ms[/]"
        else:  # no successful connection: no latency to show
            lat_text = jitter_text = "-"

        table = Table(show_header=False, box=None)
        table.add_row(
            "Success / Failed", f"[green]{s['success']}🟢[/] / [red]{s['failed']}🔴[/]"
        )
        table.add_row("Success Rate", f"[bold cyan]{s['success_rate']:.2f}%[/]")
        table.add_row("Latency (Min/Avg/Max)", lat_text)
        table.add_row("Jitter", jitter_text)
        table.add_row("Total Time", f"{s['duration_s']:.2f}s")

        self.console.print("\n📊 [bold white]Summary[/bold white]")
        self.console.print(table)


class RichMultiOutput(_RichBase):
    """Terminal, several targets: live-updating table and side-by-side summary."""

    def __init__(self, report=False, console=None):
        super().__init__(report, console)
        self._live = None
        self._targets = []

    def start(self, when, targets, count):
        self._targets = targets
        n = len(targets)
        text = f"[bold green]{n} {'target' if n == 1 else 'targets'}[/bold green]"
        _header(self.console, when, text, count, per_target=True)
        if not self.report:
            self._live = Live(
                self._live_table(), console=self.console, auto_refresh=False
            )
            self._live.start()

    def _live_table(self):
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Target")
        table.add_column("IP", style="dim")
        table.add_column("Status", justify="center")
        table.add_column("Last", justify="right")
        table.add_column("Min / Avg / Max", justify="right")
        table.add_column("Jitter", justify="right")
        table.add_column("History")
        for t in self._targets:
            stats = t.stats()
            if t.last is None:
                status, last = "[dim]waiting…[/dim]", "-"
            else:
                success, latency, error = t.last
                status = _status_text(success, error)
                last = f"{latency:.2f}ms" if success else "-"
            table.add_row(
                escape(t.label),
                escape(t.ip),
                status,
                last,
                _min_avg_max(stats),
                f"{stats[3]:.2f} ms" if stats else "-",
                "".join("🟢" if ok else "🔴" for ok in t.history),
            )
        return table

    def attempt(self, seq, when, target, success, latency, error):
        if self._live:
            self._live.update(self._live_table(), refresh=True)

    def finish(self, targets, duration_s):
        if self._live:
            self._live.stop()
        if not any(t.success_count + t.fail_count for t in targets):
            return

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Target")
        table.add_column("IP", style="dim")
        table.add_column("Success / Failed", justify="center")
        table.add_column("Rate", justify="right")
        table.add_column("Min / Avg / Max", justify="right")
        table.add_column("Jitter", justify="right")
        for t in targets:
            s = t.summary(duration_s)
            stats = t.stats()
            rate = f"{s['success_rate']:.2f}%" if s["success_rate"] is not None else "-"
            table.add_row(
                escape(t.label),
                escape(t.ip),
                f"[green]{s['success']}🟢[/] / [red]{s['failed']}🔴[/]",
                f"[bold cyan]{rate}[/]",
                _min_avg_max(stats),
                f"[magenta]{stats[3]:.2f} ms[/]" if stats else "-",
            )

        self.console.print()
        self.console.print("📊 [bold white]Summary[/bold white]")
        self.console.print(table)
        self.console.print(f"Total Time: {duration_s:.2f}s")


class JsonOutput:
    """One JSON line per event (NDJSON). With report=True only the summaries are emitted."""

    def __init__(self, report=False):
        self.report = report

    def _emit(self, data):
        print(json.dumps(data, ensure_ascii=False), flush=True)

    def error(self, target):
        self._emit(
            {"type": "error", "host": target.host, "port": target.port, "error": target.error}
        )

    def critical(self, message):
        self._emit({"type": "error", "error": message})

    def start(self, when, targets, count):
        pass

    def attempt(self, seq, when, target, success, latency, error):
        if self.report:
            return
        self._emit(
            {
                "type": "attempt",
                "host": target.host,
                "ip": target.ip,
                "port": target.port,
                "seq": seq,
                "timestamp": when.isoformat(timespec="seconds"),
                "status": "open" if success else "closed",
                "latency_ms": round(latency, 2) if success else None,
                "error": error,
            }
        )

    def finish(self, targets, duration_s):
        for t in targets:
            self._emit(
                {
                    "type": "summary",
                    "host": t.host,
                    "ip": t.ip,
                    "port": t.port,
                    "family": "ipv6" if t.family == socket.AF_INET6 else "ipv4",
                    **t.summary(duration_s),
                }
            )


def make_output(as_json, report, multi):
    if as_json:
        return JsonOutput(report)
    return RichMultiOutput(report) if multi else RichOutput(report)
