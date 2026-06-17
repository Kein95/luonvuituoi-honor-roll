"""Unit tests for the login hardening primitives in ``server.security``.

Pure and fast — no Flask app needed. The rate limiter uses an injected clock so
lockout timing is deterministic.
"""

from __future__ import annotations

import pytest
from luonvuitoi_honor_cli.server.security import (
    LoginRateLimiter,
    csrf_valid,
    ensure_csrf_token,
    recent_activity,
    record_activity,
)


class _Clock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


# --- Rate limiter ---------------------------------------------------------


def test_rate_limiter_allows_until_threshold():
    clock = _Clock()
    rl = LoginRateLimiter(max_attempts=3, lockout_seconds=60, clock=clock)
    assert rl.retry_after("ip") == 0
    rl.record_failure("ip")
    rl.record_failure("ip")
    assert rl.retry_after("ip") == 0  # 2 < 3, still allowed
    rl.record_failure("ip")
    assert rl.retry_after("ip") > 0  # 3rd failure trips the lockout


def test_rate_limiter_lockout_expires_with_time():
    clock = _Clock()
    rl = LoginRateLimiter(max_attempts=2, lockout_seconds=30, clock=clock)
    rl.record_failure("ip")
    rl.record_failure("ip")
    assert rl.retry_after("ip") > 0
    clock.t += 31  # cooldown elapsed
    assert rl.retry_after("ip") == 0


def test_rate_limiter_reset_clears_streak():
    rl = LoginRateLimiter(max_attempts=2, lockout_seconds=60)
    rl.record_failure("ip")
    rl.record_failure("ip")
    assert rl.retry_after("ip") > 0
    rl.reset("ip")
    assert rl.retry_after("ip") == 0


def test_rate_limiter_isolates_identifiers():
    rl = LoginRateLimiter(max_attempts=1, lockout_seconds=60)
    rl.record_failure("ip-a")
    assert rl.retry_after("ip-a") > 0
    assert rl.retry_after("ip-b") == 0  # a different IP is unaffected


def test_rate_limiter_rejects_bad_config():
    with pytest.raises(ValueError):
        LoginRateLimiter(max_attempts=0)
    with pytest.raises(ValueError):
        LoginRateLimiter(lockout_seconds=0)


# --- CSRF -----------------------------------------------------------------


def test_csrf_token_minted_once_and_validates():
    session: dict = {}
    token = ensure_csrf_token(session)
    assert token
    assert ensure_csrf_token(session) == token  # stable within a session
    assert csrf_valid(session, token) is True
    assert csrf_valid(session, "wrong") is False
    assert csrf_valid(session, None) is False
    assert csrf_valid({}, token) is False  # no token in session


# --- Audit log ------------------------------------------------------------


def test_audit_round_trip(tmp_path):
    db = tmp_path / "audit.db"
    record_activity(db, "login.success", ip="1.2.3.4")
    record_activity(db, "admin.add", ip="1.2.3.4", target=7, detail="x")
    rows = recent_activity(db, limit=10)
    assert len(rows) == 2
    assert rows[0]["action"] == "admin.add"  # newest first
    assert rows[0]["target"] == "7"
    assert rows[1]["action"] == "login.success"


def test_audit_never_raises_on_bad_path(tmp_path):
    # A directory path is not a writable db; the call must swallow the error.
    record_activity(tmp_path, "login.success")
    assert recent_activity(tmp_path) == []
