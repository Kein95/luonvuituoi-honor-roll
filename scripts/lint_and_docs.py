"""Run ruff lint + mkdocs build from the project root, capturing output to a file.

Usage::

    python scripts/lint_and_docs.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_REPORT = Path(__file__).parent / "_lint_output.txt"


def _run(title: str, cmd: list[str], cwd: Path) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = f"\n{'=' * 70}\n{title}\n{'=' * 70}\ncmd: {' '.join(cmd)}\ncwd: {cwd}\n\n{r.stdout}{r.stderr}"
    return r.returncode, out


def main() -> int:
    sections: list[str] = []
    code = 0

    rc, out = _run(
        "ruff check",
        [sys.executable, "-m", "ruff", "check", "packages", "scripts", "--config", "pyproject.toml"],
        _ROOT,
    )
    sections.append(out)
    code = code or rc

    rc, out = _run(
        "ruff format --check",
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            "packages",
            "scripts",
            "--config",
            "pyproject.toml",
        ],
        _ROOT,
    )
    sections.append(out)
    # format check is non-blocking for this pass (style only)

    rc, out = _run(
        "mkdocs build --strict",
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--clean", "--site-dir", "_site_test"],
        _ROOT,
    )
    sections.append(out)
    code = code or rc

    report = "\n".join(sections)
    _REPORT.write_text(report, encoding="utf-8")
    for line in report.splitlines():
        print(line)
    print(f"\n[exit code {code}] full report: scripts/_lint_output.txt")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
