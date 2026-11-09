"""Shortcut to run tcping from a clone: `uv run main.py <host> <port>`."""

import sys
from pathlib import Path

# Makes sure src/ is on the path even without the package installed.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tcping.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
