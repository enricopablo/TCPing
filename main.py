"""Atalho para rodar o tcping a partir do clone: `uv run main.py <host> <porta>`."""

import sys
from pathlib import Path

# Garante que src/ esteja no path mesmo sem o pacote instalado.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tcping.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
