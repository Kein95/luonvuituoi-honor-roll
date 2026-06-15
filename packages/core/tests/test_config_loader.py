"""Tests for the config loader (file → :class:`HonorConfig`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from luonvuitoi_honor.config import ConfigError, load_config, load_config_dict


def _valid_raw() -> dict:
    return {
        "$schema": "honor.schema.json",  # must be stripped transparently
        "project": {"name": "T", "slug": "t"},
        "competitions": [{"id": "c", "name": "C", "medals": ["GOLD"]}],
        "editions": [{"competition_id": "c", "year": 2025, "label": "L"}],
        "medals": {"GOLD": {"rank": 1, "label_en": "G", "label_vi": "V"}},
    }


def test_schema_key_stripped() -> None:
    cfg = load_config_dict(_valid_raw())
    assert cfg.project.slug == "t"


def test_load_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.json")


def test_load_config_bad_json(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid JSON"):
        load_config(p)


def test_load_config_invalid_utf8(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_bytes(b'{"x": "\xff"}')
    with pytest.raises(ConfigError, match="UTF-8"):
        load_config(p)


def test_load_config_root_not_object(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(ConfigError, match="JSON object"):
        load_config(p)


def test_load_config_validation_error_is_readable(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    raw = _valid_raw()
    raw["medals"]["GOLD"]["rank"] = "not-a-number"
    p.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ConfigError) as exc:
        load_config(p)
    # The pydantic hint URL must NOT leak into the user-facing message.
    assert "errors.pydantic.dev" not in str(exc.value)
