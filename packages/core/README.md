# luonvuitoi-honor

Config-driven student honor-roll **engine**: config validation, SQLite storage, ingest, query engine, Jinja2 UI, and the admin write API. Web-framework-agnostic. The `luonvuitoi-honor-cli` package wires it into Flask; a future serverless handler can reuse every pure function.

Install from the monorepo root:

```bash
pip install -e ./packages/core -e ./packages/cli
```

See the repo-root `README.md` for the full toolkit overview and `examples/demo-honor/` for a working project with real Demo Olympiad A 2025 data.
