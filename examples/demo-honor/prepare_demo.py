"""Generate the demo honor-roll dataset (fully blind — anonymised placeholders).

Writes ``data/demo-2025.json`` with one row per award, columns matching the
config's ``data_mapping`` so ``lvt-honor import`` ingests it without remapping.
Students are anonymised to single-letter placeholders (X / Y / Z) and every
school is the literal "School" — no real names appear anywhere.

Run::

    python prepare_demo.py
    lvt-honor import data/demo-2025.json --competition demo-a --year 2025 --replace
    lvt-honor dev
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

_NAMES = ["X", "Y", "Z"]
_SCHOOL = "School"
_SUBJECTS = ["MATH", "ENGLISH", "SCIENCE"]
_MEDALS = ["GOLD", "SILVER", "BRONZE", "HONORABLE", "MERIT"]
_AVATAR_COLORS = {"X": "#667eea", "Y": "#764ba2", "Z": "#10b981"}


def _avatar(letter: str) -> str:
    """A blind, self-contained placeholder portrait: a coloured circle with the letter."""
    color = _AVATAR_COLORS.get(letter, "#888888")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">'
        f'<rect width="120" height="120" rx="60" fill="{color}"/>'
        '<text x="60" y="82" font-size="64" font-family="Arial,sans-serif" '
        f'fill="#ffffff" text-anchor="middle">{letter}</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


_TEAM_AWARDS = ["CHAMPION", "RUNNER_UP_1", "RUNNER_UP_2", "BEST"]


def build_teams() -> list[dict[str, object]]:
    """A few blind placeholder teams — one per award, members X/Y/Z."""
    out: list[dict[str, object]] = []
    for i, award in enumerate(_TEAM_AWARDS):
        out.append(
            {
                "name": "Team " + _NAMES[i % len(_NAMES)],
                "award": award,
                "subject": _SUBJECTS[i % len(_SUBJECTS)],
                "category": "Lower Secondary",
                "members": [
                    {"name": _NAMES[(i + j) % len(_NAMES)], "grade": _NAMES[(i + j) % len(_NAMES)], "school": _SCHOOL}
                    for j in range(3)
                ],
            }
        )
    return out


def build() -> list[dict[str, str]]:
    """One award per (student, medal) — each placeholder student wins each medal once."""
    out: list[dict[str, str]] = []
    i = 0
    for name in _NAMES:
        for k, medal in enumerate(_MEDALS):
            out.append(
                {
                    "name": name,
                    "grade": name,
                    "photo": _avatar(name),
                    "school": _SCHOOL,
                    "subject": _SUBJECTS[k % len(_SUBJECTS)],
                    "medal": medal,
                    "rank": str((i * 7) % 120 + 1),
                    "candidate_no": "—",
                }
            )
            i += 1
    return out


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate the blind demo honor-roll JSON.")
    parser.add_argument("--output", type=Path, default=Path("data/demo-2025.json"), help="Output JSON path.")
    parser.add_argument(
        "--teams-output", type=Path, default=Path("data/demo-teams-2025.json"), help="Teams JSON path."
    )
    args = parser.parse_args()

    rows = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    teams = build_teams()
    args.teams_output.parent.mkdir(parents=True, exist_ok=True)
    args.teams_output.write_text(json.dumps(teams, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   teams: {len(teams)} -> {args.teams_output}")

    medals: dict[str, int] = {}
    subjects: dict[str, int] = {}
    for r in rows:
        medals[r["medal"]] = medals.get(r["medal"], 0) + 1
        subjects[r["subject"]] = subjects.get(r["subject"], 0) + 1
    print(f"OK wrote {len(rows)} achievements -> {args.output}")
    print(f"   medals: {medals}")
    print(f"   subjects: {subjects}")
    print("   next: lvt-honor import data/demo-2025.json --competition demo-a --year 2025 --replace")


if __name__ == "__main__":
    main()
