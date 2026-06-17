"""Shared pytest fixtures for engine + CLI tests.

No external assets needed — the honor-roll domain is pure SQLite + JSON, so
every fixture builds its data in ``tmp_path``. This keeps the suite hermetic
and fast (no reportlab/pypdf/font files, unlike the CERT sibling).
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _valid_config_dict() -> dict:
    """Minimal valid config matching the demo's shape (single competition/edition)."""
    return {
        "project": {
            "name": "Test Roll",
            "slug": "test-roll",
            "locale": "en",
            "tagline": "Bảng demo VN",
            "tagline_en": "Demo board EN",
        },
        "competitions": [
            {
                "id": "demo-a",
                "name": "Demo Olympiad A",
                "subjects": [
                    {"code": "MATH", "name": "Mathematics"},
                    {"code": "ENGLISH", "name": "English"},
                ],
                "medals": ["GOLD", "SILVER", "BRONZE", "MERIT"],
            }
        ],
        "editions": [{"competition_id": "demo-a", "year": 2025, "label": "Demo Olympiad A 2025"}],
        "medals": {
            "GOLD": {"rank": 1, "label_en": "Gold", "label_vi": "Vàng", "color": "#FFD700", "icon": "🥇"},
            "SILVER": {"rank": 2, "label_en": "Silver", "label_vi": "Bạc", "color": "#C0C0C0", "icon": "🥈"},
            "BRONZE": {"rank": 3, "label_en": "Bronze", "label_vi": "Đồng", "color": "#CD7F32", "icon": "🥉"},
            "MERIT": {"rank": 4, "label_en": "Merit", "label_vi": "KK", "color": "#3b82f6", "icon": "📜"},
        },
        "team_awards": {
            "CHAMPION": {"rank": 1, "label_en": "Champion", "label_vi": "Vô địch"},
            "BEST": {"rank": 2, "label_en": "Best", "label_vi": "Tốt nhất"},
        },
    }


@pytest.fixture
def config_dict() -> dict:
    return _valid_config_dict()


@pytest.fixture
def honor_config(config_dict: dict):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor.config import HonorConfig

    return HonorConfig.model_validate(config_dict)


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """An empty SQLite path inside tmp_path; the schema is created on first ingest."""
    return tmp_path / "test.db"


@pytest.fixture
def sample_rows() -> list[dict]:
    """A handful of achievements covering every medal + both subjects."""
    return [
        {
            "name": "Alice Gold",
            "grade": "Grade 5",
            "school": "School A",
            "subject": "MATH",
            "medal": "GOLD",
            "rank": "1",
            "candidate_no": "C001",
        },
        {
            "name": "Bob Silver",
            "grade": "Grade 6",
            "school": "School B",
            "subject": "ENGLISH",
            "medal": "SILVER",
            "rank": "5",
            "candidate_no": "C002",
        },
        {
            "name": "Carol Bronze",
            "grade": "Grade 5",
            "school": "School A",
            "subject": "MATH",
            "medal": "BRONZE",
            "rank": "12",
            "candidate_no": "C003",
        },
        {
            "name": "Dave Merit",
            "grade": "Grade 7",
            "school": "School C",
            "subject": "ENGLISH",
            "medal": "MERIT",
            "rank": "40",
            "candidate_no": "C004",
        },
        {
            "name": "Eve Gold",
            "grade": "Grade 8",
            "school": "School B",
            "subject": "ENGLISH",
            "medal": "GOLD",
            "rank": "3",
            "candidate_no": "C005",
        },
    ]


@pytest.fixture
def populated_db(honor_config, db_path, sample_rows):  # type: ignore[no-untyped-def]
    """A DB pre-loaded with ``sample_rows`` under the demo-a/2025 edition."""
    from luonvuitoi_honor.ingest import ingest_rows

    ingest_rows(honor_config, db_path, competition_id="demo-a", year=2025, rows=sample_rows)
    return db_path


@pytest.fixture
def app_client(honor_config, populated_db, tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """A Flask test client bound to a tmp project root with the config written to disk."""
    from luonvuitoi_honor_cli.server import build_app

    monkeypatch.setenv("ADMIN_PASSWORD", "test-secret")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    cfg_file = tmp_path / "honor.config.json"
    import json

    cfg_file.write_text(json.dumps(_valid_config_dict()), encoding="utf-8")
    # Point the app's db_path at the populated db by symlinking via project layout:
    # build_app derives db_path = project_root / data / <slug>.db, so place it there.
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    target = data_dir / "test-roll.db"
    target.write_bytes(populated_db.read_bytes())
    app = build_app(cfg_file, tmp_path)
    app.testing = True
    return app.test_client()


@pytest.fixture
def admin_client(app_client):  # type: ignore[no-untyped-def]
    """An ``app_client`` already authenticated into the admin surface.

    Carries a fresh ``csrf_token`` attribute (login rotates the token, so this is
    the post-login one) for use in the ``X-CSRF-Token`` header on write calls.
    """
    app_client.get("/login")  # mint the CSRF token the login form needs
    with app_client.session_transaction() as sess:
        token = sess.get("csrf_token")
    resp = app_client.post("/login", data={"password": "test-secret", "csrf_token": token})
    assert resp.status_code in (302, 303)
    app_client.get("/admin")  # login rotated the token; mint a fresh one
    with app_client.session_transaction() as sess:
        app_client.csrf_token = sess.get("csrf_token")
    return app_client
