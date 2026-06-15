"""Tests for the honorroll query engine (listing, search, stats, admin)."""

from __future__ import annotations

from luonvuitoi_honor.honorroll import (
    list_all_for_admin,
    list_honor_roll,
    list_schools,
    search_student,
    stats,
)


def test_list_orders_by_medal_rank(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, competition_id="demo-a", year=2025)
    medals = [a.medal for a in page.achievements]
    # GOLD(rank 1) < SILVER(rank 2) < BRONZE(rank 3) < MERIT(rank 4)
    assert medals[0] == "GOLD"
    assert medals[-1] == "MERIT"
    assert medals.index("GOLD") < medals.index("SILVER") < medals.index("BRONZE")


def test_list_total_matches_ingested(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, competition_id="demo-a", year=2025)
    assert page.total == 5
    assert len(page.achievements) == 5


def test_list_filter_by_medal(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, medal="GOLD")
    assert page.total == 2
    assert all(a.medal == "GOLD" for a in page.achievements)


def test_list_filter_medal_case_insensitive(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, medal="gold")
    assert page.total == 2


def test_list_filter_by_subject(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, subject_code="english")
    assert page.total == 3  # Bob SILVER, Dave MERIT, Eve GOLD


def test_list_filter_by_school(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, school="School A")
    assert page.total == 2  # Alice, Carol


def test_list_name_query_substring(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, name_query="alic")
    assert page.total == 1
    assert page.achievements[0].name == "Alice Gold"


def test_search_student_across_editions(populated_db):  # type: ignore[no-untyped-def]
    results = search_student(populated_db, name_query="Gold")
    # Alice Gold + Eve Gold
    assert len(results) == 2


def test_search_student_no_match(populated_db):  # type: ignore[no-untyped-def]
    assert search_student(populated_db, name_query="Zzz") == []


def test_stats_aggregates(populated_db, honor_config):  # type: ignore[no-untyped-def]
    s = stats(honor_config, populated_db)
    assert s["total_achievements"] == 5
    assert s["total_students"] == 5  # all distinct names
    assert s["medals"]["GOLD"] == 2
    assert s["medals"]["SILVER"] == 1
    assert any(e["competition_id"] == "demo-a" and e["year"] == 2025 for e in s["editions"])


def test_admin_listing_newest_first(populated_db):  # type: ignore[no-untyped-def]
    rows, total = list_all_for_admin(populated_db)
    assert total == 5
    ids = [r.id for r in rows]
    assert ids == sorted(ids, reverse=True)


def test_admin_listing_filter_by_competition(populated_db):  # type: ignore[no-untyped-def]
    rows, total = list_all_for_admin(populated_db, competition_id="demo-a")
    assert total == 5
    rows_ghost, total_ghost = list_all_for_admin(populated_db, competition_id="ghost")
    assert total_ghost == 0


def test_list_schools_distinct_sorted(populated_db):  # type: ignore[no-untyped-def]
    assert list_schools(populated_db) == ["School A", "School B", "School C"]


def test_list_honor_roll_filter_by_school(populated_db, honor_config):  # type: ignore[no-untyped-def]
    page = list_honor_roll(honor_config, populated_db, school="School A")
    assert page.total == 2  # Alice, Carol
    assert all(a.school == "School A" for a in page.achievements)


def test_list_teams_ordered_by_award_rank(honor_config, db_path):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor.honorroll import list_teams
    from luonvuitoi_honor.ingest import ingest_teams

    ingest_teams(
        honor_config,
        db_path,
        competition_id="demo-a",
        year=2025,
        teams=[
            {"name": "Team Best", "award": "BEST", "members": [{"name": "X"}]},
            {"name": "Team Champ", "award": "CHAMPION", "members": [{"name": "Y"}, {"name": "Z"}]},
        ],
    )
    teams = list_teams(honor_config, db_path)
    assert [t.name for t in teams] == ["Team Champ", "Team Best"]  # CHAMPION (rank 1) first
    assert len(teams[0].members) == 2


def test_list_teams_empty_when_no_table(honor_config, db_path):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor.honorroll import list_teams

    assert list_teams(honor_config, db_path) == []  # fresh path, no teams table yet
