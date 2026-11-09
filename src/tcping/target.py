"""Targets (host + port): argument parsing, resolution and statistics."""

import socket
from collections import deque
from dataclasses import dataclass, field

from tcping.probe import ResolveError, format_address, resolve
from tcping.stats import calculate_stats, summarize

HISTORY_SIZE = 10  # attempts shown in the "History" column


def target_label(host, port):
    """host:port, with brackets for IPv6 literals ([::1]:443)."""
    return f"[{host}]:{port}" if ":" in host else f"{host}:{port}"


def parse_targets(values):
    """Splits the arguments into hosts and ports: numbers are ports, the rest are hosts.

    Returns (hosts, ports) without duplicates, in the given order.
    Raises ValueError with a friendly message on error.
    """
    hosts, ports = [], []
    for value in values:
        if value.isdigit():
            port = int(value)
            if not 1 <= port <= 65535:
                raise ValueError(f"Invalid port: {value} (use 1 to 65535).")
            ports.append(port)
        else:
            hosts.append(value)
    if not hosts:
        raise ValueError("Provide at least one host.")
    if not ports:
        raise ValueError("Provide at least one port.")
    return list(dict.fromkeys(hosts)), list(dict.fromkeys(ports))


@dataclass
class Target:
    host: str
    port: int
    family: int = socket.AF_UNSPEC
    sockaddr: tuple | None = None
    error: str | None = None  # resolution (DNS) error
    success_count: int = 0
    fail_count: int = 0
    latencies: list = field(default_factory=list)
    history: deque = field(default_factory=lambda: deque(maxlen=HISTORY_SIZE))
    last: tuple | None = None  # (success, latency, error) of the last attempt

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
        """(avg, min, max, jitter) or None if there was no success."""
        return calculate_stats(self.latencies) if self.latencies else None

    def summary(self, duration_s):
        return summarize(self.success_count, self.fail_count, self.latencies, duration_s)


def build_targets(hosts, ports, family=socket.AF_UNSPEC):
    """Creates one target per host x port combination. Each host is resolved only once."""
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
