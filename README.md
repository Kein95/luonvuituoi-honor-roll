<div align="center">

# 🏆 LUONVUITUOI-HONOR ROLL

**Config-driven student honor-roll toolkit.**
Bring your results CSV/Excel/JSON + one config → ship a bilingual award gallery, student search, an all-time Hall of Fame, team awards, and a password-protected admin to Vercel or Docker in an afternoon.

[![Live Demo](https://img.shields.io/badge/Live_Demo-honor--roll-2ea44f?style=for-the-badge&logo=vercel&logoColor=white)](https://honor-roll.luonvuituoi.work)
[![Tests](https://img.shields.io/github/actions/workflow/status/Kein95/luonvuituoi-honor-roll/test.yml?style=for-the-badge&label=tests&logo=github)](https://github.com/Kein95/luonvuituoi-honor-roll/actions/workflows/test.yml)
&nbsp;

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-server-000000?style=flat-square&logo=flask&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Bilingual](https://img.shields.io/badge/UI-VI%20%2F%20EN-0ea5e9?style=flat-square)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

### [🔴 Live demo →](https://honor-roll.luonvuituoi.work) &nbsp;·&nbsp; [🥇 Hall of Fame](https://honor-roll.luonvuituoi.work/hall-of-fame) &nbsp;·&nbsp; [🔍 Search](https://honor-roll.luonvuituoi.work/search) &nbsp;·&nbsp; [🤝 Teams](https://honor-roll.luonvuituoi.work/teams) &nbsp;·&nbsp; [🔐 Admin](https://honor-roll.luonvuituoi.work/login)

</div>

---

Sibling project of [**LUONVUITUOI-CERT**](https://github.com/Kein95/luonvuituoi-cert), the certificate portal toolkit. Where CERT issues and verifies PDFs, HONOR ROLL **publishes and celebrates** the achievements.

## 💡 Why

You ran a competition (a math olympiad, a science challenge, a school contest, and so on) and now have a spreadsheet of medal winners. You need:

- A **public honor roll** where students, parents, and schools see the achievements, filterable by competition / year / medal / subject / school, styled like a real award gallery.
- A **student search** so anyone can look up a name and see every medal they've earned across editions.
- An **admin surface** to add / correct / delete entries without touching files.

LUONVUITUOI-HONOR ROLL ships these and more, config-driven and zero-code, deployable to Vercel's free tier or a Docker host.

## ✨ Features

- **🌏 Bilingual UI (VI / EN)**: Auto-detects the browser language, with a manual VI|EN toggle remembered via cookie. Project name, labels, medals, subjects, and taglines all switch.
- **🖥️ Public surfaces**: Honor roll (`/`), student search (`/search`), **Hall of Fame** (`/hall-of-fame`, all-time top achievers across editions), and **All-Star Teams** (`/teams`, group/team awards).
- **🎓 Student cards**: Photo avatar, grade, school, medal badge. Click a card for a detail popup listing all of that student's awards, with a one-click **PNG download** (rounded "certificate" image). A whole-board PNG export is one click away too.
- **🎛️ Filters & facets**: Competition, year, medal, subject, and school, plus a stat dashboard and medal legend.
- **🗓️ Multi-competition / multi-year**: One config declares every competition, their subjects, and the editions (competition + year). A global medal registry (rank, EN/VI label, color, icon) keeps badges consistent everywhere. Upcoming editions show a friendly "coming soon" banner.
- **🔐 Password-protected admin**: A separate `/login` page gates `/admin` and the write API; credentials come from environment variables only. Hardened with login rate-limiting, CSRF tokens, and an audit log.
- **📥 Flexible ingest**: CSV / Excel / JSON for achievements, JSON for teams, mapped through `data_mapping` so a renamed column needs only a config edit.
- **🚀 Deploy-ready & hardened**: Vercel serverless (`api/index.py`) or Docker (`wsgi.py`); optional HSTS, proxy-header trust, and CORS allow-listing via environment variables.

## ⚡ Quickstart

```bash
git clone https://github.com/Kein95/luonvuituoi-honor-roll
cd luonvuituoi-honor-roll
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ./packages/core -e ./packages/cli

lvt-honor init my-awards
cd my-awards
lvt-honor import results.csv --competition demo-a --year 2025 --replace
lvt-honor dev                             # http://localhost:5000
```

## 🎬 Reference demo

The `examples/demo-honor/` project ships with **synthetic placeholder data** (anonymized students X/Y/Z, schools labeled "School") so you can explore every surface without any real personal data:

```bash
cd examples/demo-honor
python prepare_demo.py                                                   # generates data/demo-2025.json + data/demo-teams-2025.json
lvt-honor import data/demo-2025.json --competition demo-a --year 2025 --replace
lvt-honor import-teams data/demo-teams-2025.json --competition demo-a --year 2025 --replace
lvt-honor dev                                                            # http://localhost:5000
```

> 👉 Or just open the **[live demo](https://honor-roll.luonvuituoi.work)** if you prefer to explore it without setup.

## 🛠️ CLI

| Command | What it does |
|---|---|
| `lvt-honor init <dir>` | Scaffold a new project (atomic, config validated on write). |
| `lvt-honor import <file>` | Load achievements from CSV / Excel / JSON (`--replace` for idempotent re-import). |
| `lvt-honor import-teams <file.json>` | Load team / group awards. |
| `lvt-honor seed --count N` | Generate fake achievements for local preview. |
| `lvt-honor dev` | Run the portal locally (Flask, per-request CSP nonce + security headers). |

## ⚙️ Config at a glance

`honor.config.json` is the whole portal; see `honor.schema.json` for the full typed reference.

```jsonc
{
  "project": { "name": "Bảng Vinh Danh", "name_en": "Honor Roll", "slug": "…", "locale": "vi", "tagline": "…", "tagline_en": "…" },
  "competitions": [
    { "id": "demo-a", "subjects": [{ "code": "MATH", "icon": "🔢" }], "medals": ["GOLD","SILVER"] }
  ],
  "editions": [
    { "competition_id": "demo-a", "year": 2025, "label": "…" },
    { "competition_id": "demo-a", "year": 2026, "label": "…", "upcoming": true }
  ],
  "medals": { "GOLD": { "rank": 1, "label_en": "Gold", "label_vi": "Huy chương Vàng", "color": "#FFD700", "icon": "🥇" } },
  "team_awards": { "CHAMPION": { "rank": 1, "label_en": "Champion", "label_vi": "Vô địch", "color": "#FFD700", "icon": "🏆" } },
  "data_mapping": { "name_col": "name", "grade_col": "grade", "photo_col": "photo", "medal_col": "medal" },
  "display": { "layout": "both", "cards_per_row": 4 },
  "contact": { "email": "…", "repo_url": "https://github.com/you/your-honor-roll" }
}
```

## ☁️ Deploy

- **Vercel**: Run `vercel deploy` against the scaffolded `api/index.py`.
- **Docker**: Run `docker compose up -d` against the repo-root `wsgi.py`.

Environment variables (set in your host / `.env`, never committed):

| Var | Purpose |
|---|---|
| `ADMIN_PASSWORD` | Enables admin login. Unset = admin stays locked. |
| `SECRET_KEY` | Signs the session cookie (set a long random value in production). |
| `ADMIN_LOGIN_MAX_ATTEMPTS` / `ADMIN_LOGIN_LOCKOUT_SECONDS` | Login brute-force guard (defaults 5 / 60s). |
| `PUBLIC_BASE_URL` | Canonical origin for `<link rel=canonical>` and `og:url`. |
| `ALLOWED_ORIGINS` | Comma-separated CORS allow-list for `/api/*` (`*` for any). |
| `FORCE_HSTS` | `1` to emit `Strict-Transport-Security` (HTTPS only). |
| `TRUST_PROXY_HEADERS` | `1` behind a reverse proxy (Nginx, Caddy, or Vercel). |

## 📁 Repo layout

```text
packages/
  core/    # luonvuitoi-honor: engine (config, storage, ingest, queries, ui, api)
  cli/     # luonvuitoi-honor-cli: lvt-honor scaffolder + Flask dev server
examples/
  demo-honor/   # full-feature reference project (synthetic data)
```

## 📫 Contact

- **Email**: [htkien95@gmail.com](mailto:htkien95@gmail.com)
- **GitHub**: [@Kein95](https://github.com/Kein95)

## 📄 License

MIT © LUONVUITUOI-HONOR ROLL contributors.
