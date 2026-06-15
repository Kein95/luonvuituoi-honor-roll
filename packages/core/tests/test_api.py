"""Tests for the admin write API (add / delete achievements)."""

from __future__ import annotations

import pytest
from luonvuitoi_honor import api


def test_add_achievement_inserts(honor_config, db_path):  # type: ignore[no-untyped-def]
    created = api.add_achievement(
        honor_config,
        db_path,
        payload={"competition_id": "demo-a", "year": 2025, "name": "New Kid", "medal": "GOLD"},
    )
    assert created.id > 0
    from luonvuitoi_honor.honorroll import search_student

    assert any(a.name == "New Kid" for a in search_student(db_path, name_query="New"))


def test_add_requires_competition(honor_config, db_path):  # type: ignore[no-untyped-def]
    with pytest.raises(api.ApiError, match="competition_id is required"):
        api.add_achievement(honor_config, db_path, payload={"name": "X", "medal": "GOLD"})


def test_add_rejects_unknown_competition(honor_config, db_path):  # type: ignore[no-untyped-def]
    with pytest.raises(api.ApiError, match="unknown competition"):
        api.add_achievement(
            honor_config, db_path, payload={"competition_id": "ghost", "name": "X", "medal": "GOLD"}
        )


def test_add_rejects_unknown_medal(honor_config, db_path):  # type: ignore[no-untyped-def]
    with pytest.raises(api.ApiError, match="unknown medal"):
        api.add_achievement(
            honor_config,
            db_path,
            payload={"competition_id": "demo-a", "name": "X", "medal": "PLATINUM"},
        )


def test_add_requires_name(honor_config, db_path):  # type: ignore[no-untyped-def]
    with pytest.raises(api.ApiError, match="name is required"):
        api.add_achievement(honor_config, db_path, payload={"competition_id": "demo-a", "medal": "GOLD"})


def test_add_defaults_year_to_latest_edition(honor_config, db_path):  # type: ignore[no-untyped-def]
    created = api.add_achievement(
        honor_config,
        db_path,
        payload={"competition_id": "demo-a", "name": "X", "medal": "GOLD"},
    )
    assert created.year == 2025  # only edition for demo-a


def test_add_uppercases_medal_and_subject(honor_config, db_path):  # type: ignore[no-untyped-def]
    api.add_achievement(
        honor_config,
        db_path,
        payload={
            "competition_id": "demo-a",
            "name": "Y",
            "medal": "gold",
            "subject_code": "math",
        },
    )
    from luonvuitoi_honor.honorroll import search_student

    a = search_student(db_path, name_query="Y")[0]
    assert a.medal == "GOLD"
    assert a.subject_code == "MATH"


def test_add_stores_grade(honor_config, db_path):  # type: ignore[no-untyped-def]
    api.add_achievement(
        honor_config,
        db_path,
        payload={"competition_id": "demo-a", "name": "Graded Kid", "medal": "GOLD", "grade": "Grade 9"},
    )
    from luonvuitoi_honor.honorroll import search_student

    a = search_student(db_path, name_query="Graded")[0]
    assert a.grade == "Grade 9"


def test_add_stores_photo(honor_config, db_path):  # type: ignore[no-untyped-def]
    api.add_achievement(
        honor_config,
        db_path,
        payload={
            "competition_id": "demo-a",
            "name": "Photo Kid",
            "medal": "GOLD",
            "photo_url": "https://example.test/p.jpg",
        },
    )
    from luonvuitoi_honor.honorroll import search_student

    a = search_student(db_path, name_query="Photo")[0]
    assert a.photo_url == "https://example.test/p.jpg"


def test_delete_existing(populated_db):  # type: ignore[no-untyped-def]
    assert api.delete_achievement(populated_db, achievement_id=1) is True


def test_delete_missing_returns_false(populated_db):  # type: ignore[no-untyped-def]
    assert api.delete_achievement(populated_db, achievement_id=999999) is False


def test_delete_missing_db_returns_false(tmp_path):  # type: ignore[no-untyped-def]
    assert api.delete_achievement(tmp_path / "ghost.db", achievement_id=1) is False
