"""``lvt-honor import``: load achievements from a CSV/Excel/JSON source file.

Reads ``honor.config.json``, reads the source file, projects rows through the
config's ``data_mapping``, and writes them into ``data/<slug>.db`` for the given
``--competition`` + ``--year`` edition. ``--replace`` first deletes that
edition's existing rows so re-imports are idempotent.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Import achievements from CSV/Excel/JSON.")
console = Console()


@app.callback(invoke_without_command=True)
def import_data(
    source: Path = typer.Argument(..., help="Source file (.csv / .xlsx / .json)."),
    competition: str = typer.Option(..., "--competition", "-C", help="competition_id from config."),
    year: int = typer.Option(..., "--year", "-y", help="Edition year."),
    config_path: Path = typer.Option(Path("honor.config.json"), "--config", "-c"),
    db_path: Path | None = typer.Option(None, "--db", help="SQLite path (default: data/<slug>.db)."),
    replace: bool = typer.Option(False, "--replace", help="Delete existing rows for this edition first."),
    header_row: int = typer.Option(0, "--header-row", help="0-indexed header row (CSV/Excel)."),
) -> None:
    from luonvuitoi_honor.config import load_config
    from luonvuitoi_honor.ingest import ingest_rows, read_file, replace_edition

    try:
        config = load_config(config_path)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]ERR[/] can't load config {config_path}: {e}")
        raise typer.Exit(code=1) from e

    if not any(c.id == competition for c in config.competitions):
        console.print(
            f"[red]ERR[/] --competition {competition!r} not in config "
            f"(available: {[c.id for c in config.competitions]})"
        )
        raise typer.Exit(code=2)

    source = source.expanduser().resolve()
    if not source.exists():
        console.print(f"[red]ERR[/] source file not found: {source}")
        raise typer.Exit(code=1)

    out = (db_path or Path("data") / f"{config.project.slug}.db").expanduser().resolve()
    try:
        rows = read_file(source, header_row=header_row)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]ERR[/] failed to read {source}: {e}")
        raise typer.Exit(code=3) from e

    if replace:
        n = replace_edition(out, competition_id=competition, year=year)
        console.print(f"[dim]replaced {n} existing rows for {competition} {year}[/]")

    result = ingest_rows(config, out, competition_id=competition, year=year, rows=rows)
    console.print(
        f"[green]OK[/] imported {result.rows_inserted} achievements "
        f"(skipped {result.rows_skipped}) for {competition} {year} -> {out}"
    )
    if result.warnings:
        for w in result.warnings[:8]:
            console.print(f"  [yellow]![/] {w}")
        if len(result.warnings) > 8:
            console.print(f"  [dim]…and {len(result.warnings) - 8} more warnings[/]")
