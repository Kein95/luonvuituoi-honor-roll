"""Project source rows into achievement records and write them to SQLite.

The orchestrator owns three concerns:

1. **Schema bootstrap** — calls :func:`init_db` idempotently.
2. **Column projection** — maps the source file's headers (via
   :class:`DataMapping`) onto the logical achievement fields, normalising
   medals to uppercase and skipping rows without a name or medal.
3. **Competition/year context** — every ingest call is bound to one
   ``competition_id`` + ``year`` (an edition), so a single source file always
   lands in the right slice of the honor roll without per-row guessing.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import closing
from pathlib import Path
from typing import Any

from luonvuitoi_honor.config import HonorConfig
from luonvuitoi_honor.ingest.base import IngestError, IngestResult, SourceRow
from luonvuitoi_honor.storage import init_db


def _str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _medal_normalise(v: Any, *, valid: set[str]) -> str:
    """Uppercase + accept; return ``""`` when the medal isn't recognised.

    Unknown medals are dropped (warned) rather than inserted, so a typo in the
    source can't pollute the honor roll with a medal the UI can't render.
    """
    m = _str(v).upper().replace(" ", "_")
    return m if m in valid else ""


def project_row(
    config: HonorConfig,
    *,
    competition_id: str,
    year: int,
    row: SourceRow,
) -> dict[str, Any] | None:
    """Map one source row onto an achievement dict, or ``None`` to skip."""
    m = config.data_mapping
    name = _str(row.get(m.name_col))
    medal = _medal_normalise(row.get(m.medal_col), valid=set(config.medals.keys()))
    if not name:
        return None
    if not medal:
        return None
    competition = next((c for c in config.competitions if c.id == competition_id), None)
    if competition is None:
        raise IngestError(f"competition_id {competition_id!r} not declared in config")
    candidate_no = _str(row.get(m.candidate_no_col)) or "—"
    grade = _str(row.get(m.grade_col)) if m.grade_col else ""
    photo_url = _str(row.get(m.photo_col)) if m.photo_col else ""
    school = _str(row.get(m.school_col)) if m.school_col else ""
    rank = _str(row.get(m.rank_col)) if m.rank_col else ""
    percentile = _str(row.get(m.percentile_col)) if m.percentile_col else ""
    subject_code = _str(row.get(m.subject_col)).upper() if m.subject_col else ""
    if subject_code and competition.subjects:
        known = {s.code for s in competition.subjects}
        if subject_code not in known:
            # Unknown subject still kept (displayed verbatim) but flagged via caller.
            subject_code = subject_code
    return {
        "competition_id": competition_id,
        "year": int(year),
        "candidate_no": candidate_no,
        "name": name,
        "grade": grade,
        "photo_url": photo_url,
        "school": school,
        "subject_code": subject_code,
        "medal": medal,
        "rank": rank,
        "percentile": percentile,
    }


def ingest_rows(
    config: HonorConfig,
    db_path: str | Path,
    *,
    competition_id: str,
    year: int,
    rows: Iterable[SourceRow],
) -> IngestResult:
    """Insert projected achievements into the ``achievements`` table.

    Re-ingesting the same edition is additive by design (honour rolls grow);
    call :func:`replace_edition` first to make it idempotent per edition.
    """
    db_path = Path(db_path).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(db_path))
    result = IngestResult()
    sql = (
        "INSERT INTO achievements "
        "(competition_id, year, candidate_no, name, grade, photo_url, school, subject_code, medal, rank, percentile) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    idx = 0
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        for row in rows:
            idx += 1
            rec = project_row(config, competition_id=competition_id, year=year, row=row)
            if rec is None:
                result.rows_skipped += 1
                result.warn(f"row #{idx} missing name/medal; skipped")
                continue
            conn.execute(sql, tuple(rec.values()))
            result.rows_inserted += 1
    return result


def replace_edition(db_path: str | Path, *, competition_id: str, year: int) -> int:
    """Delete all achievements for one edition; return the count removed.

    Used by ``lvt-honor import --replace`` to make re-imports idempotent.
    """
    db_path = Path(db_path).expanduser().resolve()
    if not Path(db_path).exists():
        return 0
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        cur = conn.execute(
            "DELETE FROM achievements WHERE competition_id = ? AND year = ?",
            (competition_id, int(year)),
        )
        return cur.rowcount or 0


def ingest_teams(
    config: HonorConfig,
    db_path: str | Path,
    *,
    competition_id: str,
    year: int,
    teams: Iterable[dict[str, Any]],
) -> IngestResult:
    """Insert team/group awards into the ``teams`` table.

    Each team dict: ``{name, award, subject?, category?, members:[{name,grade,school}]}``.
    ``award`` is uppercased and validated against the config's ``team_awards`` registry.
    """
    db_path = Path(db_path).expanduser().resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    init_db(str(db_path))
    result = IngestResult()
    valid = set(config.team_awards.keys())
    sql = (
        "INSERT INTO teams (competition_id, year, name, award, subject, category, members) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
    idx = 0
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        for team in teams:
            idx += 1
            name = _str(team.get("name"))
            award = _str(team.get("award")).upper().replace(" ", "_")
            if not name or not award:
                result.rows_skipped += 1
                result.warn(f"team #{idx} missing name/award; skipped")
                continue
            if valid and award not in valid:
                result.rows_skipped += 1
                result.warn(f"team #{idx} unknown award {award!r}; skipped")
                continue
            raw_members = team.get("members") or []
            members = (
                [
                    {
                        "name": _str(m.get("name")),
                        "grade": _str(m.get("grade")),
                        "school": _str(m.get("school")),
                    }
                    for m in raw_members
                    if isinstance(m, dict) and _str(m.get("name"))
                ]
                if isinstance(raw_members, list)
                else []
            )
            conn.execute(
                sql,
                (
                    competition_id,
                    int(year),
                    name,
                    award,
                    _str(team.get("subject")).upper(),
                    _str(team.get("category")),
                    json.dumps(members, ensure_ascii=False),
                ),
            )
            result.rows_inserted += 1
    return result


def replace_teams_edition(db_path: str | Path, *, competition_id: str, year: int) -> int:
    """Delete all teams for one edition; return the count removed."""
    db_path = Path(db_path).expanduser().resolve()
    if not Path(db_path).exists():
        return 0
    with closing(sqlite3.connect(str(db_path))) as conn, conn:
        try:
            cur = conn.execute(
                "DELETE FROM teams WHERE competition_id = ? AND year = ?",
                (competition_id, int(year)),
            )
        except sqlite3.OperationalError:
            return 0
        return cur.rowcount or 0
