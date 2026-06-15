"""Unit tests for :mod:`luonvuitoi_honor.config.models`.

These lock down cross-field invariants (editions reference declared
competitions, medals are registered, IDs/codes are unique) so future schema
changes fail loud instead of silently allowing malformed configs to reach the
handlers.
"""

from __future__ import annotations

import copy

import pytest
from luonvuitoi_honor.config import HonorConfig
from luonvuitoi_honor.config.models import Branding, Project
from pydantic import ValidationError


def _valid_raw() -> dict:
    return {
        "project": {"name": "Test", "slug": "test"},
        "competitions": [{"id": "demo-a", "name": "Demo Olympiad A", "medals": ["GOLD", "SILVER"]}],
        "editions": [{"competition_id": "demo-a", "year": 2025, "label": "Demo Olympiad A 2025"}],
        "medals": {
            "GOLD": {"rank": 1, "label_en": "Gold", "label_vi": "Vàng"},
            "SILVER": {"rank": 2, "label_en": "Silver", "label_vi": "Bạc"},
        },
    }


def test_minimal_config_loads_with_defaults() -> None:
    cfg = HonorConfig.model_validate(_valid_raw())
    assert cfg.project.locale == "vi"  # Vietnamese is the project default
    assert cfg.display.layout == "both"
    assert cfg.display.cards_per_row == 4
    assert cfg.admin.enabled is True
    assert cfg.data_mapping.medal_col == "medal"  # default


def test_slug_must_be_kebab_case() -> None:
    with pytest.raises(ValidationError):
        Project(name="Demo", slug="Invalid Slug")
    with pytest.raises(ValidationError):
        Project(name="Demo", slug="UPPER")
    with pytest.raises(ValidationError):
        Project(name="Demo", slug="trailing-")
    # Valid kebab-case.
    Project(name="Demo", slug="demo-academy")


def test_hex_color_validated() -> None:
    with pytest.raises(ValidationError):
        Branding(primary_color="not-a-color")
    # 6-digit hex ok.
    b = Branding(primary_color="#1E3A8A", accent_color="#abc")
    assert b.primary_color == "#1E3A8A"


def test_logo_url_rejects_javascript_scheme() -> None:
    with pytest.raises(ValidationError):
        Branding(logo_url="javascript:alert(1)")
    # http/data/relative are fine.
    assert Branding(logo_url="/img.png").logo_url == "/img.png"
    assert Branding(logo_url="https://x.test/l.png").logo_url == "https://x.test/l.png"


def test_competition_id_must_be_ident() -> None:
    raw = _valid_raw()
    raw["competitions"][0]["id"] = "bad id!"
    with pytest.raises(ValidationError):
        HonorConfig.model_validate(raw)


def test_competition_ids_must_be_unique() -> None:
    raw = _valid_raw()
    raw["competitions"].append(copy.deepcopy(raw["competitions"][0]))
    with pytest.raises(ValidationError, match="unique"):
        HonorConfig.model_validate(raw)


def test_medals_uppercased_and_deduped() -> None:
    raw = _valid_raw()
    raw["competitions"][0]["medals"] = ["gold", "GOLD"]
    with pytest.raises(ValidationError, match="unique"):
        HonorConfig.model_validate(raw)


def test_competition_medals_must_be_registered() -> None:
    raw = _valid_raw()
    raw["competitions"][0]["medals"] = ["GOLD", "FAKE"]
    with pytest.raises(ValidationError, match="not in the global medal registry"):
        HonorConfig.model_validate(raw)


def test_edition_must_reference_declared_competition() -> None:
    raw = _valid_raw()
    raw["editions"][0]["competition_id"] = "nope"
    with pytest.raises(ValidationError, match="unknown competition_id"):
        HonorConfig.model_validate(raw)


def test_editions_unique_by_competition_year() -> None:
    raw = _valid_raw()
    raw["editions"].append(copy.deepcopy(raw["editions"][0]))
    with pytest.raises(ValidationError, match="unique"):
        HonorConfig.model_validate(raw)


def test_medal_ranks_unique() -> None:
    raw = _valid_raw()
    raw["medals"]["GOLD"]["rank"] = 2  # clashes with SILVER
    with pytest.raises(ValidationError, match="medal ranks must be unique"):
        HonorConfig.model_validate(raw)


def test_competition_subject_codes_unique() -> None:
    raw = _valid_raw()
    raw["competitions"][0]["subjects"] = [
        {"code": "MATH", "name": "Math"},
        {"code": "MATH", "name": "Maths"},
    ]
    with pytest.raises(ValidationError, match="duplicate subject codes"):
        HonorConfig.model_validate(raw)


def test_year_bounds() -> None:
    raw = _valid_raw()
    raw["editions"][0]["year"] = 1800
    with pytest.raises(ValidationError):
        HonorConfig.model_validate(raw)


def test_medal_code_must_be_safe_identifier() -> None:
    # Codes are interpolated into SQL CASE clauses, so quotes/spaces must be rejected.
    raw = _valid_raw()
    raw["medals"]["O'HARA"] = {"rank": 99, "label_en": "x", "label_vi": "y"}
    with pytest.raises(ValidationError, match="must match"):
        HonorConfig.model_validate(raw)
