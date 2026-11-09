"""TCPING - Utilitário de Teste de Conectividade TCP."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tcping")
except PackageNotFoundError:  # rodando direto do código-fonte, sem instalar
    __version__ = "dev"
