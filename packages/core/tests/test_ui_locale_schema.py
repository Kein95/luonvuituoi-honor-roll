"""Tests for the UI renderers, locale loader, and JSON-schema sync."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from luonvuitoi_honor.locale import load_locale
from luonvuitoi_honor.ui import render_admin_page, render_honor_roll_page, render_search_page

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA_PATH = _REPO_ROOT / "honor.schema.json"


def test_locale_vi_has_all_keys_of_en() -> None:
    en = load_locale("en")
    vi = load_locale("vi")

    def keys(d, prefix=""):  # type: ignore[no-untyped-def]
        for k, v in d.items():
            if isinstance(v, dict):
                yield from keys(v, prefix + k + ".")
            else:
                yield prefix + k

    missing = sorted(set(keys(en)) - set(keys(vi)))
    assert not missing, f"vi locale missing keys: {missing}"


def test_locale_unknown_falls_back_to_en() -> None:
    # 'fr' isn't bundled; loader must fall back to English, not crash.
    fr = load_locale("fr")  # type: ignore[arg-type]
    assert fr["roll"]["title"] == "Honor Roll"


def test_render_honor_roll_contains_known_student(populated_db, honor_config):  # type: ignore[no-untyped-def]
    html = render_honor_roll_page(
        config=honor_config, locale=load_locale("en"), db_path=populated_db, csp_nonce="n1"
    )
    assert "Alice Gold" in html
    assert "School A" in html
    assert "Honor Roll" in html  # page title


def test_render_honor_roll_empty_db_renders_no_results(honor_config, db_path):  # type: ignore[no-untyped-def]
    from luonvuitoi_honor.storage import init_db

    init_db(str(db_path))
    html = render_honor_roll_page(
        config=honor_config, locale=load_locale("en"), db_path=db_path, csp_nonce="n"
    )
    assert "No achievements" in html  # empty-state copy


def test_render_search_with_query(populated_db, honor_config):  # type: ignore[no-untyped-def]
    html = render_search_page(
        config=honor_config, locale=load_locale("en"), db_path=populated_db, csp_nonce="n", name_query="Gold"
    )
    assert "Alice Gold" in html
    assert "Eve Gold" in html


def test_render_search_no_query_shows_form_only(populated_db, honor_config):  # type: ignore[no-untyped-def]
    html = render_search_page(
        config=honor_config, locale=load_locale("en"), db_path=populated_db, csp_nonce="n", name_query=""
    )
    assert "Find a student" in html  # the form heading
    assert "Alice Gold" not in html  # no results rendered


def test_render_admin_lists_rows(populated_db, honor_config):  # type: ignore[no-untyped-def]
    html = render_admin_page(
        config=honor_config, locale=load_locale("en"), db_path=populated_db, csp_nonce="n"
    )
    assert "Alice Gold" in html
    assert "Admin" in html


@pytest.mark.skipif(not _SCHEMA_PATH.exists(), reason="schema not exported yet")
def test_schema_in_sync_with_models() -> None:
    """The committed honor.schema.json must match the live Pydantic schema.

    If you edit ``config/models.py``, re-run ``python scripts/export_schema.py``
    so editor autocomplete stays correct. Mirrors the CERT ``test_schema_export``.
    """
    from luonvuitoi_honor.config.models import HonorConfig

    committed = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    live = HonorConfig.model_json_schema()
    assert committed == live, (
        "honor.schema.json is out of sync with config.models. Run "
        "`python scripts/export_schema.py` to regenerate."
    )
