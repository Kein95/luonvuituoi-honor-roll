# Deploy on Vercel

The scaffolded project includes an `api/index.py` that Vercel's `@vercel/python` runtime mounts as the WSGI app.

## 1. Scaffold + import locally

```bash
lvt-honor init my-awards --non-interactive
cd my-awards
lvt-honor import results.csv --competition demo-a --year 2025 --replace
```

The `data/<slug>.db` is committed alongside the config for Vercel to serve. (For large rollouts, swap SQLite for a hosted database; the query engine accepts a `db_path`, so a connection-pool adapter represents a small change.)

## 2. Deploy

```bash
npm i -g vercel
vercel deploy
```

Vercel detects the `api/index.py` entrypoint automatically. Set environment variables in the Vercel dashboard:

| Variable | Purpose |
|----------|---------|
| `PUBLIC_BASE_URL` | Your `https://<project>.vercel.app` origin |
| `FORCE_HSTS` | `1` (Vercel terminates TLS) |

## 3. Verify

```bash
curl https://<project>.vercel.app/health
# → {"ok":true}
```

## Notes

- **Admin surface**: Vercel deploys are public by default. Gate `/admin` behind Vercel's password protection (Pro plan) or set `admin.enabled: false` in the config.
- **Cold starts**: the first request after idle spins up the serverless function (~200ms). The `/health` endpoint is dependency-free for fast probes.
