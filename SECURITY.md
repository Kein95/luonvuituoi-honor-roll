# Security Policy

## Supported versions

LUONVUITUOI-HONOR ROLL follows semantic versioning. The latest minor release of the current major branch receives security fixes.

| Version | Supported |
|---------|-----------|
| 0.x     | ✓ (pre-1.0; APIs may change) |
| < 0.1   | ✗         |

## Reporting a vulnerability

If you believe you've found a vulnerability in LUONVUITUOI-HONOR ROLL:

- **Do not** open a public GitHub issue.
- Email the maintainers at [htkien95@gmail.com](mailto:htkien95@gmail.com), or open a draft **private security advisory** via the GitHub repository's Security tab.
- Include reproduction steps, the affected version, and any proof-of-concept material you have.

We aim to acknowledge reports within 72 hours and to ship a fix or mitigation within 30 days for critical issues. You'll be credited in the advisory unless you request otherwise.

## Threat model

LUONVUITUOI-HONOR ROLL is a public-facing honor-roll portal. The design assumptions:

- **Config author is trusted.** The operator writes `honor.config.json`. We validate competition IDs, medal codes, hex colors, and slug formats defensively (Pydantic `extra="forbid"`), but we do not protect against a malicious operator who controls the config file.
- **Visitors are untrusted.** The public read surface (`/`, `/search`, `/hall-of-fame`, `/teams`, `/api/stats`, `/api/search`) is read-only and parameterised — registry codes are validated to safe identifiers, so even the medal-ordering `CASE` clause cannot be injected. The admin surface (`/admin` + `/api/admin/*`) is gated by a password login (`ADMIN_PASSWORD`) and stays locked until that env var is set; serve it over HTTPS.
- **No PII is collected beyond what the operator ingests.** The achievements table holds name + school + medal — no DOB, phone, or email by default.

Out-of-scope:

- **Admin auth is a single shared password.** `/admin` and the write API require login with `ADMIN_PASSWORD` (constant-time compared) via a signed-cookie session (`SECRET_KEY`); `SameSite=Lax` mitigates CSRF. There are no per-user accounts or roles. Always serve over HTTPS so the session cookie isn't exposed.
- Denial of service via costly renders (the listing is capped at `limit=2000`; beyond that a resource-exhaustion attack succeeds at the platform level).
- Supply-chain compromise of `pydantic`, `flask`, `pandas`, or `jinja2`. Pin dependencies in your deployment's lockfile.

## Hardening checklist

Before exposing a deployment publicly:

1. Set a strong `ADMIN_PASSWORD` and a long random `SECRET_KEY`. Without `ADMIN_PASSWORD`, admin stays locked; set `admin.enabled: false` to remove the surface entirely.
2. Set `PUBLIC_BASE_URL` to the exact HTTPS origin, and `ALLOWED_ORIGINS` if other origins call `/api/*`.
3. Serve over HTTPS (terminate TLS at the platform or a reverse proxy). Set `FORCE_HSTS=1`, and `TRUST_PROXY_HEADERS=1` when behind a proxy (Nginx / Caddy / Vercel).
4. Review the achievements you ingest — names, grades, schools, and photos are published publicly. Do not ingest data you're not authorised to publish.
5. Keep the SQLite DB file (`data/<slug>.db`) out of any public web root; it's bind-mounted inside the container and never served over HTTP.
