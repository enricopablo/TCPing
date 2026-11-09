import errno
import socket
import time


class ResolveError(Exception):
    """Falha ao resolver o nome do host."""


def resolve(host, port, family=socket.AF_UNSPEC):
    """Resolve o host uma única vez e retorna (família, sockaddr).

    Feito antes do loop para que o tempo de DNS não entre na latência medida.
    """
    try:
        infos = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
    except socket.gaierror as e:
        if family != socket.AF_UNSPEC:
            versao = "IPv4" if family == socket.AF_INET else "IPv6"
            raise ResolveError(f"Host não encontrado ou sem endereço {versao}") from e
        raise ResolveError("Host não encontrado") from e
    if not infos:
        raise ResolveError("Host não encontrado")
    fam, _, _, _, sockaddr = infos[0]
    return fam, sockaddr


def format_address(family, sockaddr):
    """Formata IP:porta, usando colchetes para IPv6 ([::1]:443)."""
    ip, port = sockaddr[0], sockaddr[1]
    return f"[{ip}]:{port}" if family == socket.AF_INET6 else f"{ip}:{port}"


_ERRNO_MESSAGES = {
    errno.ENETUNREACH: "Rede inalcançável",
    errno.EHOSTUNREACH: "Host inalcançável",
}


def check_tcp_port(family, sockaddr, timeout):
    """Tenta o handshake TCP e retorna (sucesso, latência_ms | None, erro | None)."""
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    start = time.perf_counter()
    try:
        sock.connect(sockaddr)
        return True, (time.perf_counter() - start) * 1000, None
    except TimeoutError:
        return False, None, "Timeout"
    except ConnectionRefusedError:
        return False, None, "Recusada"
    except OSError as e:
        return False, None, _ERRNO_MESSAGES.get(e.errno, e.strerror or str(e))
    finally:
        sock.close()
