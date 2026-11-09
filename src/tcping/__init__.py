"""TCPING - TCP connectivity testing tool."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tcping")
except PackageNotFoundError:  # running from source, not installed
    __version__ = "dev"
