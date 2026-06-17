"""Flask app builder for the local dev server.

Deliberately minimal: each route reads params, calls the matching pure-function
handler in :mod:`luonvuitoi_honor`, and returns the result. Dev matches prod:
a per-request CSP nonce whitelists inline scripts, and security headers are
applied on every response.
"""

from __future__ import annotations

import hmac
import json
import os
import secrets
from dataclasses import asdict
from pathlib import Path

from flask import Flask, Response, g, jsonify, make_response, redirect, request, session
from luonvuitoi_honor import api as honor_api
from luonvuitoi_honor.config import HonorConfig, load_config
from luonvuitoi_honor.locale import load_locale
from luonvuitoi_honor.ui import (
    render_admin_page,
    render_hall_of_fame_page,
    render_honor_roll_page,
    render_login_page,
    render_search_page,
    render_teams_page,
    set_public_base_url,
)

from .security import (
    LoginRateLimiter,
    csrf_valid,
    ensure_csrf_token,
    record_activity,
)

MAX_BODY_BYTES = 32 * 1024


def _json_body() -> dict:
    raw = request.get_data(cache=False) or b""
    if len(raw) > MAX_BODY_BYTES:
        raise honor_api.ApiError("request body too large")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise honor_api.ApiError(f"invalid JSON body: {e.msg}") from e
    if not isinstance(parsed, dict):
        raise honor_api.ApiError("request body must be a JSON object")
    return parsed


def build_app(config_path: Path, project_root: Path) -> Flask:
    config = load_config(config_path)
    db_path = project_root / "data" / f"{config.project.slug}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES
    app.config["HONOR_DB_PATH"] = str(db_path)  # exposed for tooling/tests (e.g. audit reads)
    # Signed-cookie sessions for admin auth. SECRET_KEY persists logins across
    # restarts; an ephemeral key is fine for dev but logs everyone out on reboot.
    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    # Admin password is read from the environment only — never from the committed config.
    admin_password = os.environ.get("ADMIN_PASSWORD", "")

    # Brute-force guard for the login form. Per-IP, per-process (see security.py).
    login_limiter = LoginRateLimiter(
        max_attempts=_int_env("ADMIN_LOGIN_MAX_ATTEMPTS", 5),
        lockout_seconds=_int_env("ADMIN_LOGIN_LOCKOUT_SECONDS", 60),
    )

    # Deploy hardening knobs (read from env so docker-compose / Vercel can set them).
    force_hsts = _flag("FORCE_HSTS")
    allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    set_public_base_url(os.environ.get("PUBLIC_BASE_URL", ""))
    if _flag("TRUST_PROXY_HEADERS"):
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]

    def _authed() -> bool:
        return bool(session.get("admin"))

    @app.before_request
    def _nonce() -> None:
        g.csp_nonce = secrets.token_urlsafe(16)
        g.lang = _resolve_lang(config)
        g.locale = load_locale(g.lang)

    @app.context_processor
    def _inject_nonce():
        return {"csp_nonce": g.csp_nonce}

    @app.errorhandler(honor_api.ApiError)
    def _api_err(e):
        return jsonify({"error": str(e)}), 400

    @app.get("/health")
    def _health():
        return jsonify({"ok": True}), 200

    @app.get("/")
    def _roll():
        return render_honor_roll_page(
            config=config,
            locale=g.locale,
            db_path=db_path,
            csp_nonce=g.csp_nonce,
            competition_id=request.args.get("competition") or None,
            year=_int_or_none(request.args.get("year")),
            medal=request.args.get("medal") or None,
            subject_code=request.args.get("subject") or None,
            school=request.args.get("school") or None,
            admin_authed=_authed(),
            lang=g.lang,
        )

    @app.get("/search")
    def _search():
        return render_search_page(
            config=config,
            locale=g.locale,
            db_path=db_path,
            csp_nonce=g.csp_nonce,
            name_query=request.args.get("q") or None,
            admin_authed=_authed(),
            lang=g.lang,
        )

    @app.get("/hall-of-fame")
    def _hall():
        return render_hall_of_fame_page(
            config=config, locale=g.locale, db_path=db_path, csp_nonce=g.csp_nonce,
            admin_authed=_authed(), lang=g.lang,
        )

    @app.get("/teams")
    def _teams():
        return render_teams_page(
            config=config, locale=g.locale, db_path=db_path, csp_nonce=g.csp_nonce,
            admin_authed=_authed(), lang=g.lang,
        )

    @app.get("/login")
    def _login_form():
        if not config.admin.enabled:
            return ("admin disabled", 404)
        if _authed():
            return redirect("/admin")
        return render_login_page(
            config=config, locale=g.locale, csp_nonce=g.csp_nonce,
            configured=bool(admin_password), csrf_token=ensure_csrf_token(session), lang=g.lang,
        )

    @app.post("/login")
    def _login():
        if not config.admin.enabled:
            return ("admin disabled", 404)
        ip = _client_ip()
        if not admin_password:
            return (
                render_login_page(config=config, locale=g.locale, csp_nonce=g.csp_nonce, configured=False, lang=g.lang),
                503,
            )
        # CSRF: the token is minted on GET /login and echoed back in a hidden field.
        if not csrf_valid(session, request.form.get("csrf_token")):
            record_activity(db_path, "login.csrf_reject", ip=ip)
            return (
                render_login_page(
                    config=config, locale=g.locale, csp_nonce=g.csp_nonce, error=True,
                    csrf_token=ensure_csrf_token(session), lang=g.lang,
                ),
                400,
            )
        # Brute-force lockout takes precedence over checking the password.
        wait = login_limiter.retry_after(ip)
        if wait > 0:
            record_activity(db_path, "login.lockout", ip=ip, detail=f"retry_after={wait}s")
            resp = make_response(
                render_login_page(
                    config=config, locale=g.locale, csp_nonce=g.csp_nonce,
                    locked_out=True, retry_after=wait, csrf_token=ensure_csrf_token(session), lang=g.lang,
                ),
                429,
            )
            resp.headers["Retry-After"] = str(wait)
            return resp
        supplied = request.form.get("password") or ""
        if hmac.compare_digest(supplied, admin_password):
            login_limiter.reset(ip)
            session["admin"] = True
            session.pop("csrf_token", None)  # rotate the token on privilege change
            record_activity(db_path, "login.success", ip=ip)
            return redirect("/admin")
        login_limiter.record_failure(ip)
        record_activity(db_path, "login.failure", ip=ip)
        return (
            render_login_page(
                config=config, locale=g.locale, csp_nonce=g.csp_nonce, error=True,
                csrf_token=ensure_csrf_token(session), lang=g.lang,
            ),
            401,
        )

    @app.route("/logout", methods=["GET", "POST"])
    def _logout():
        if session.get("admin"):
            record_activity(db_path, "logout", ip=_client_ip())
        session.pop("admin", None)
        session.pop("csrf_token", None)
        return redirect("/")

    @app.get("/admin")
    def _admin():
        if not config.admin.enabled:
            return ("admin disabled", 404)
        if not _authed():
            return redirect("/login")
        return render_admin_page(
            config=config, locale=g.locale, db_path=db_path, csp_nonce=g.csp_nonce,
            admin_authed=True, csrf_token=ensure_csrf_token(session), lang=g.lang,
        )

    @app.post("/api/admin/achievements")
    def _add():
        if not config.admin.enabled:
            return jsonify({"error": "admin disabled"}), 404
        if not _authed():
            return jsonify({"error": "authentication required"}), 401
        if not csrf_valid(session, request.headers.get("X-CSRF-Token")):
            return jsonify({"error": "invalid CSRF token"}), 403
        created = honor_api.add_achievement(config=config, db_path=db_path, payload=_json_body())
        record_activity(db_path, "admin.add", ip=_client_ip(), target=created.id)
        return jsonify(asdict(created)), 201

    @app.delete("/api/admin/achievements/<int:achievement_id>")
    def _delete(achievement_id: int):
        if not config.admin.enabled:
            return jsonify({"error": "admin disabled"}), 404
        if not _authed():
            return jsonify({"error": "authentication required"}), 401
        if not csrf_valid(session, request.headers.get("X-CSRF-Token")):
            return jsonify({"error": "invalid CSRF token"}), 403
        removed = honor_api.delete_achievement(db_path, achievement_id=achievement_id)
        record_activity(db_path, "admin.delete", ip=_client_ip(), target=achievement_id)
        return jsonify({"deleted": removed, "id": achievement_id})

    @app.get("/api/stats")
    def _stats_api():
        from luonvuitoi_honor.honorroll import stats

        return jsonify(stats(config, db_path))

    @app.get("/api/search")
    def _search_api():
        from dataclasses import asdict as _asdict

        from luonvuitoi_honor.honorroll import search_student

        q = request.args.get("q") or ""
        if not q.strip():
            return jsonify({"results": [], "query": ""})
        rows = search_student(db_path, name_query=q)
        return jsonify({"query": q, "results": [{**_asdict(r)} for r in rows]})

    @app.after_request
    def _headers(response: Response) -> Response:
        if response.mimetype == "text/html":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{g.csp_nonce}'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "frame-ancestors 'none'"
            )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        if force_hsts:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if allowed_origins and request.path.startswith("/api/"):
            origin = request.headers.get("Origin")
            if origin and ("*" in allowed_origins or origin in allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = "*" if "*" in allowed_origins else origin
                response.headers.setdefault("Vary", "Origin")
        # Remember an explicit language choice so it sticks across pages.
        if request.args.get("lang") in ("en", "vi"):
            response.set_cookie("lang", request.args["lang"], max_age=31536000, samesite="Lax", httponly=True)
        return response

    return app


def _flag(name: str) -> bool:
    """Truthy check for an env flag (1/true/yes/on)."""
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _int_env(name: str, default: int) -> int:
    """Read a positive integer env var, falling back to ``default`` if unset/invalid."""
    try:
        value = int(os.environ.get(name, ""))
    except ValueError:
        return default
    return value if value >= 1 else default


def _client_ip() -> str:
    """Best-effort client IP. ProxyFix rewrites remote_addr from X-Forwarded-For
    when TRUST_PROXY_HEADERS is set, so this is correct behind a trusted proxy."""
    return request.remote_addr or "unknown"


def _resolve_lang(config: HonorConfig) -> str:
    """Pick UI language: ?lang= override -> saved cookie -> Accept-Language -> config default."""
    lang = request.args.get("lang")
    if lang not in ("en", "vi"):
        lang = request.cookies.get("lang")
    if lang not in ("en", "vi"):
        lang = request.accept_languages.best_match(["vi", "en"]) or config.project.locale
    return lang


def _int_or_none(v: str | None) -> int | None:
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None
