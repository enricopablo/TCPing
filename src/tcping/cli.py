import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import click

from tcping import __version__
from tcping.output import make_output
from tcping.probe import check_tcp_port
from tcping.target import build_targets, parse_targets

# Códigos de saída (mesma semântica do ping, generalizada para vários alvos)
EXIT_OK = 0  # todos os alvos tiveram ao menos uma conexão bem-sucedida
EXIT_NO_REPLY = 1  # algum alvo não teve nenhuma conexão bem-sucedida
EXIT_ERROR = 2  # erro de uso, host não encontrado ou erro inesperado

MAX_WORKERS = 64  # limite de testes simultâneos

EXAMPLES = """\b
Exemplos:
  tcping google.com 443             Roda até Ctrl+C
  tcping 1.1.1.1 80 -c 10           10 tentativas
  tcping 1.1.1.1 80 -c 10 -i 0.5    10 tentativas, intervalo de 0.5s
  tcping meu-servidor 22 -t 5       Timeout de 5s por tentativa
  tcping -6 google.com 443          Força IPv6
  tcping google.com 443 -c 5 -r     Só o relatório final
  tcping google.com 443 -c 5 --json Saída em JSON (uma linha por evento)
  tcping web1 web2 443              Vários hosts na mesma porta
  tcping google.com 80 443          Várias portas no mesmo host
  tcping web1 web2 80 443           Todas as combinações (4 alvos)
"""


def _probe(target, timeout):
    """Executado em paralelo: testa um alvo e registra quando terminou."""
    success, latency, error = check_tcp_port(target.family, target.sockaddr, timeout)
    return success, latency, error, datetime.now()


@click.command(epilog=EXAMPLES, context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("args", nargs=-1, required=True, metavar="HOST... PORT...")
@click.option(
    "--count",
    "-c",
    default=0,
    type=int,
    help="Número de pings por alvo (0 para infinito).",
    show_default=True,
)
@click.option(
    "--interval", "-i", default=1.0, help="Intervalo (segundos).", show_default=True
)
@click.option(
    "--timeout", "-t", default=2.0, help="Timeout (segundos).", show_default=True
)
@click.option("-4", "ipv4", is_flag=True, help="Força o uso de IPv4.")
@click.option("-6", "ipv6", is_flag=True, help="Força o uso de IPv6.")
@click.option(
    "--report", "-r", is_flag=True, help="Exibe só o relatório final, sem as tentativas."
)
@click.option(
    "--json", "as_json", is_flag=True, help="Saída em JSON (uma linha por evento)."
)
@click.version_option(__version__, "--version", "-V", prog_name="tcping")
def main(args, count, interval, timeout, ipv4, ipv6, report, as_json):
    """TCPING - Utilitário de Teste de Conectividade TCP."""

    if ipv4 and ipv6:
        raise click.UsageError("Use apenas uma das opções -4 ou -6.")
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

    start_run = time.time()
    unexpected_error = False
    pool = ThreadPoolExecutor(max_workers=min(len(active), MAX_WORKERS))
    current_round = 0

    try:
        while count == 0 or current_round < count:
            current_round += 1
            # Todos os alvos da rodada são testados ao mesmo tempo
            futures = [(t, pool.submit(_probe, t, timeout)) for t in active]
            for t, future in futures:
                success, latency, error, when = future.result()
                t.record(success, latency, error)
                out.attempt(current_round, when, t, success, latency, error)

            if count == 0 or current_round < count:
                time.sleep(interval)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        out.critical(str(e))
        unexpected_error = True
    finally:
        pool.shutdown(wait=False, cancel_futures=True)

    out.finish(active, time.time() - start_run)

    if unexpected_error or unresolved:
        sys.exit(EXIT_ERROR)
    sys.exit(EXIT_OK if all(t.success_count for t in active) else EXIT_NO_REPLY)
