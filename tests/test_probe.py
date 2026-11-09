import socket

import pytest

from tcping.probe import ResolveError, check_tcp_port, format_address, resolve


def test_resolve_ipv4_literal():
    family, sockaddr = resolve("127.0.0.1", 80)
    assert family == socket.AF_INET
    assert sockaddr == ("127.0.0.1", 80)


def test_resolve_invalid_host():
    with pytest.raises(ResolveError, match="Host não encontrado"):
        resolve("host-inexistente.invalid", 80)


def test_resolve_forced_ipv4_with_ipv6_literal():
    with pytest.raises(ResolveError, match="IPv4"):
        resolve("::1", 80, socket.AF_INET)


def test_format_address_ipv4():
    assert format_address(socket.AF_INET, ("1.1.1.1", 443)) == "1.1.1.1:443"


def test_format_address_ipv6_uses_brackets():
    assert format_address(socket.AF_INET6, ("::1", 443, 0, 0)) == "[::1]:443"


def test_check_open_port(open_port):
    family, sockaddr = resolve("127.0.0.1", open_port)
    success, latency, error = check_tcp_port(family, sockaddr, timeout=1)
    assert success is True
    assert latency > 0
    assert error is None


def test_check_refused_port(closed_port):
    family, sockaddr = resolve("127.0.0.1", closed_port)
    success, latency, error = check_tcp_port(family, sockaddr, timeout=1)
    assert success is False
    assert latency is None
    assert error == "Recusada"


def test_check_open_port_ipv6(open_port_v6):
    family, sockaddr = resolve("::1", open_port_v6)
    assert family == socket.AF_INET6
    success, _, _ = check_tcp_port(family, sockaddr, timeout=1)
    assert success is True
