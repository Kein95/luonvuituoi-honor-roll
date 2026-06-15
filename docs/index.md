# LUONVUITUOI-HONOR ROLL

> Config-driven student honor-roll toolkit. Bring your results CSV/Excel/JSON + a config → ship a public honor roll (cards + table + stats), a student search, and an admin management surface to Vercel or Docker in an afternoon.

Sibling project of [**LUONVUITUOI-CERT**](https://github.com/Kein95/luonvuituoi-cert) — the certificate portal toolkit. Where CERT *issues and verifies* PDFs, HONOR ROLL **publishes and celebrates** the achievements.

## Why

You ran a competition (Demo Olympiad A, Demo Olympiad B, a school olympiad…) and now have a spreadsheet of medal winners. You need:

- A **public honor roll** where students, parents, and schools see the achievements, styled like a real award gallery.
- A **student search** so anyone can look up a name and see every medal they've earned across editions.
- An **admin surface** to add/correct/delete entries without touching files.

This toolkit ships all three — config-driven, zero-code.

## Features

- :material-trophy: **Multi-competition / multi-year** — one config declares every competition, its subjects, and the editions you've run.
- :material-medal: **Global medal registry** — define each medal once (rank, EN/VI label, color, icon); badges stay consistent everywhere.
- :material-magnify: **Three surfaces** — honor roll, student search, admin.
- :material-file-import: **Flexible ingest** — CSV / Excel / JSON, mapped through `data_mapping`.
- :material-cellphone-link: **Animated, responsive UI** — desktop, tablet, mobile.
- :material-translate: **i18n** — English + Vietnamese.
- :material-rocket-launch: **Deploy-ready** — Vercel or Docker.

## Reference demo

`examples/demo-honor/` ships with the real **Demo Olympiad A 2025** results (66 awards across MATHS / ENGLISH / SCIENCE).

```bash
cd examples/demo-honor
python prepare_demo.py
lvt-honor import data/demo-2025.json --competition demo-a --year 2025 --replace
lvt-honor dev
```

## Quick links

- [:material-fast-forward: Quickstart](quickstart.md)
- [:material-cog: Configuration reference](config-reference.md)
- [:material-sitemap: Architecture](architecture.md)
- [:material-cloud: Deploy on Vercel](deploy-vercel.md) · [:material-docker: Deploy on Docker](deploy-docker.md)
