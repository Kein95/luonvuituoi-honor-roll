"""Jinja2 environment that loads the bundled page templates.

Templates ship inside the wheel under ``luonvuitoi_honor/templates`` and are
read via :mod:`importlib.resources`, so a deployed wheel needs no extra file
mounting. ``csp_nonce`` is threaded into every render so the Flask app's
per-request Content-Security-Policy can whitelist the inline scripts.
"""

from __future__ import annotations

from importlib import resources
from typing import Any

from jinja2 import Environment, FunctionLoader, select_autoescape

_TEMPLATE_PKG = "luonvuitoi_honor.templates"


def _load_source(name: str) -> str | None:
    """Read one template file from the package; return None if missing."""
    try:
        return resources.files(_TEMPLATE_PKG).joinpath(name).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


_env = Environment(
    loader=FunctionLoader(_load_source),
    autoescape=select_autoescape(["html", "html.j2", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


class RenderError(Exception):
    """Raised when a template is missing or fails to render."""


def render_template(name: str, **context: Any) -> str:
    """Render a bundled template, raising :class:`RenderError` on failure."""
    if _env.loader.get_source(_env, name)[0] is None:  # type: ignore[union-attr]
        raise RenderError(f"template not found: {name}")
    try:
        return _env.get_template(name).render(**context)
    except Exception as e:  # noqa: BLE001 - surface a readable message
        raise RenderError(f"failed to render {name}: {e}") from e
