"""``lvt-honor import-teams`` — load team/group awards from a JSON file.

Reads ``honor.config.json``, reads a JSON list of team objects, validates each
team's ``award`` against the config's ``team_awards`` registry, and writes them
into ``data/<slug>.db`` for the given ``--competition`` + ``--year`` edition.
``--replace`` first deletes that edition's existing teams so re-imports are idempotent.

Team JSON shape::

    [
      {"name": "Team A", "award": "CHAMPION", "subject": "MATH", "category": "Lower Secondary",
       "members": [{"name": "...", "grade": "...", "school": "..."}]}
    ]
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Import team/group awards from a JSON file.")
console = Console()


@app.callback(invoke_without_command=True)
def import_teams(
    source: Path = typer.Argument(..., help="Team JSON file."),
    competition: str = typer.Option(..., "--competition", "-C", help="competition_id from config."),
    year: int = typer.Option(..., "--year", "-y", help="Edition year."),
    config_path: Path = typer.Option(Path("honor.config.json"), "--config", "-c"),
    db_path: Path | None = typer.Option(None, "--db", help="SQLite path (default: data/<slug>.db)."),
    replace: bool = typer.Option(False, "--replace", help="Delete existing teams for this edition first."),
) -> None:
    from luonvuitoi_honor.config import load_config
    from luonvuitoi_honor.ingest import ingest_teams, read_teams_file, replace_teams_edition

    try:
        config = load_config(config_path)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]ERR[/] can't load config {config_path}: {e}")
        raise typer.Exit(code=1) from e

    if not config.team_awards:
        console.print(
            "[yellow]![/] config has no 'team_awards' registry — teams import will store rows, "
            "but the All-Star Teams page only shows once you declare team_awards."
        )
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
        teams = read_teams_file(source)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]ERR[/] failed to read {source}: {e}")
        raise typer.Exit(code=3) from e

    if replace:
        n = replace_teams_edition(out, competition_id=competition, year=year)
        console.print(f"[dim]replaced {n} existing teams for {competition} {year}[/]")

    result = ingest_teams(config, out, competition_id=competition, year=year, teams=teams)
    console.print(
        f"[green]OK[/] imported {result.rows_inserted} teams "
        f"(skipped {result.rows_skipped}) for {competition} {year} -> {out}"
    )
    if result.warnings:
        for w in result.warnings[:8]:
            console.print(f"  [yellow]![/] {w}")
