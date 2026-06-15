# Deploy on Docker

The repo-root `Dockerfile` + `docker-compose.yml` build a non-root image serving the portal via gunicorn on port 8000.

## 1. Prepare the project directory

The container bind-mounts `./project` to `/app/project`, so place your `honor.config.json` + `data/` there:

```
project/
├── honor.config.json
└── data/
    └── <slug>.db      # created by lvt-honor import
```

You can generate these on the host (no Python needed inside the container):

```bash
mkdir -p project/data
# ... copy your honor.config.json + the seeded data/<slug>.db into project/ ...
```

## 2. Build + run

```bash
cp .env.example .env      # set PUBLIC_BASE_URL
docker compose up -d --build
```

## 3. Verify

```bash
curl http://localhost:8000/health
# → {"ok":true}
```

Open `http://localhost:8000` for the honor roll, `/search`, and `/admin`.

## Notes

- **Non-root**: the container runs as a `app:app` system user.
- **Healthcheck**: probes `/health` (dependency-free) every 30s.
- **Single worker**: `WEB_CONCURRENCY=1` because the default SQLite store isn't multi-process safe. To scale horizontally, move the store to a shared host and bump `WEB_CONCURRENCY`.
- **Editing config**: change `project/honor.config.json` on the host and `docker compose restart` — no rebuild needed.
- **Admin surface**: put the container behind a reverse proxy (Nginx / Caddy / Traefik) with TLS + auth before exposing `/admin` publicly.
