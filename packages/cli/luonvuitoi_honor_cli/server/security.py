"""Admin login hardening for the Flask server.

Three concerns, deliberately small:

* :class:`LoginRateLimiter`: in-process brute-force guard keyed by client IP.
* CSRF tokens: per-session token issued to admin forms and required on writes.
* Audit log: append-only ``admin_activity`` rows in the project SQLite db.

The rate limiter is per-process by design: it fits the single-instance dev /
Docker deploy this project targets. A multi-instance serverless deploy would
need a shared counter store (see ``docs/security``); that is intentionally out
of scope here.
"""

from __future__ import annotations

import hmac
import secrets
import sqlite3
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# --- Brute-force rate limiting -------------------------------------------


class LoginRateLimiter:
    """Lock an IP out after too many failed logins.

    Tracks ``(fail_count, last_attempt_ts)`` per identifier. Once ``fail_count``
    reaches ``max_attempts`` the identifier is blocked until ``lockout_seconds``
    have elapsed since its *last* failed attempt, so hammering the form during
    a lockout keeps pushing the unlock time out. A success clears the entry.
    Thread-safe for the threaded Flask dev server.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        lockout_seconds: int = 60,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if lockout_seconds < 1:
            raise ValueError("lockout_seconds must be >= 1")
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self._clock = clock or time.time
        self._state: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def retry_after(self, identifier: str) -> int:
        """Seconds the identifier must wait, or ``0`` if it may attempt now."""
        with self._lock:
            entry = self._state.get(identifier)
            if not entry:
                return 0
            count, last_ts = entry
            if count < self.max_attempts:
                return 0
            elapsed = self._clock() - last_ts
            if elapsed >= self.lockout_seconds:
                self._state.pop(identifier, None)  # lockout window fully elapsed
                return 0
            return max(int(self.lockout_seconds - elapsed) + 1, 1)

    def record_failure(self, identifier: str) -> None:
        """Note one failed attempt for the identifier."""
        with self._lock:
            count, last_ts = self._state.get(identifier, (0, 0.0))
            now = self._clock()
            if count >= self.max_attempts and (now - last_ts) >= self.lockout_seconds:
                count = 0  # a prior lockout has expired; start a fresh streak
            self._state[identifier] = (count + 1, now)

    def reset(self, identifier: str) -> None:
        """Clear the failure streak (call on a successful login)."""
        with self._lock:
            self._state.pop(identifier, None)


# --- CSRF -----------------------------------------------------------------


def ensure_csrf_token(session: Any) -> str:
    """Return the session CSRF token, minting one on first use."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def csrf_valid(session: Any, supplied: str | None) -> bool:
    """Constant-time compare ``supplied`` against the session CSRF token."""
    expected = session.get("csrf_token")
    if not expected or not supplied:
        return False
    return hmac.compare_digest(str(supplied), str(expected))


# --- Audit log (SQLite) ---------------------------------------------------

_AUDIT_DDL = (
    "CREATE TABLE IF NOT EXISTS admin_activity ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "timestamp TEXT NOT NULL,"
    "action TEXT NOT NULL,"
    "ip TEXT,"
    "target TEXT,"
    "detail TEXT)"
)

_AUDIT_COLUMNS = ("timestamp", "action", "ip", "target", "detail")


def _connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute(_AUDIT_DDL)
    return conn


def record_activity(
    db_path: str | Path,
    action: str,
    *,
    ip: str | None = None,
    target: Any = None,
    detail: str | None = None,
) -> None:
    """Append one audit row. Never raises into the request path; a failed
    audit write must not break the operation it was recording."""
    try:
        conn = _connect(db_path)
        with conn:
            conn.execute(
                "INSERT INTO admin_activity (timestamp, action, ip, target, detail) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now(UTC).isoformat(timespec="seconds"),
                    action,
                    ip,
                    None if target is None else str(target),
                    detail,
                ),
            )
        conn.close()
    except sqlite3.Error:
        pass


def recent_activity(db_path: str | Path, limit: int = 20) -> list[dict[str, Any]]:
    """Read back the most recent audit rows (for the CLI / tests)."""
    try:
        conn = _connect(db_path)
        rows = conn.execute(
            "SELECT timestamp, action, ip, target, detail FROM admin_activity ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        conn.close()
    except sqlite3.Error:
        return []
    return [dict(zip(_AUDIT_COLUMNS, row)) for row in rows]
