"""Fase 4: vários alvos."""

import json

from click.testing import CliRunner

from tcping.cli import main


def run(*args):
    # Terminal largo para as tabelas não quebrarem os nomes dos alvos
    return CliRunner().invoke(main, [str(a) for a in args], env={"COLUMNS": "200"})


def json_lines(output):
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def test_multi_all_open_exit_0(open_port):
    result = run("127.0.0.1", "localhost", "-4", open_port, "-c", 2, "-i", 0)
    assert result.exit_code == 0
    assert "2 alvos" in result.output
    assert "(2 tentativas por alvo)" in result.output
    assert "Resumo da Execução" in result.output
    assert f"127.0.0.1:{open_port}" in result.output
    assert f"localhost:{open_port}" in result.output


def test_multi_one_without_reply_exit_1(open_port, closed_port):
    result = run("127.0.0.1", open_port, closed_port, "-c", 1)
    assert result.exit_code == 1
    assert "FECHADA" in result.output


def test_multi_report_shows_only_summary(open_port, closed_port):
    result = run("127.0.0.1", open_port, closed_port, "-c", 1, "-r")
    assert "Resumo da Execução" in result.output
    assert "Histórico" not in result.output  # tabela ao vivo não aparece


def test_multi_dns_error_continues_and_exits_2(open_port):
    result = run("host-inexistente.invalid", "127.0.0.1", open_port, "-c", 1)
    assert result.exit_code == 2
    assert "Host não encontrado" in result.output
    assert f"127.0.0.1:{open_port}" in result.output
    assert "Resumo da Execução" in result.output
    assert "1 alvo " in result.output  # singular quando só 1 alvo restou


def test_multi_json(open_port, closed_port):
    result = run("127.0.0.1", open_port, closed_port, "-c", 2, "-i", 0, "--json")
    lines = json_lines(result.output)
    attempts = [line for line in lines if line["type"] == "attempt"]
    summaries = [line for line in lines if line["type"] == "summary"]
    assert len(attempts) == 4
    assert {(a["port"], a["status"]) for a in attempts} == {
        (open_port, "open"),
        (closed_port, "closed"),
    }
    assert all(a["host"] == "127.0.0.1" and a["ip"] == "127.0.0.1" for a in attempts)
    assert [s["port"] for s in summaries] == [open_port, closed_port]
    assert lines[-2:] == summaries  # resumos no fim


def test_multi_json_report_and_dns_error(open_port):
    result = run("host-inexistente.invalid", "127.0.0.1", open_port, "-c", 1, "--json", "-r")
    assert result.exit_code == 2
    types = [line["type"] for line in json_lines(result.output)]
    assert types == ["error", "summary"]


def test_parallel_round_is_not_sequential(closed_port, monkeypatch):
    """Com 4 alvos de 0.3s cada, uma rodada em paralelo leva ~0.3s, não ~1.2s."""
    import time

    def slow(*_):
        time.sleep(0.3)
        return False, None, "Timeout"

    monkeypatch.setattr("tcping.cli.check_tcp_port", slow)
    start = time.perf_counter()
    run("127.0.0.1", 1, 2, 3, 4, "-c", 1)
    assert time.perf_counter() - start < 0.9


def test_usage_errors():
    assert run("443").exit_code == 2
    assert "ao menos um host" in run("443").output
    assert "ao menos uma porta" in run("google.com").output
    assert "Porta inválida" in run("google.com", 70000).output
