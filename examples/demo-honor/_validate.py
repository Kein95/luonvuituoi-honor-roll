"""End-to-end smoke test for the demo-honor example.

Run from the example dir with PYTHONPATH pointing at both packages:
    python _validate.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CORE = REPO / "packages" / "core"
CLI = REPO / "packages" / "cli"
for p in (str(CORE), str(CLI)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("ADMIN_PASSWORD", "demo-pass")
os.environ.setdefault("SECRET_KEY", "demo-key")

from luonvuitoi_honor.config import load_config  # noqa: E402
from luonvuitoi_honor.honorroll import list_honor_roll, search_student, stats  # noqa: E402
from luonvuitoi_honor.ingest import (  # noqa: E402
    ingest_rows,
    ingest_teams,
    read_file,
    read_teams_file,
    replace_edition,
    replace_teams_edition,
)
from luonvuitoi_honor.locale import load_locale  # noqa: E402
from luonvuitoi_honor.ui import render_admin_page, render_honor_roll_page, render_search_page  # noqa: E402
from luonvuitoi_honor_cli.server import build_app  # noqa: E402

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "honor.config.json"
DB = ROOT / "data" / "demo-honor.db"
SOURCE = ROOT / "data" / "demo-2025.json"


def main() -> None:
    cfg = load_config(CFG)
    print(f"[1/7] config OK: {cfg.project.name} | "
          f"{len(cfg.competitions)} comps, {len(cfg.editions)} editions, {len(cfg.medals)} medals")

    locale = load_locale(cfg.project.locale)
    print(f"[2/7] locale OK: {cfg.project.locale} ({len(locale)} top-level keys)")

    rows = read_file(SOURCE)
    print(f"[3/7] source read: {len(rows)} rows from {SOURCE.name}")

    replace_edition(DB, competition_id="demo-a", year=2025)
    result = ingest_rows(cfg, DB, competition_id="demo-a", year=2025, rows=rows)
    print(f"[4/7] ingest OK: inserted={result.rows_inserted} skipped={result.rows_skipped} "
          f"warnings={len(result.warnings)}")

    replace_teams_edition(DB, competition_id="demo-a", year=2025)
    teams = read_teams_file(ROOT / "data" / "demo-teams-2025.json")
    tres = ingest_teams(cfg, DB, competition_id="demo-a", year=2025, teams=teams)
    print(f"       teams ingest: inserted={tres.rows_inserted}")

    page = list_honor_roll(cfg, DB, competition_id="demo-a", year=2025)
    print(f"[5/7] query OK: total={page.total}, "
          f"medals={[(m.medal, m.count) for m in page.medal_breakdown]}")

    s = stats(cfg, DB)
    print(f"       stats: achievements={s['total_achievements']} "
          f"students={s['total_students']} schools={s['total_schools']}")

    html = render_honor_roll_page(config=cfg, locale=locale, db_path=DB, csp_nonce="test123")
    assert "X" in html or "Gold" in html, "expected a known student in HTML"
    print(f"[6/7] render OK: honor-roll HTML = {len(html)} chars")

    # Search render
    html2 = render_search_page(config=cfg, locale=locale, db_path=DB, csp_nonce="t", name_query="X")
    found = search_student(DB, name_query="X")
    print(f"       search 'X' -> {len(found)} results, HTML = {len(html2)} chars")

    # Admin render
    html3 = render_admin_page(config=cfg, locale=locale, db_path=DB, csp_nonce="t")
    print(f"       admin HTML = {len(html3)} chars")

    # Flask test client
    app = build_app(CFG, ROOT)
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200, f"GET / -> {r.status_code}"
    assert b"LUONVUITUOI HONOR ROLL" in r.data, "project name missing from page"
    print(f"[7/7] Flask OK: GET / -> {r.status_code} ({len(r.data)} bytes)")

    r2 = client.get("/search?q=X")
    assert r2.status_code == 200
    print(f"       GET /search?q=X -> {r2.status_code}")

    client.post("/login", data={"password": "demo-pass"})
    r3 = client.get("/admin")
    assert r3.status_code == 200
    print(f"       GET /admin -> {r3.status_code}")

    assert client.get("/hall-of-fame").status_code == 200
    r_teams = client.get("/teams")
    assert r_teams.status_code == 200
    print(f"       GET /hall-of-fame & /teams -> 200 ({tres.rows_inserted} teams)")

    r4 = client.get("/api/stats")
    assert r4.status_code == 200
    print(f"       GET /api/stats -> {r4.status_code}: {r4.get_json()['total_achievements']} achievements")

    r5 = client.get("/health")
    assert r5.status_code == 200 and r5.get_json()["ok"] is True
    print(f"       GET /health -> {r5.status_code}")

    print("\nALL CHECKS PASSED - LUONVUITUOI-HONOR ROLL is working end-to-end.")


if __name__ == "__main__":
    main()
