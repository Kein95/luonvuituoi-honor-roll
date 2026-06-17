"""Page renderers: build the context each Jinja2 template consumes.

Pure functions: they query the store (via the :mod:`honorroll` engine), shape
the result for the template, and return rendered HTML. The Flask layer just
calls these and returns the string. Keeping presentation shaping here means
the CLI and tests can render a page without a running server.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from luonvuitoi_honor.config import HonorConfig
from luonvuitoi_honor.honorroll import (
    hall_of_fame,
    list_all_for_admin,
    list_honor_roll,
    list_schools,
    list_teams,
    search_student,
    stats,
)
from luonvuitoi_honor.ui.templates import render_template

_PUBLIC_BASE_URL = ""


def set_public_base_url(url: str) -> None:
    """Set the canonical site origin (from ``PUBLIC_BASE_URL``) for canonical/og:url tags."""
    global _PUBLIC_BASE_URL
    _PUBLIC_BASE_URL = url or ""


def _base_context(
    config: HonorConfig,
    locale: dict[str, Any],
    csp_nonce: str,
    *,
    admin_authed: bool = False,
    admin_area: bool = False,
    lang: str | None = None,
) -> dict[str, Any]:
    return {
        "csp_nonce": csp_nonce,
        "locale": locale,
        "locale_code": lang or config.project.locale,
        "project_name": (
            config.project.name_en if (lang or config.project.locale) == "en" else config.project.name
        )
        or config.project.name,
        "tagline": (
            config.project.tagline_en if (lang or config.project.locale) == "en" else config.project.tagline
        )
        or locale["brand"]["default_tagline"],
        "primary_color": config.project.branding.primary_color,
        "accent_color": config.project.branding.accent_color,
        "logo_url": config.project.branding.logo_url,
        "layout": config.display.layout,
        "cards_per_row": config.display.cards_per_row,
        "show_rank": config.display.show_rank,
        "show_percentile": config.display.show_percentile,
        "medals": config.medals,
        "competitions": config.competitions,
        "editions": config.editions,
        "years": sorted({e.year for e in config.editions}, reverse=True),
        "show_admin": config.admin.enabled,
        "admin_authed": admin_authed,
        "admin_area": admin_area,
        "contact": config.contact,
        "show_teams": bool(config.team_awards),
        "public_base_url": _PUBLIC_BASE_URL,
    }


def _medal_def(config: HonorConfig, code: str) -> dict[str, Any] | None:
    m = config.medals.get(code)
    return m.model_dump() if m else None


def _competition_name(config: HonorConfig, competition_id: str, *, vi: bool = True) -> str:
    for c in config.competitions:
        if c.id == competition_id:
            return (c.name_vi or c.name) if vi else c.name
    return competition_id


def _subject_options(config: HonorConfig, *, vi: bool) -> list[tuple[str, str, str]]:
    """Distinct subject (code, display-name, icon) across all competitions. Populates the roll filter."""
    seen: dict[str, tuple[str, str]] = {}
    for c in config.competitions:
        for s in c.subjects:
            if s.code not in seen:
                seen[s.code] = ((s.name_vi or s.name) if vi else s.name, s.icon)
    return sorted((code, nm, icon) for code, (nm, icon) in seen.items())


def _subject_name(config: HonorConfig, competition_id: str, code: str, *, vi: bool = True) -> str:
    comp = next((c for c in config.competitions if c.id == competition_id), None)
    if comp:
        for s in comp.subjects:
            if s.code == code:
                return (s.name_vi or s.name) if vi else s.name
    return code


def render_honor_roll_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    db_path: str | Path,
    csp_nonce: str,
    competition_id: str | None = None,
    year: int | None = None,
    medal: str | None = None,
    subject_code: str | None = None,
    school: str | None = None,
    admin_authed: bool = False,
    lang: str | None = None,
) -> str:
    """Render the public honor roll (cards + table + stat dashboard)."""
    vi = (lang or config.project.locale) == "vi"
    page = list_honor_roll(
        config,
        db_path,
        competition_id=competition_id,
        year=year,
        medal=medal,
        subject_code=subject_code,
        school=school,
    )
    s = stats(config, db_path)
    achievements = []
    for a in page.achievements:
        md = _medal_def(config, a.medal)
        achievements.append(
            {
                "id": a.id,
                "name": a.name,
                "grade": a.grade,
                "photo_url": a.photo_url,
                "school": a.school,
                "competition_id": a.competition_id,
                "competition_name": _competition_name(config, a.competition_id, vi=vi),
                "year": a.year,
                "subject_code": a.subject_code,
                "subject_name": _subject_name(config, a.competition_id, a.subject_code, vi=vi),
                "medal": a.medal,
                "medal_label": md["label_vi"]
                if md and (lang or config.project.locale) == "vi"
                else (md["label_en"] if md else a.medal),
                "medal_color": md["color"] if md else "#888888",
                "medal_icon": md["icon"] if md else "🏅",
                "rank": a.rank,
                "percentile": a.percentile,
            }
        )
    ctx = _base_context(config, locale, csp_nonce, admin_authed=admin_authed, lang=lang)
    ctx.update(
        {
            "page_title": locale["roll"]["title"],
            "achievements": achievements,
            "total": page.total,
            "medal_breakdown": [asdict(m) for m in page.medal_breakdown],
            "subject_breakdown": [asdict(s2) for s2 in page.subject_breakdown],
            "stats": s,
            "active_competition": competition_id,
            "active_year": year,
            "active_medal": medal,
            "active_subject": subject_code,
            "active_school": school,
            "subject_options": _subject_options(config, vi=(lang or config.project.locale) == "vi"),
            "schools": list_schools(db_path),
            "upcoming_editions": [e.label for e in config.editions if e.upcoming],
            "years": sorted({e.year for e in config.editions}, reverse=True),
        }
    )
    return render_template("index.html.j2", **ctx)


def render_search_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    db_path: str | Path,
    csp_nonce: str,
    name_query: str | None = None,
    admin_authed: bool = False,
    lang: str | None = None,
) -> str:
    """Render the student search page + results when a query is present."""
    vi = (lang or config.project.locale) == "vi"
    results: list[dict[str, Any]] = []
    if name_query and name_query.strip():
        for a in search_student(db_path, name_query=name_query):
            md = _medal_def(config, a.medal)
            results.append(
                {
                    "id": a.id,
                    "name": a.name,
                    "grade": a.grade,
                    "photo_url": a.photo_url,
                    "school": a.school,
                    "competition_name": _competition_name(config, a.competition_id, vi=vi),
                    "year": a.year,
                    "subject_name": _subject_name(config, a.competition_id, a.subject_code, vi=vi),
                    "medal": a.medal,
                    "medal_label": md["label_vi"]
                    if md and (lang or config.project.locale) == "vi"
                    else (md["label_en"] if md else a.medal),
                    "medal_color": md["color"] if md else "#888888",
                    "medal_icon": md["icon"] if md else "🏅",
                    "rank": a.rank,
                }
            )
    ctx = _base_context(config, locale, csp_nonce, admin_authed=admin_authed, lang=lang)
    ctx.update(
        {
            "page_title": locale["search"]["title"],
            "name_query": name_query or "",
            "results": results,
            "has_query": bool(name_query and name_query.strip()),
        }
    )
    return render_template("search.html.j2", **ctx)


def render_admin_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    db_path: str | Path,
    csp_nonce: str,
    admin_authed: bool = False,
    csrf_token: str = "",
    lang: str | None = None,
) -> str:
    """Render the admin management surface (table + add form)."""
    vi = (lang or config.project.locale) == "vi"
    rows, total = list_all_for_admin(db_path)
    achievements = [
        {
            "id": a.id,
            "name": a.name,
            "grade": a.grade,
            "photo_url": a.photo_url,
            "school": a.school,
            "competition_id": a.competition_id,
            "competition_name": _competition_name(config, a.competition_id, vi=vi),
            "year": a.year,
            "subject_code": a.subject_code,
            "medal": a.medal,
            "rank": a.rank,
            "candidate_no": a.candidate_no,
        }
        for a in rows
    ]
    ctx = _base_context(config, locale, csp_nonce, admin_authed=admin_authed, admin_area=True, lang=lang)
    ctx.update(
        {
            "page_title": locale["admin"]["title"],
            "achievements": achievements,
            "total": total,
            "csrf_token": csrf_token,
        }
    )
    return render_template("admin.html.j2", **ctx)


def render_login_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    csp_nonce: str,
    configured: bool = True,
    error: bool = False,
    locked_out: bool = False,
    retry_after: int = 0,
    csrf_token: str = "",
    lang: str | None = None,
) -> str:
    """Render the admin login page (its own tab/route)."""
    ctx = _base_context(config, locale, csp_nonce, admin_authed=False, admin_area=True, lang=lang)
    ctx.update(
        {
            "page_title": locale["admin"]["login"],
            "login_error": error,
            "admin_configured": configured,
            "locked_out": locked_out,
            "retry_after": retry_after,
            "csrf_token": csrf_token,
        }
    )
    return render_template("login.html.j2", **ctx)


def render_hall_of_fame_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    db_path: str | Path,
    csp_nonce: str,
    admin_authed: bool = False,
    lang: str | None = None,
) -> str:
    """Render the all-time Hall of Fame (top achievers across every edition)."""
    vi = (lang or config.project.locale) == "vi"
    stars = []
    for s in hall_of_fame(config, db_path):
        md = _medal_def(config, s["best_medal"])
        stars.append(
            {
                "name": s["name"],
                "grade": s["grade"],
                "school": s["school"],
                "photo_url": s["photo_url"],
                "count": s["count"],
                "medal_label": md["label_vi"] if md and vi else (md["label_en"] if md else s["best_medal"]),
                "medal_color": md["color"] if md else "#888888",
                "medal_icon": md["icon"] if md else "🏅",
            }
        )
    ctx = _base_context(config, locale, csp_nonce, admin_authed=admin_authed, lang=lang)
    ctx.update({"page_title": locale["hall"]["title"], "stars": stars})
    return render_template("hall.html.j2", **ctx)


def render_teams_page(
    *,
    config: HonorConfig,
    locale: dict[str, Any],
    db_path: str | Path,
    csp_nonce: str,
    admin_authed: bool = False,
    lang: str | None = None,
) -> str:
    """Render the All-Star Team page (group/team awards across editions)."""
    vi = (lang or config.project.locale) == "vi"
    teams = []
    for t in list_teams(config, db_path):
        ad = config.team_awards.get(t.award)
        teams.append(
            {
                "name": t.name,
                "award_label": (ad.label_vi if vi else ad.label_en) if ad else t.award,
                "award_color": ad.color if ad else "#888888",
                "award_icon": ad.icon if ad else "🏆",
                "subject": t.subject,
                "category": t.category,
                "year": t.year,
                "members": t.members,
            }
        )
    ctx = _base_context(config, locale, csp_nonce, admin_authed=admin_authed, lang=lang)
    ctx.update({"page_title": locale["teams"]["title"], "teams": teams})
    return render_template("teams.html.j2", **ctx)
