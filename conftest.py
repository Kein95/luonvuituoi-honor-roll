"""Root conftest: put both source packages on sys.path so the test suite runs
from a checkout without requiring ``pip install -e``.

This mirrors how the sibling LUONVUITUOI-CERT tests are structured and keeps
CI's ``pip install -e`` path identical for both projects.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
for _pkg in (_ROOT / "packages" / "core", _ROOT / "packages" / "cli"):
    _src = str(_pkg)
    if _src not in sys.path:
        sys.path.insert(0, _src)
