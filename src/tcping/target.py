"""Alvos (host + porta): interpretação dos argumentos, resolução e estatísticas."""

import socket
from collections import deque
from dataclasses import dataclass, field

from tcping.probe import ResolveError, format_address, resolve
from tcping.stats import calculate_stats, summarize

HISTORY_SIZE = 10  # tentativas exibidas na coluna "Histórico"


def target_label(host, port):
    """host:porta, com colchetes para IPv6 literal ([::1]:443)."""
    return f"[{host}]:{port}" if ":" in host else f"{host}:{port}"


def parse_targets(values):
    """Separa os argumentos em hosts e portas: números são portas, o resto são hosts.

    Retorna (hosts, portas) sem duplicatas, na ordem informada.
    Levanta ValueError com mensagem amigável em caso de erro.
    """
    hosts, ports = [], []
    for value in values:
        if value.isdigit():
            port = int(value)
            if not 1 <= port <= 65535:
                raise ValueError(f"Porta inválida: {value} (use de 1 a 65535).")
            ports.append(port)
        else:
            hosts.append(value)
    if not hosts:
        raise ValueError("Informe ao menos um host.")
    if not ports:
        raise ValueError("Informe ao menos uma porta.")
    return list(dict.fromkeys(hosts)), list(dict.fromkeys(ports))


@dataclass
class Target:
    host: str
    port: int
    family: int = socket.AF_UNSPEC
    sockaddr: tuple | None = None
    error: str | None = None  # erro de resolução (DNS)
    success_count: int = 0
    fail_count: int = 0
    latencies: list = field(default_factory=list)
    history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_SIZE))
    last: tuple | None = None  # (sucesso, latência, erro) da última tentativa

    @property
    def label(self):
        return target_label(self.host, self.port)

    @property
    def ip(self):
        return self.sockaddr[0] if self.sockaddr else None

    @property
    def address(self):
        return format_address(self.family, self.sockaddr)

    def record(self, success, latency, error):
        if success:
            self.success_count += 1
            self.latencies.append(latency)
        else:
            self.fail_count += 1
        self.history.append(success)
        self.last = (success, latency, error)

    def stats(self):
        """(média, mín, máx, jitter) ou None se não houve sucesso."""
        return calculate_stats(self.latencies) if self.latencies else None

    def summary(self, duration_s):
        return summarize(self.success_count, self.fail_count, self.latencies, duration_s)


def build_targets(hosts, ports, family=socket.AF_UNSPEC):
    """Cria um alvo por combinação host x porta. Cada host é resolvido uma única vez."""
    targets = []
    for host in hosts:
        try:
            fam, sockaddr = resolve(host, ports[0], family)
            error = None
        except ResolveError as e:
            fam, sockaddr, error = family, None, str(e)
        for port in ports:
            t = Target(host, port, error=error)
            if not error:
                t.family = fam
                t.sockaddr = (sockaddr[0], port, *sockaddr[2:])
            targets.append(t)
    return targets
