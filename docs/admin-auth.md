# Admin authentication

The honor roll uses a single password-based login scheme, checked with a timing-safe HMAC compare to prevent timing attacks.

## Login flow

1. Navigate to `https://<your-portal>/login`.
2. Enter the admin password (set via `ADMIN_PASSWORD` environment variable).
3. Click **Sign in**. On success, a signed Flask session cookie is issued.
4. The session is valid for the browser tab. Closing the tab logs you out.

## Password configuration

**Required.** The admin password is read from the environment only, never from the committed config:

```bash
export ADMIN_PASSWORD="your-secure-password-here"
```

Change the password by restarting the application with a new `ADMIN_PASSWORD` value. All active sessions remain valid until the browser is closed.

## Security features

### Timing-safe comparison

The password is checked using `hmac.compare_digest()`, a constant-time comparison that prevents an observer from deducing password length or content via response-time analysis. Even for an invalid password, the server performs the same cryptographic work before rejecting the login.

### Session cookies

Sessions are stored in signed Flask cookies with the following protections:

- **`SESSION_COOKIE_HTTPONLY=True`**: The session token is never accessible to JavaScript, closing XSS exfiltration paths.
- **`SESSION_COOKIE_SAMESITE="Lax"`**: Cookies are not sent on cross-site requests, mitigating CSRF.
- **`SECRET_KEY`**: Signs the cookie. If not set, a random ephemeral key is generated (sessions are lost on restart). For production, set a stable key:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

### Content Security Policy

Every HTML response includes a `Content-Security-Policy` header with a per-request nonce, preventing inline script injection.

## Admin disabling

Set `admin.enabled: false` in your `honor.config.json` to disable the entire admin surface:

```json
"admin": { "enabled": false, "auth_mode": "password" }
```

Requests to `/login`, `/admin`, or `/api/admin/*` return HTTP 404.

## Hardening features (in development)

The following features are being added concurrently and are present in current builds:

### Login brute-force rate limiting

A per-IP rate limiter prevents password-guessing attacks:

- After `N` failed login attempts (default: 5), the IP is locked for `M` seconds (default: 60).
- Failed attempts are tracked per IP address, not per user (since the login form doesn't ask for a username).
- The cooldown timer resets after each failed attempt.

Configure via environment variables:

```bash
export ADMIN_LOGIN_MAX_ATTEMPTS=5
export ADMIN_LOGIN_LOCKOUT_SECONDS=60
```

### CSRF token on admin POST forms

All admin forms (`<form method="POST">`) include a hidden CSRF token field. The server verifies the token before processing any write operation:

- A token is bound to your session and rotated whenever you log in or out.
- The admin write API (`/api/admin/*`) requires the same token in an `X-CSRF-Token` request header; a missing or invalid token results in HTTP 403 (Forbidden). The login form rejects a missing token with HTTP 400.
- This prevents cross-site request forgery from an attacker's page.

### Audit logging of login success/failure and admin actions

Every admin operation is logged:

- **Login success**: Timestamp, IP address, session start.
- **Login failure**: Timestamp, IP address, reason (incorrect password, lockout, etc.).
- **Admin write**: Timestamp, IP, action (add achievement, delete achievement), and target student ID.

Logs are persisted in the SQLite database (`admin_activity` table) and are readable via SQL:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity ORDER BY timestamp DESC LIMIT 20;"
```

## Transport-layer contract

Any handler that calls the login endpoint **must**:

1. Validate the request size before parsing (the Flask app does this at 32 KB max).
2. Catch auth errors and translate to HTTP 401.
3. Emit the CSP header with a nonce on HTML responses.

The development server (`lvt-honor dev`) and the Vercel handler (`api/index.py`) both implement these contracts. Custom transports should follow the same pattern.
