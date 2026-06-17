# Security

Security guidance for deploying and operating LUONVUITUOI-HONOR ROLL.

## Overview

The portal is designed as a **read-public, write-gated** system:

- **Public surfaces** (`/`, `/search`, `/hall-of-fame`, `/teams`) serve unauthenticated visitor traffic.
- **Admin surface** (`/admin`, `/api/admin/*`) requires password authentication.
- **No PII** is exposed publicly; only name, school, medal, subject, and rank are visible.

## Admin authentication

See [admin-auth.md](admin-auth.md) for the full authentication model.

Summary:

- Single password login via `ADMIN_PASSWORD` environment variable.
- Timing-safe HMAC compare to prevent timing attacks.
- Signed Flask session cookies with `HTTPOnly` and `SameSite=Lax` flags.
- Per-IP brute-force rate limiting (configurable, default: 5 attempts in 60 seconds).
- CSRF token on all admin POST forms.
- Audit logging of all login success/failure and admin write actions.

## Deploying the admin surface securely

The admin surface is **not production-safe by default**. If you expose the portal publicly, gate `/admin` behind a reverse proxy:

### Option 1: Reverse proxy with Basic Auth (Nginx)

```nginx
location /admin {
    auth_basic "Admin required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}

location /api/admin {
    auth_basic "Admin required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}
```

### Option 2: Reverse proxy with OAuth (Caddy)

Use a forward-auth plugin like `oauth2-proxy`:

```
https://example.com/admin {
    forward_auth localhost:4180 {
        uri /oauth2/auth
    }
    proxy / localhost:8000
}
```

### Option 3: Disable the admin surface

Set `admin.enabled: false` in your config:

```json
"admin": { "enabled": false }
```

Requests to `/login`, `/admin`, and `/api/admin/*` return HTTP 404.

### Option 4: IP allowlist

Use a firewall or reverse proxy to whitelist admin IPs:

```nginx
location /admin {
    allow 203.0.113.0/24;    # office network
    deny all;
    proxy_pass http://localhost:8000;
}
```

## Environment variables

Never commit these to git; use your deployment platform's secrets management:

| Variable | Purpose | Example |
|----------|---------|---------|
| `ADMIN_PASSWORD` | Admin login password | `export ADMIN_PASSWORD="abc123xyz"` |
| `SECRET_KEY` | Signs session cookies | `export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"` |
| `PUBLIC_BASE_URL` | Public origin (for CSRF origin checks) | `https://example.com` |
| `FORCE_HSTS` | Enable `Strict-Transport-Security` header | `1` |
| `TRUST_PROXY_HEADERS` | Use `X-Forwarded-For` for client IP | `1` |
| `ADMIN_LOGIN_MAX_ATTEMPTS` | Brute-force limit: max login attempts | `5` |
| `ADMIN_LOGIN_LOCKOUT_SECONDS` | Brute-force lockout duration | `60` |

## Database security

### File permissions

If running on a shared system, protect the SQLite database:

```bash
chmod 600 data/honor.db
chmod 700 data/
```

### Backups

- Encrypt database backups in transit and at rest.
- Store backups in a secure, access-controlled location.
- Rotate old backups (e.g., keep last 30 days).

### Data retention

The portal does not implement automatic data expiration. If GDPR/CCPA compliance is needed, implement a manual deletion process:

```bash
# Delete all records for a specific student (by candidate_no)
sqlite3 data/honor.db "DELETE FROM achievements WHERE candidate_no = '12345';"

# Vacuum to reclaim space
sqlite3 data/honor.db "VACUUM;"
```

## Transport security

### TLS

Always use HTTPS in production. Obtain a certificate from a trusted CA:

- **Vercel**: Auto-provisions HTTPS via Let's Encrypt.
- **Docker + Nginx**: Use Certbot for Let's Encrypt or your CA's certificate.
- **Docker + Traefik**: Traefik auto-renews HTTPS.

### CSP (Content Security Policy)

Every HTML response includes a per-request nonce in the `Content-Security-Policy` header, preventing inline script injection:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123...'; ...
```

This blocks reflected XSS attacks. Stored XSS is not a risk because the portal only stores structured data (no user-submitted HTML).

### CORS

The portal does **not** expose CORS headers. Public surfaces are for human visitors, not API clients. If you need CORS, add it at the reverse proxy level.

## Input validation

### Student records (import)

- `candidate_no`, `name`, `school`, `subject_code`, `medal` are validated by the config schema.
- Missing or unrecognized competition/medal codes are rejected during import.
- The `data_mapping` prevents header injection; columns are mapped by name rather than by position.

### Search queries

- Search accepts any string (UTF-8).
- The query is used in a parameterized SQL `LIKE` clause, preventing SQL injection.
- Search results are filtered by the config schema (only existing competitions/years are shown).

### Form inputs (admin)

- The admin password form accepts any string.
- Passwords are compared with `hmac.compare_digest()` (constant-time).
- CSV import validates column names against `data_mapping` before processing rows.

## Logging and monitoring

### Sensitive data

- Passwords are **never** logged.
- Audit logs record action, IP, and timestamp without recording student names or details.
- Exception stack traces are logged at DEBUG level (not shown in production).

### Activity log

All admin actions are recorded in the `admin_activity` table:

- `admin.login.success` / `admin.login.failure`
- `achievement.add`
- `achievement.delete`

Query the log:

```bash
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity WHERE timestamp > datetime('now', '-1 day') ORDER BY timestamp DESC;"
```

## Known limitations

- **No data encryption at rest**: The SQLite database is stored as plaintext on disk. For highly sensitive data, apply filesystem-level encryption (LUKS, FileVault, or BitLocker).
- **No audit-log immutability**: An admin with database access can edit or delete the audit log. For compliance, implement a separate, append-only audit store (Cloudflare Logs, AWS CloudTrail, or similar).
- **Session duration**: Sessions are valid for the browser tab's lifetime. Consider adding an explicit session timeout (for example, 1 hour of inactivity) if needed.
- **No rate limiting on public endpoints**: Search, filter, and gallery views are unthrottled. For public portals with high traffic, implement rate limiting at the reverse proxy.

## Reporting security issues

If you discover a security vulnerability, please report it responsibly:

1. Do **not** open a public GitHub issue.
2. Email the maintainers privately via the repository's security policy (if published).
3. Include a detailed description, proof of concept, and suggested mitigation.

The maintainers will coordinate a fix and a responsible disclosure timeline.
