"""Run the full test suite from a source checkout (no pip install needed).

Usage::

    python scripts/run_tests.py

Writes a summary to stdout and the full report to ``scripts/_test_output.txt``.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for _pkg in (_ROOT / "packages" / "core", _ROOT / "packages" / "cli"):
    if str(_pkg) not in sys.path:
        sys.path.insert(0, str(_pkg))


def main() -> int:
    import pytest

    args = [
        str(_ROOT / "packages" / "core" / "tests"),
        str(_ROOT / "packages" / "cli" / "tests"),
        "-ra",
        "--tb=short",
        "-q",
        "-p",
        "no:cacheprovider",
        "--rootdir",
        str(_ROOT),
    ]
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        code = pytest.main(args)
    output = buf.getvalue()
    (Path(__file__).parent / "_test_output.txt").write_text(output, encoding="utf-8")
    # Print just the summary lines so the console isn't flooded.
    for line in output.splitlines()[-40:]:
        print(line)
    print(f"\n[exit code {code}] full report: scripts/_test_output.txt")
    return int(code)


if __name__ == "__main__":
    raise SystemExit(main())
