import socket

import pytest


@pytest.fixture
def open_port():
    """Porta TCP local aceitando conexões (o kernel completa o handshake após listen())."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
    yield srv.getsockname()[1]
    srv.close()


@pytest.fixture
def closed_port():
    """Porta TCP local sem ninguém escutando (conexão recusada)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def open_port_v6():
    """Porta TCP em ::1; pula o teste se o ambiente não tiver IPv6."""
    try:
        srv = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        srv.bind(("::1", 0))
    except OSError:
        pytest.skip("IPv6 indisponível neste ambiente")
    srv.listen(16)
    yield srv.getsockname()[1]
    srv.close()
