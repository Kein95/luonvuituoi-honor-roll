# Contributing to LUONVUITUOI-HONOR ROLL

Thanks for taking an interest. This project is a small-surface toolkit. The bar for new features is whether you would want it in your own deploy tomorrow. If yes, read on.

## Dev setup

```bash
git clone https://github.com/Kein95/luonvuituoi-honor-roll
cd luonvuituoi-honor-roll
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ./packages/core[dev] -e ./packages/cli
```

Run the full suite:

```bash
pytest -ra
```

Run only the fast unit tests (skip the Flask E2E suite):

```bash
pytest -m "not e2e"
```

From a source checkout without `pip install -e`, the root `conftest.py` puts both packages on `sys.path`, so `pytest` works directly.

Lint + type-check:

```bash
ruff check packages scripts
ruff format --check packages scripts
mypy packages/core/luonvuitoi_honor packages/cli/luonvuitoi_honor_cli
```

Re-export the JSON schema after editing `luonvuitoi_honor/config/models.py`:

```bash
python scripts/export_schema.py
```

The `test_schema_in_sync_with_models` test fails if you forget.

## Conventions

- **Config-driven over code.** A new capability belongs in `honor.config.json` + a Pydantic model, not a hardcoded constant. Operators should be able to enable/disable it without editing Python.
- **Pure functions in `core/`.** The engine stays web-framework-agnostic. The Flask app factory (`cli/.../server/app.py`) is a thin layer that calls pure handlers and serializes results without any business logic in routes.
- **Cross-field invariants live in `@model_validator`** on `HonorConfig`, so a malformed config fails loud at load time rather than producing a half-rendered portal.
- **Tests mirror the module under test.** `config/models.py` → `tests/test_config_models.py`. E2E coverage (Flask test client) lives under `tests/e2e/` and is marked `e2e` so it can be skipped in the fast loop.

## Sibling project

This toolkit mirrors the architecture of [**LUONVUITUOI-CERT**](https://github.com/Kein95/luonvuituoi-cert) (certificate portal). When in doubt about a convention, check how CERT does it. The two should feel like one codebase.
