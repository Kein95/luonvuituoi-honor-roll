"""Entry point for the ``lvt-honor`` console script.

Each command module exposes a single ``run`` function; we register them as
top-level Typer commands so positional args (e.g. ``lvt-honor init <target>``)
resolve as expected.
"""

from __future__ import annotations

import typer
from rich.console import Console

from . import __version__
from .commands import dev, import_data, import_teams, init, seed

console = Console()

app = typer.Typer(
    name="lvt-honor",
    help="LUONVUITUOI-HONOR ROLL — scaffold, seed, import, and run student honor-roll portals.",
    no_args_is_help=True,
    add_completion=False,
)

app.command(name="init", help="Scaffold a new honor-roll project.")(init.init_project)
app.command(name="seed", help="Generate fake achievements for local testing.")(seed.seed)
app.command(name="import", help="Import achievements from CSV/Excel/JSON.")(import_data.import_data)
app.command(name="import-teams", help="Import team/group awards from JSON.")(import_teams.import_teams)
app.command(name="dev", help="Run the honor-roll portal locally.")(dev.dev)


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit."),
) -> None:
    if version:
        console.print(f"lvt-honor [bold cyan]{__version__}[/]")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":  # pragma: no cover
    app()
