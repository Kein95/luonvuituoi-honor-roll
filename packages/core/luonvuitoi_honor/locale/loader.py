"""Locale loader: read bundled en/vi JSON dictionaries via importlib.resources.

Ships English + Vietnamese out of the box; the project's ``locale`` config key
selects which one the UI renders. Falls back to English when a key is missing
rather than rendering a raw ``{{ key }}`` placeholder.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from luonvuitoi_honor.config.models import LocaleCode

_PKG = "luonvuitoi_honor.locale"


@lru_cache(maxsize=8)
def _load_raw(locale: LocaleCode) -> dict[str, Any]:
    """Read and cache one locale file; English is always available as fallback."""
    try:
        text = resources.files(_PKG).joinpath(f"{locale}.json").read_text(encoding="utf-8")
        return json.loads(text)
    except (FileNotFoundError, OSError):
        if locale == "en":
            return {}
        return _load_raw("en")


def load_locale(locale: LocaleCode) -> dict[str, Any]:
    """Return the merged locale dict (requested + English fallback under it)."""
    base = _load_raw("en")
    if locale == "en":
        return _deep_copy(base)
    overlay = _load_raw(locale)
    return _deep_merge(base, overlay)


def _deep_copy(d: dict[str, Any]) -> dict[str, Any]:
    return {k: (_deep_copy(v) if isinstance(v, dict) else v) for k, v in d.items()}


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = _deep_copy(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out
