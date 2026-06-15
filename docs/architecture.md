# Architecture

LUONVUITUOI-HONOR ROLL is a config-driven monorepo, deliberately mirroring the structure of its sibling [LUONVUITUOI-CERT](https://github.com/Kein95/luonvuituoi-cert). The two share conventions so a contributor comfortable with one is comfortable with the other.

## Layered design

```mermaid
flowchart TD
    subgraph CLI["packages/cli (lvt-honor)"]
        APP["Flask app factory<br/>server/app.py"]
        CMDS["Commands<br/>init · import · seed · dev"]
    end
    subgraph CORE["packages/core (luonvuitoi_honor)"]
        UI["ui/<br/>Jinja2 renderers"]
        API["api/<br/>admin write surface"]
        QR["honorroll/<br/>query engine"]
        ING["ingest/<br/>CSV·Excel·JSON → rows"]
        STO["storage/<br/>SQLite schema"]
        CFG["config/<br/>Pydantic models + loader"]
    end
    DB[("SQLite<br/>achievements")]
    CMDS --> CORE
    APP --> UI & API
    UI --> QR
    API --> QR
    QR --> DB
    ING --> DB
    CFG -.validates.-> CORE
```

The core package stays **web-framework-agnostic**. Every handler is a pure function: take a `db_path` + filters, return dataclasses / rendered HTML. The Flask app factory in `cli/.../server/app.py` is a thin layer that calls these handlers and serialises results — no business logic in routes. This means a future serverless handler (Vercel, Cloud Run) reuses every pure function unchanged.

## Data model: one flat table

Unlike CERT (which keeps a table per round), the honor roll uses a **single flat `achievements` table** — one row per award. This is the natural unit: a student with three medals produces three rows, and every public listing is a single indexed `SELECT` with filters, not a fan-out across per-edition tables.

| column | purpose |
|--------|---------|
| `id` | autoincrement PK |
| `competition_id`, `year` | the edition (filter + label) |
| `candidate_no`, `name`, `school` | identity |
| `subject_code`, `medal`, `rank`, `percentile` | the award |
| `created_at` | ingest timestamp |

Indexes on `(competition_id, year, medal, subject_code)`, `name`, and `candidate_no` keep the filter + search queries fast.

## Config validation

`honor.config.json` is validated by Pydantic models with `extra="forbid"`. Cross-field invariants (editions reference declared competitions, every competition's medals exist in the global registry, IDs/codes/ranks are unique) live in `@model_validator` hooks on `HonorConfig`, so a malformed config fails loud at load time — never producing a half-rendered portal.

## Domain difference from CERT

| Aspect | CERT | HONOR ROLL |
|--------|------|------------|
| **Unit** | one student per round | one award (student × subject × medal) |
| **Store** | per-round tables | single flat `achievements` table |
| **Public output** | search → download PDF | filter → browse gallery |
| **Write surface** | admin issues/corrects certificates | admin adds/deletes achievements |
| **Signing** | RSA-PSS QR verify | none (publishing, not attestation) |

The shared conventions: config-driven, monorepo (`packages/core` + `packages/cli` + `examples`), pure-function core, thin Flask factory, CSP-nonce + security headers, i18n (EN + VI), and identical dev/deploy ergonomics (`lvt-*` CLI, Vercel + Docker).
