import errno
import socket
import time


class ResolveError(Exception):
    """Host name resolution failed."""


def resolve(host, port, family=socket.AF_UNSPEC):
    """Resolves the host once and returns (family, sockaddr).

    Done before the loop so DNS time is not included in the measured latency.
    """
    try:
        infos = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
    except socket.gaierror as e:
        if family != socket.AF_UNSPEC:
            version = "IPv4" if family == socket.AF_INET else "IPv6"
            raise ResolveError(f"Host not found or has no {version} address") from e
        raise ResolveError("Host not found") from e
    if not infos:
        raise ResolveError("Host not found")
    fam, _, _, _, sockaddr = infos[0]
    return fam, sockaddr


def format_address(family, sockaddr):
    """Formats IP:port, with brackets for IPv6 ([::1]:443)."""
    ip, port = sockaddr[0], sockaddr[1]
    return f"[{ip}]:{port}" if family == socket.AF_INET6 else f"{ip}:{port}"


_ERRNO_MESSAGES = {
    errno.ENETUNREACH: "Network unreachable",
    errno.EHOSTUNREACH: "Host unreachable",
}


def check_tcp_port(family, sockaddr, timeout):
    """Attempts the TCP handshake and returns (success, latency_ms | None, error | None)."""
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    start = time.perf_counter()
    try:
        sock.connect(sockaddr)
        return True, (time.perf_counter() - start) * 1000, None
    except TimeoutError:
        return False, None, "Timeout"
    except ConnectionRefusedError:
        return False, None, "Refused"
    except OSError as e:
        return False, None, _ERRNO_MESSAGES.get(e.errno, e.strerror or str(e))
    finally:
        sock.close()
