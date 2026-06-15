"""Apply ruff auto-fixes + format, from the project root.

Usage::

    python scripts/fix_lint.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    for cmd in (
        [sys.executable, "-m", "ruff", "check", "--fix", "packages", "scripts", "--config", "pyproject.toml"],
        [sys.executable, "-m", "ruff", "format", "packages", "scripts", "--config", "pyproject.toml"],
    ):
        r = subprocess.run(cmd, cwd=str(_ROOT))
        if r.returncode not in (0, 1):
            return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
