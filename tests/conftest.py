import socket

import pytest


@pytest.fixture
def open_port():
    """Local TCP port accepting connections (the kernel completes the handshake after listen())."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(16)
    yield srv.getsockname()[1]
    srv.close()


@pytest.fixture
def closed_port():
    """Local TCP port with nothing listening (connection refused)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def open_port_v6():
    """TCP port on ::1; skips the test if the environment has no IPv6."""
    try:
        srv = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        srv.bind(("::1", 0))
    except OSError:
        pytest.skip("IPv6 not available in this environment")
    srv.listen(16)
    yield srv.getsockname()[1]
    srv.close()
