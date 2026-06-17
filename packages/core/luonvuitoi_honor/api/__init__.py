"""API handlers: pure functions the Flask/serverless layer calls.

Read paths (listing / search / stats) live in :mod:`luonvuitoi_honor.honorroll`;
this module owns the *write* surface (admin add / delete) plus request-shaping
helpers so the Flask routes stay thin.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from luonvuitoi_honor.config import HonorConfig
from luonvuitoi_honor.storage import init_db


class ApiError(Exception):
    """Raised for malformed/invalid API input (→ HTTP 400)."""


@dataclass(frozen=True, slots=True)
class CreatedAchievement:
    id: int
    competition_id: str
    year: int
    name: str


def _str(v: Any) -> str:
    return "" if v is None else str(v).strip()


def add_achievement(
    config: HonorConfig,
    db_path: str | Path,
    *,
    payload: dict[str, Any],
) -> CreatedAchievement:
    """Validate + insert one achievement from a JSON payload.

    ``competition_id`` must be declared and ``medal`` must be in the global
    medal registry; everything else is coerced to text. Year defaults to the
    latest edition of the chosen competition.
    """
    competition_id = _str(payload.get("competition_id"))
    if not competition_id:
        raise ApiError("competition_id is required")
    if not any(c.id == competition_id for c in config.competitions):
        raise ApiError(f"unknown competition_id {competition_id!r}")
    medal = _str(payload.get("medal")).upper()
    if medal not in config.medals:
        raise ApiError(f"unknown medal {medal!r}; known: {sorted(config.medals)}")
    name = _str(payload.get("name"))
    if not name:
        raise ApiError("name is required")

    year_raw = payload.get("year")
    if year_raw is None or year_raw == "":
        years = [e.year for e in config.editions if e.competition_id == competition_id]
        year = max(years) if years else 0
    else:
        try:
            year = int(year_raw)
        except (TypeError, ValueError) as e:
            raise ApiError("year must be an integer") from e

    rec = {
        "competition_id": competition_id,
        "year": year,
        "candidate_no": _str(payload.get("candidate_no")) or "-",
        "name": name,
        "grade": _str(payload.get("grade")),
        "photo_url": _str(payload.get("photo_url")),
        "school": _str(payload.get("school")),
        "subject_code": _str(payload.get("subject_code")).upper(),
        "medal": medal,
        "rank": _str(payload.get("rank")),
        "percentile": _str(payload.get("percentile")),
    }
    db_path = Path(db_path).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(db_path))
    sql = (
        "INSERT INTO achievements "
        "(competition_id, year, candidate_no, name, grade, photo_url, school, subject_code, medal, rank, percentile) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        cur = conn.execute(sql, tuple(rec.values()))
        new_id = int(cur.lastrowid or 0)
    return CreatedAchievement(id=new_id, competition_id=competition_id, year=year, name=name)


def delete_achievement(db_path: str | Path, *, achievement_id: int) -> bool:
    """Delete one achievement by id; return whether a row was removed."""
    p = Path(db_path).expanduser().resolve()
    if not p.exists():
        return False
    with closing(sqlite3.connect(str(p))) as conn, conn:
        cur = conn.execute("DELETE FROM achievements WHERE id = ?", (int(achievement_id),))
        return bool(cur.rowcount)


__all__ = ["ApiError", "CreatedAchievement", "add_achievement", "delete_achievement"]
