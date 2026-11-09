"""Exit codes, --report / -r and --json."""

import json

from click.testing import CliRunner

from tcping.cli import main


def run(*args):
    return CliRunner().invoke(main, [str(a) for a in args])


def json_lines(output):
    return [json.loads(line) for line in output.splitlines() if line.strip()]


# --- Exit codes (same meaning as ping) -----------------------------------


def test_exit_0_when_port_open(open_port):
    assert run("127.0.0.1", open_port, "-c", 1).exit_code == 0


def test_exit_1_when_no_reply(closed_port):
    assert run("127.0.0.1", closed_port, "-c", 2, "-i", 0).exit_code == 1


def test_exit_0_with_partial_success(open_port, monkeypatch):
    # 1st attempt fails, 2nd succeeds -> 0 (same as ping)
    results = iter([(False, None, "Refused"), (True, 5.0, None)])
    monkeypatch.setattr("tcping.cli.check_tcp_port", lambda *a: next(results))
    assert run("127.0.0.1", open_port, "-c", 2, "-i", 0).exit_code == 0


# --- --report / -r -------------------------------------------------------


def test_report_hides_attempts_keeps_header_and_summary(open_port):
    for flag in ("-r", "--report"):
        result = run("127.0.0.1", open_port, "-c", 2, "-i", 0, flag)
        assert result.exit_code == 0
        assert "Testing TCP" in result.output
        assert "Summary" in result.output
        assert "OPEN" not in result.output


# --- --json --------------------------------------------------------------


def test_json_attempts_and_summary(open_port):
    result = run("127.0.0.1", open_port, "-c", 2, "-i", 0, "--json")
    assert result.exit_code == 0
    lines = json_lines(result.output)
    assert [line["type"] for line in lines] == ["attempt", "attempt", "summary"]

    attempt = lines[0]
    assert attempt["seq"] == 1
    assert attempt["status"] == "open"
    assert attempt["latency_ms"] > 0
    assert attempt["error"] is None

    summary = lines[-1]
    assert summary["host"] == "127.0.0.1"
    assert summary["ip"] == "127.0.0.1"
    assert summary["port"] == open_port
    assert summary["family"] == "ipv4"
    assert summary["attempts"] == 2
    assert summary["success_rate"] == 100.0
    assert set(summary["latency_ms"]) == {"min", "avg", "max", "jitter"}


def test_json_report_only_summary(open_port):
    result = run("127.0.0.1", open_port, "-c", 2, "-i", 0, "--json", "-r")
    lines = json_lines(result.output)
    assert [line["type"] for line in lines] == ["summary"]


def test_json_failed_attempt_uses_null(closed_port):
    result = run("127.0.0.1", closed_port, "-c", 1, "--json")
    assert result.exit_code == 1
    attempt, summary = json_lines(result.output)
    assert attempt["status"] == "closed"
    assert attempt["latency_ms"] is None
    assert attempt["error"] == "Refused"
    assert summary["latency_ms"] is None


def test_json_invalid_host_error():
    result = run("host-inexistente.invalid", 80, "--json")
    assert result.exit_code == 2
    assert json_lines(result.output) == [
        {
            "type": "error",
            "host": "host-inexistente.invalid",
            "port": 80,
            "error": "Host not found",
        }
    ]


def test_json_ipv6_family(open_port_v6):
    result = run("::1", open_port_v6, "-c", 1, "--json", "-r")
    assert json_lines(result.output)[0]["family"] == "ipv6"
