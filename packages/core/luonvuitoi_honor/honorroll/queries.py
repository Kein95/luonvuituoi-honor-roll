"""Query engine: read achievements from SQLite with config-driven filtering.

All read paths used by the public honor roll, the student search, and the
admin list live here as pure functions that take a ``db_path`` + filters and
return dataclasses. Keeping them out of the Flask layer means the CLI, tests,
and a future serverless handler all share one implementation.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from luonvuitoi_honor.config import HonorConfig


@dataclass(frozen=True, slots=True)
class Achievement:
    id: int
    competition_id: str
    year: int
    candidate_no: str
    name: str
    grade: str
    photo_url: str
    school: str
    subject_code: str
    medal: str
    rank: str
    percentile: str


@dataclass(frozen=True, slots=True)
class MedalBreakdown:
    medal: str
    count: int


@dataclass(frozen=True, slots=True)
class SubjectBreakdown:
    subject_code: str
    count: int


@dataclass(slots=True)
class HonorRollPage:
    """A slice of the honor roll + the facets shown alongside it."""

    achievements: list[Achievement]
    total: int
    medal_breakdown: list[MedalBreakdown] = field(default_factory=list)
    subject_breakdown: list[SubjectBreakdown] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class TeamRecord:
    """One team/group award with its members (members decoded from the JSON column)."""

    id: int
    competition_id: str
    year: int
    name: str
    award: str
    subject: str
    category: str
    members: list[dict[str, str]]


_COLUMNS = "id, competition_id, year, candidate_no, name, grade, photo_url, school, subject_code, medal, rank, percentile"


def _row_to_achievement(r: sqlite3.Row) -> Achievement:
    return Achievement(
        id=int(r["id"]),
        competition_id=r["competition_id"],
        year=int(r["year"]),
        candidate_no=r["candidate_no"],
        name=r["name"],
        grade=r["grade"] or "",
        photo_url=r["photo_url"] or "",
        school=r["school"] or "",
        subject_code=r["subject_code"] or "",
        medal=r["medal"] or "",
        rank=r["rank"] or "",
        percentile=r["percentile"] or "",
    )


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(Path(db_path).expanduser().resolve()))
    conn.row_factory = sqlite3.Row
    return conn


def list_honor_roll(
    config: HonorConfig,
    db_path: str | Path,
    *,
    competition_id: str | None = None,
    year: int | None = None,
    medal: str | None = None,
    subject_code: str | None = None,
    school: str | None = None,
    name_query: str | None = None,
    limit: int = 2000,
    offset: int = 0,
) -> HonorRollPage:
    """Return a filtered, medal-ranked slice of the honor roll + facets.

    ``medal`` is normalised to uppercase; ``name_query`` / ``school`` do a
    case-insensitive substring match. Results are ordered by medal rank then
    numeric rank so the most prestigious awards surface first.
    """
    where: list[str] = []
    params: list[Any] = []
    if competition_id:
        where.append("competition_id = ?")
        params.append(competition_id)
    if year is not None:
        where.append("year = ?")
        params.append(int(year))
    if medal:
        where.append("medal = ?")
        params.append(medal.strip().upper())
    if subject_code:
        where.append("UPPER(subject_code) = ?")
        params.append(subject_code.strip().upper())
    if school:
        where.append("LOWER(school) LIKE ?")
        params.append(f"%{school.strip().lower()}%")
    if name_query:
        where.append("LOWER(name) LIKE ?")
        params.append(f"%{name_query.strip().lower()}%")
    clause = (" WHERE " + " AND ".join(where)) if where else ""

    order_map = {code: i for i, code in enumerate(sorted(config.medals, key=lambda c: config.medals[c].rank))}
    medal_cases = " ".join(f"WHEN '{m}' THEN {i}" for m, i in order_map.items())
    medal_order = f"CASE medal {medal_cases} ELSE 999 END" if order_map else "999"

    with closing(_connect(db_path)) as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM achievements{clause}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT {_COLUMNS} FROM achievements{clause} "
            f"ORDER BY {medal_order}, CAST(NULLIF(rank,'') AS INTEGER), name "
            f"LIMIT ? OFFSET ?",
            [*params, int(limit), int(offset)],
        ).fetchall()
        medals = [
            MedalBreakdown(medal=r["medal"], count=int(r["c"]))
            for r in conn.execute(
                f"SELECT medal, COUNT(*) c FROM achievements{clause} GROUP BY medal ORDER BY COUNT(*) DESC",
                params,
            )
        ]
        subjects = [
            SubjectBreakdown(subject_code=r["subject_code"] or "", count=int(r["c"]))
            for r in conn.execute(
                f"SELECT COALESCE(NULLIF(subject_code,''), '-') subject_code, COUNT(*) c "
                f"FROM achievements{clause} GROUP BY subject_code ORDER BY COUNT(*) DESC",
                params,
            )
        ]
    return HonorRollPage(
        achievements=[_row_to_achievement(r) for r in rows],
        total=int(total),
        medal_breakdown=medals,
        subject_breakdown=subjects,
    )


def search_student(
    db_path: str | Path,
    *,
    name_query: str,
    limit: int = 50,
) -> list[Achievement]:
    """Case-insensitive name search across all editions. This is the portal lookup."""
    q = f"%{name_query.strip().lower()}%"
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            f"SELECT {_COLUMNS} FROM achievements WHERE LOWER(name) LIKE ? ORDER BY year DESC, name LIMIT ?",
            (q, int(limit)),
        ).fetchall()
    return [_row_to_achievement(r) for r in rows]


def stats(config: HonorConfig, db_path: str | Path) -> dict[str, Any]:
    """Aggregate counts for the dashboard: totals, medals, subjects, schools."""
    with closing(_connect(db_path)) as conn:
        total = conn.execute("SELECT COUNT(*) FROM achievements").fetchone()[0]
        students = conn.execute("SELECT COUNT(DISTINCT name) FROM achievements").fetchone()[0]
        schools = conn.execute(
            "SELECT COUNT(DISTINCT school) FROM achievements WHERE school != ''"
        ).fetchone()[0]
        medals = {
            r["medal"]: int(r["c"])
            for r in conn.execute("SELECT medal, COUNT(*) c FROM achievements GROUP BY medal")
        }
        by_edition = [
            {"competition_id": r["competition_id"], "year": int(r["year"]), "count": int(r["c"])}
            for r in conn.execute(
                "SELECT competition_id, year, COUNT(*) c FROM achievements "
                "GROUP BY competition_id, year ORDER BY year DESC, competition_id"
            )
        ]
        top_schools = [
            {"school": r["school"], "count": int(r["c"])}
            for r in conn.execute(
                "SELECT school, COUNT(*) c FROM achievements WHERE school != '' "
                "GROUP BY school ORDER BY COUNT(*) DESC LIMIT 10"
            )
        ]
    _ = config  # signature kept symmetric for future per-competition scoping
    return {
        "total_achievements": int(total),
        "total_students": int(students),
        "total_schools": int(schools),
        "medals": medals,
        "editions": by_edition,
        "top_schools": top_schools,
    }


def list_schools(db_path: str | Path) -> list[str]:
    """Distinct, non-empty school names (alphabetical). Populates the roll's school filter."""
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT DISTINCT school FROM achievements WHERE school != '' ORDER BY school"
        ).fetchall()
    return [r["school"] for r in rows]


def hall_of_fame(config: HonorConfig, db_path: str | Path, *, limit: int = 60) -> list[dict[str, Any]]:
    """All-time top achievers across every edition.

    Aggregates by student name: total awards + their most prestigious medal
    (lowest configured rank). Sorted by best medal, then award count, then name.
    Returns plain dicts (an aggregate, not a single-row :class:`Achievement`).
    """
    medal_rank = {code: m.rank for code, m in config.medals.items()}
    by_name: dict[str, dict[str, Any]] = {}
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT name, grade, photo_url, school, medal FROM achievements WHERE name != ''"
        ).fetchall()
    for r in rows:
        name = r["name"]
        star = by_name.setdefault(
            name,
            {
                "name": name,
                "grade": "",
                "photo_url": "",
                "school": "",
                "count": 0,
                "best_rank": 1_000_000,
                "best_medal": "",
            },
        )
        star["count"] += 1
        if not star["grade"] and (r["grade"] or ""):
            star["grade"] = r["grade"]
        if not star["photo_url"] and (r["photo_url"] or ""):
            star["photo_url"] = r["photo_url"]
        if not star["school"] and (r["school"] or ""):
            star["school"] = r["school"]
        rank = medal_rank.get((r["medal"] or "").upper(), 1_000_000)
        if rank < star["best_rank"]:
            star["best_rank"] = rank
            star["best_medal"] = (r["medal"] or "").upper()
    ordered = sorted(by_name.values(), key=lambda s: (s["best_rank"], -s["count"], s["name"]))
    return ordered[:limit]


def list_all_for_admin(
    db_path: str | Path,
    *,
    competition_id: str | None = None,
    year: int | None = None,
    limit: int = 500,
    offset: int = 0,
) -> tuple[list[Achievement], int]:
    """Unranked listing for the admin table (newest first)."""
    where: list[str] = []
    params: list[Any] = []
    if competition_id:
        where.append("competition_id = ?")
        params.append(competition_id)
    if year is not None:
        where.append("year = ?")
        params.append(int(year))
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    with closing(_connect(db_path)) as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM achievements{clause}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT {_COLUMNS} FROM achievements{clause} ORDER BY id DESC LIMIT ? OFFSET ?",
            [*params, int(limit), int(offset)],
        ).fetchall()
    return [_row_to_achievement(r) for r in rows], int(total)


def list_teams(
    config: HonorConfig,
    db_path: str | Path,
    *,
    competition_id: str | None = None,
    year: int | None = None,
) -> list[TeamRecord]:
    """Team/group awards ordered by award prestige then name. Empty if no teams table yet."""
    order_map = {code: a.rank for code, a in config.team_awards.items()}
    where: list[str] = []
    params: list[Any] = []
    if competition_id:
        where.append("competition_id = ?")
        params.append(competition_id)
    if year is not None:
        where.append("year = ?")
        params.append(int(year))
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    with closing(_connect(db_path)) as conn:
        try:
            rows = conn.execute(
                f"SELECT id, competition_id, year, name, award, subject, category, members "
                f"FROM teams{clause} ORDER BY year DESC, name",
                params,
            ).fetchall()
        except sqlite3.OperationalError:
            return []  # teams table not created on this DB yet
    out: list[TeamRecord] = []
    for r in rows:
        try:
            members = json.loads(r["members"]) if r["members"] else []
        except (ValueError, TypeError):
            members = []
        if not isinstance(members, list):
            members = []
        out.append(
            TeamRecord(
                id=int(r["id"]),
                competition_id=r["competition_id"],
                year=int(r["year"]),
                name=r["name"],
                award=(r["award"] or "").upper(),
                subject=r["subject"] or "",
                category=r["category"] or "",
                members=members,
            )
        )
    out.sort(key=lambda t: (order_map.get(t.award, 1_000_000), t.name))
    return out
