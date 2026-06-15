"""``lvt-honor seed`` — generate fake achievements for local testing.

Reads ``honor.config.json`` from the current directory, invents ``--count``
achievements across the declared competitions/editions with Faker, and writes
them to ``data/<slug>.db``. Not intended for production data.
"""

from __future__ import annotations

import random
import secrets as _secrets
from pathlib import Path

import typer
from faker import Faker
from rich.console import Console

app = typer.Typer(help="Generate fake achievements for local testing.")
console = Console()

_SCHOOLS = ["School"]


@app.callback(invoke_without_command=True)
def seed(
    count: int = typer.Option(60, "--count", "-n", min=1, max=10_000, help="Number of fake achievements."),
    config_path: Path = typer.Option(Path("honor.config.json"), "--config", "-c"),
    db_path: Path | None = typer.Option(None, "--db", help="SQLite output path (default: data/<slug>.db)."),
    locale: str = typer.Option("en_US", help="Faker locale (e.g. en_US, vi_VN)."),
    seed_value: int | None = typer.Option(None, "--seed", help="Deterministic seed for reproducible output."),
) -> None:
    from luonvuitoi_honor.config import load_config
    from luonvuitoi_honor.ingest import ingest_rows

    try:
        config = load_config(config_path)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]ERR[/] can't load config {config_path}: {e}")
        raise typer.Exit(code=1) from e

    rng = random.Random(seed_value) if seed_value is not None else random.Random(_secrets.randbits(64))
    fake = Faker(locale)
    if seed_value is not None:
        Faker.seed(seed_value)

    out = (db_path or Path("data") / f"{config.project.slug}.db").expanduser().resolve()
    by_edition: dict[tuple[str, int], list[str]] = {}
    for ed in config.editions:
        comp = next(c for c in config.competitions if c.id == ed.competition_id)
        by_edition[(ed.competition_id, ed.year)] = comp.medals

    # Bucket rows by edition: ingest_rows binds a whole call to one (competition, year),
    # so each edition's rows must be ingested in their own call (else all rows land in one).
    buckets: dict[tuple[str, int], list[dict]] = {}
    for _ in range(count):
        (competition_id, year), medals = rng.choice(list(by_edition.items()))
        comp = next(c for c in config.competitions if c.id == competition_id)
        subject_code = rng.choice([s.code for s in comp.subjects]) if comp.subjects else ""
        buckets.setdefault((competition_id, year), []).append(
            {
                "name": fake.name(),
                "grade": f"Grade {rng.randint(1, 12)}",
                "school": rng.choice(_SCHOOLS),
                "medal": rng.choice(medals),
                "subject": subject_code,
                "rank": str(rng.randint(1, 120)),
                "candidate_no": f"S{rng.randint(10000, 99999)}",
            }
        )

    total = 0
    for (competition_id, year), rows in buckets.items():
        total += ingest_rows(config, out, competition_id=competition_id, year=year, rows=rows).rows_inserted
    console.print(f"[green]OK[/] seeded {total} achievements across {len(buckets)} edition(s) -> {out}")
