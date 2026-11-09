from click.testing import CliRunner

from tcping import __version__
from tcping.cli import main


def run(*args):
    return CliRunner().invoke(main, [str(a) for a in args])


def test_version():
    result = run("--version")
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help_shows_examples():
    for flag in ("-h", "--help"):
        result = run(flag)
        assert result.exit_code == 0
        assert "Exemplos:" in result.output
        assert "Código de saída" not in result.output


def test_ipv4_and_ipv6_together_is_usage_error():
    result = run("-4", "-6", "localhost", 80)
    assert result.exit_code == 2
    assert "-4 ou -6" in result.output


def test_invalid_host_exits_2():
    result = run("host-inexistente.invalid", 80)
    assert result.exit_code == 2
    assert "Host não encontrado" in result.output


def test_open_port_output(open_port):
    result = run("127.0.0.1", open_port, "-c", 2, "-i", 0)
    assert "ABERTA" in result.output
    assert "(2 tentativas)" in result.output
    assert "Resumo da Execução" in result.output


def test_refused_port_output(closed_port):
    result = run("127.0.0.1", closed_port, "-c", 1)
    assert "FECHADA (Recusada)" in result.output
    assert "(1 tentativa)" in result.output
