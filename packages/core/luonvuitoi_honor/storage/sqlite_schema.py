"""SQLite schema for the honor-roll store.

A single flat ``achievements`` table holds one row per award. This is the
natural unit for an honor roll: a student with three medals produces three
rows, and every public listing is a single indexed SELECT (filter by
competition / year / medal / subject / school) instead of a fan-out across
per-edition tables.

All data columns are TEXT. SQLite is dynamically typed and source values can
be mixed numeric/string without penalty. Handlers cast when needed.
"""

from __future__ import annotations

from dataclasses import dataclass

SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS achievements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competition_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  candidate_no TEXT NOT NULL,
  name TEXT NOT NULL,
  grade TEXT,
  photo_url TEXT,
  school TEXT,
  subject_code TEXT,
  medal TEXT,
  rank TEXT,
  percentile TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ach_filter
  ON achievements (competition_id, year, medal, subject_code);

CREATE INDEX IF NOT EXISTS idx_ach_name
  ON achievements (name);

CREATE INDEX IF NOT EXISTS idx_ach_candidate
  ON achievements (candidate_no);

CREATE TABLE IF NOT EXISTS teams (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  competition_id TEXT NOT NULL,
  year INTEGER NOT NULL,
  name TEXT NOT NULL,
  award TEXT NOT NULL,
  subject TEXT,
  category TEXT,
  members TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_teams_filter
  ON teams (competition_id, year, award);
"""


@dataclass(frozen=True, slots=True)
class AchievementRow:
    """One achievement record, in storage order."""

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


def init_db(db_path: str) -> None:
    """Create the achievements table + indexes if they don't yet exist.

    Idempotent: safe to call on every boot and every ingest.
    """
    import sqlite3
    from contextlib import closing
    from pathlib import Path

    p = Path(db_path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(str(p))) as conn, conn:
        conn.executescript(SCHEMA_SQL)
