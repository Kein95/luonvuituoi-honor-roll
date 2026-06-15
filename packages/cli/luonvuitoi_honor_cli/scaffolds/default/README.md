# {{ project_name }}

A student honor-roll portal scaffolded by `lvt-honor`.

## Quickstart

```bash
pip install -r requirements.txt
lvt-honor import <your-results.csv> --competition demo-a --year 2025 --replace
lvt-honor dev
# → http://127.0.0.1:5000
```

## Files

- `honor.config.json` — the whole portal config (competitions, medals, editions, display).
- `data/` — the SQLite store (`{{ project_slug }}.db`) is created on first import/seed.
- `api/index.py` — Vercel serverless entrypoint.

## Data format

Each source row (CSV/Excel/JSON) maps via `data_mapping` in the config.
Minimal columns: `name`, `medal`. Optional: `candidate_no`, `school`, `rank`, `subject`, `percentile`.

## Deploy

- **Vercel** — `vercel deploy` (uses `api/index.py`).
- **Docker** — build from the repo-root `Dockerfile`.
