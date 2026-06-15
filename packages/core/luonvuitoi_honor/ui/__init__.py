"""UI layer: Jinja2 template loader + page renderers."""

from luonvuitoi_honor.ui.pages import (
    render_admin_page,
    render_hall_of_fame_page,
    render_honor_roll_page,
    render_login_page,
    render_search_page,
    render_teams_page,
    set_public_base_url,
)
from luonvuitoi_honor.ui.templates import RenderError, render_template

__all__ = [
    "render_honor_roll_page",
    "render_search_page",
    "render_admin_page",
    "render_hall_of_fame_page",
    "render_teams_page",
    "render_login_page",
    "set_public_base_url",
    "render_template",
    "RenderError",
]
