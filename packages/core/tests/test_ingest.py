"""Tests for the ingest layer: readers + projection orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from luonvuitoi_honor.ingest import (
    IngestError,
    ingest_rows,
    read_csv,
    read_json,
    replace_edition,
)


def _rows() -> list[dict]:
    return [
        {"name": "Alice", "school": "S", "subject": "MATH", "medal": "Gold", "rank": "1"},
        {"name": "Bob", "school": "S", "subject": "ENGLISH", "medal": "SILVER", "rank": "5"},
        {"name": "Carol", "medal": "bronze", "rank": "9"},  # medal lowercased → BRONZE
    ]


def test_ingest_inserts_and_normalises_medal(honor_config, db_path):  # type: ignore[no-untyped-def]
    result = ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=_rows())
    assert result.rows_inserted == 3
    assert result.rows_skipped == 0
    # lowercased 'bronze' → stored as 'BRONZE'
    from luonvuitoi_honor.honorroll import search_student

    carol = [a for a in search_student(db_path, name_query="Carol") if a.name == "Carol"]
    assert len(carol) == 1 and carol[0].medal == "BRONZE"


def test_ingest_skips_rows_without_name_or_medal(honor_config, db_path):  # type: ignore[no-untyped-def]
    rows = [
        {"name": "", "medal": "GOLD"},  # no name
        {"name": "X", "medal": ""},  # no medal
        {"name": "Valid", "medal": "GOLD"},
    ]
    result = ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=rows)
    assert result.rows_inserted == 1
    assert result.rows_skipped == 2
    assert len(result.warnings) == 2


def test_ingest_unknown_competition_raises(honor_config, db_path):  # type: ignore[no-untyped-def]
    with pytest.raises(IngestError, match="not declared"):
        ingest_rows(honor_config, db_path, competition_id="ghost", year=2025, rows=_rows())


def test_ingest_unknown_medal_is_skipped(honor_config, db_path):  # type: ignore[no-untyped-def]
    rows = [{"name": "X", "medal": "PLATINUM"}]  # not in registry
    result = ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=rows)
    assert result.rows_inserted == 0
    assert result.rows_skipped == 1


def test_replace_edition_is_idempotent(honor_config, db_path):  # type: ignore[no-untyped-def]
    ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=_rows())
    n = replace_edition(db_path, competition_id="demo-a", year=2025)
    assert n == 3
    # second replace finds nothing
    assert replace_edition(db_path, competition_id="demo-a", year=2025) == 0
    # re-ingest works after wipe
    r = ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=_rows())
    assert r.rows_inserted == 3


def test_replace_edition_missing_db_returns_zero(tmp_path: Path) -> None:
    assert replace_edition(tmp_path / "ghost.db", competition_id="x", year=2020) == 0


def test_ingest_teams_validates_award(honor_config, db_path):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor.ingest import ingest_teams

    teams = [
        {"name": "Team A", "award": "CHAMPION", "members": [{"name": "X", "grade": "5"}]},
        {"name": "Team B", "award": "PLATINUM"},  # unknown award -> skipped
        {"name": "", "award": "BEST"},  # missing name -> skipped
    ]
    r = ingest_teams(honor_config, db_path, competition_id="demo-a", year=2025, teams=teams)
    assert r.rows_inserted == 1
    assert r.rows_skipped == 2


def test_read_csv_skips_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,medal\nAlice,GOLD\n\nBob,SILVER\n", encoding="utf-8")
    rows = read_csv(p)
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"


def test_read_csv_missing_file(tmp_path: Path) -> None:
    with pytest.raises(IngestError, match="not found"):
        read_csv(tmp_path / "nope.csv")


def test_read_csv_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "e.csv"
    p.write_text("", encoding="utf-8")
    with pytest.raises(IngestError, match="empty"):
        read_csv(p)


def test_read_json_list_of_objects(tmp_path: Path) -> None:
    p = tmp_path / "d.json"
    p.write_text(json.dumps([{"name": "A", "medal": "GOLD"}]), encoding="utf-8")
    rows = read_json(p)
    assert rows[0]["name"] == "A"


def test_read_json_year_keyed_dict(tmp_path: Path) -> None:
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"2025": [{"name": "A", "medal": "GOLD"}]}), encoding="utf-8")
    rows = read_json(p)
    assert rows[0]["name"] == "A"
    assert rows[0]["year"] == "2025"


def test_read_json_invalid(tmp_path: Path) -> None:
    p = tmp_path / "d.json"
    p.write_text("{bad", encoding="utf-8")
    with pytest.raises(IngestError, match="invalid JSON"):
        read_json(p)


def test_read_json_wrong_shape(tmp_path: Path) -> None:
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"just": "a string"}), encoding="utf-8")
    with pytest.raises(IngestError, match="JSON must be"):
        read_json(p)
