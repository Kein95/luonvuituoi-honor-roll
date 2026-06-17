"""End-to-end tests that exercise the full Flask surface via the test client.

Marked ``e2e`` so they can be skipped with ``pytest -m 'not e2e'`` for the fast
unit-only loop. They build the real app factory, hit every route, and assert
on status codes + visible content, catching wiring regressions the pure unit
tests can't see.
"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.e2e


def test_health_endpoint(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_honor_roll_page_renders(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/")
    assert r.status_code == 200
    assert b"Alice Gold" in r.data
    assert b"Test Roll" in r.data  # project name in header


def test_honor_roll_filters_by_medal(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/?medal=GOLD")
    assert r.status_code == 200
    assert b"Alice Gold" in r.data
    assert b"Bob Silver" not in r.data


def test_search_page_empty(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/search")
    assert r.status_code == 200
    assert b"Find a student" in r.data


def test_search_page_with_query(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/search?q=Gold")
    assert r.status_code == 200
    assert b"Alice Gold" in r.data
    assert b"Eve Gold" in r.data


def test_admin_page_renders(admin_client):  # type: ignore[no-untyped-def]
    r = admin_client.get("/admin")
    assert r.status_code == 200
    assert b"Alice Gold" in r.data


def test_admin_requires_login(app_client):  # type: ignore[no-untyped-def]
    # Unauthenticated admin page redirects to /login...
    r = app_client.get("/admin")
    assert r.status_code in (301, 302, 303, 307, 308)
    assert "/login" in r.headers.get("Location", "")
    # ...and the write API rejects with 401.
    add = app_client.post(
        "/api/admin/achievements",
        data=json.dumps({"competition_id": "demo-a", "name": "Sneaky", "medal": "GOLD"}),
        content_type="application/json",
    )
    assert add.status_code == 401
    assert app_client.delete("/api/admin/achievements/1").status_code == 401


def test_login_flow(app_client):  # type: ignore[no-untyped-def]
    app_client.get("/login")  # mint a CSRF token for the form
    with app_client.session_transaction() as sess:
        token = sess.get("csrf_token")
    assert app_client.post("/login", data={"password": "nope", "csrf_token": token}).status_code == 401
    ok = app_client.post("/login", data={"password": "test-secret", "csrf_token": token})
    assert ok.status_code in (302, 303)
    assert app_client.get("/admin").status_code == 200
    app_client.get("/logout")
    assert app_client.get("/admin").status_code in (301, 302, 303, 307, 308)


def test_login_rejects_missing_csrf(app_client):  # type: ignore[no-untyped-def]
    # A correct password with no CSRF token is refused (400), not logged in.
    r = app_client.post("/login", data={"password": "test-secret"})
    assert r.status_code == 400
    assert app_client.get("/admin").status_code in (301, 302, 303, 307, 308)


def test_login_lockout_after_repeated_failures(app_client):  # type: ignore[no-untyped-def]
    app_client.get("/login")
    with app_client.session_transaction() as sess:
        token = sess.get("csrf_token")
    # default ADMIN_LOGIN_MAX_ATTEMPTS=5 → the 6th attempt is locked out (429).
    for _ in range(5):
        assert app_client.post("/login", data={"password": "wrong", "csrf_token": token}).status_code == 401
    locked = app_client.post("/login", data={"password": "wrong", "csrf_token": token})
    assert locked.status_code == 429
    assert "Retry-After" in locked.headers
    # Even the *correct* password is locked out while the cooldown holds.
    assert app_client.post("/login", data={"password": "test-secret", "csrf_token": token}).status_code == 429


def test_admin_write_requires_csrf_header(admin_client):  # type: ignore[no-untyped-def]
    # Authenticated but no X-CSRF-Token header → 403.
    payload = {"competition_id": "demo-a", "name": "NoToken", "medal": "GOLD"}
    r = admin_client.post(
        "/api/admin/achievements", data=json.dumps(payload), content_type="application/json"
    )
    assert r.status_code == 403
    assert "CSRF" in r.get_json()["error"]
    assert admin_client.delete("/api/admin/achievements/1").status_code == 403


def test_admin_actions_are_audited(admin_client):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor_cli.server.security import recent_activity

    payload = {"competition_id": "demo-a", "year": 2025, "name": "Audited", "medal": "GOLD"}
    admin_client.post(
        "/api/admin/achievements",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": admin_client.csrf_token},
    )
    db = admin_client.application.config["HONOR_DB_PATH"]
    actions = {row["action"] for row in recent_activity(db, limit=50)}
    assert "login.success" in actions
    assert "admin.add" in actions


def test_hall_of_fame_page(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/hall-of-fame")
    assert r.status_code == 200
    assert b"Alice Gold" in r.data  # a top achiever surfaces in the hall


def test_teams_page(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/teams")
    assert r.status_code == 200
    assert b"All-Star Teams" in r.data  # title renders even with no teams yet


def test_api_stats(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/api/stats")
    assert r.status_code == 200
    body = r.get_json()
    assert body["total_achievements"] == 5
    assert body["total_students"] == 5


def test_api_search(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/api/search?q=Alice")
    assert r.status_code == 200
    body = r.get_json()
    assert body["query"] == "Alice"
    assert any(res["name"] == "Alice Gold" for res in body["results"])


def test_api_admin_add_achievement(admin_client):  # type: ignore[no-untyped-def]
    payload = {
        "competition_id": "demo-a",
        "year": 2025,
        "name": "Zoe New",
        "school": "School Z",
        "medal": "GOLD",
        "subject_code": "MATH",
    }
    r = admin_client.post(
        "/api/admin/achievements",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": admin_client.csrf_token},
    )
    assert r.status_code == 201
    created = r.get_json()
    assert created["name"] == "Zoe New"
    # now visible on the public roll
    r2 = admin_client.get("/?medal=GOLD")
    assert b"Zoe New" in r2.data


def test_api_admin_add_rejects_bad_payload(admin_client):  # type: ignore[no-untyped-def]
    r = admin_client.post(
        "/api/admin/achievements",
        data=json.dumps({"competition_id": "demo-a", "name": "X", "medal": "PLATINUM"}),
        content_type="application/json",
        headers={"X-CSRF-Token": admin_client.csrf_token},
    )
    assert r.status_code == 400
    assert "unknown medal" in r.get_json()["error"]


def test_api_admin_add_rejects_oversized_body(admin_client):  # type: ignore[no-untyped-def]
    big = {"name": "x" * 100_000, "competition_id": "demo-a", "medal": "GOLD"}
    r = admin_client.post(
        "/api/admin/achievements",
        data=json.dumps(big),
        content_type="application/json",
        headers={"X-CSRF-Token": admin_client.csrf_token},
    )
    # 32KB cap → rejected
    assert r.status_code in (400, 413)


def test_api_admin_delete_achievement(admin_client):  # type: ignore[no-untyped-def]
    r = admin_client.delete("/api/admin/achievements/1", headers={"X-CSRF-Token": admin_client.csrf_token})
    assert r.status_code == 200
    assert r.get_json()["deleted"] is True


def test_security_headers_present(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/")
    assert "Content-Security-Policy" in r.headers
    assert "nonce-" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_hsts_and_cors_from_env(honor_config, populated_db, tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor_cli.server import build_app

    monkeypatch.setenv("ADMIN_PASSWORD", "x")
    monkeypatch.setenv("SECRET_KEY", "y")
    monkeypatch.setenv("FORCE_HSTS", "1")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://ok.test")
    cfg = tmp_path / "honor.config.json"
    cfg.write_text(honor_config.model_dump_json(), encoding="utf-8")
    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data" / "test-roll.db").write_bytes(populated_db.read_bytes())
    client = build_app(cfg, tmp_path).test_client()

    assert "Strict-Transport-Security" in client.get("/").headers
    allowed = client.get("/api/stats", headers={"Origin": "https://ok.test"})
    assert allowed.headers.get("Access-Control-Allow-Origin") == "https://ok.test"
    denied = client.get("/api/stats", headers={"Origin": "https://evil.test"})
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_language_switch_sets_cookie(app_client):  # type: ignore[no-untyped-def]
    en = app_client.get("/").get_data(as_text=True)  # config default (en)
    assert "Demo board EN" in en and "Honor Roll" in en
    resp = app_client.get("/?lang=vi")
    vi = resp.get_data(as_text=True)
    assert "Bảng demo VN" in vi and "Bảng Vinh Danh" in vi  # tagline + nav both switch
    assert "lang=vi" in resp.headers.get("Set-Cookie", "")


def test_language_from_accept_header(app_client):  # type: ignore[no-untyped-def]
    r = app_client.get("/", headers={"Accept-Language": "vi-VN,vi;q=0.9,en;q=0.5"})
    assert "Bảng demo VN" in r.get_data(as_text=True)
