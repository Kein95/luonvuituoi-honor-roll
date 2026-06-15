"""``lvt-honor dev`` — run the honor-roll portal locally.

Builds the Flask app from ``honor.config.json`` in the current directory (or a
config path override) and serves it on ``--host`` / ``--port``.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Run the honor-roll portal locally.")
console = Console()


@app.callback(invoke_without_command=True)
def dev(
    config_path: Path = typer.Option(Path("honor.config.json"), "--config", "-c"),
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(5000, "--port", "-p"),
    debug: bool = typer.Option(False, "--debug", help="Enable Flask debug/auto-reload."),
) -> None:
    config_path = config_path.expanduser().resolve()
    if not config_path.exists():
        console.print(f"[red]ERR[/] config not found: {config_path}")
        console.print("  run [cyan]lvt-honor init <target>[/] first, then cd into it.")
        raise typer.Exit(code=1)

    project_root = config_path.parent
    from luonvuitoi_honor_cli.server import build_app

    flask_app = build_app(config_path, project_root)
    console.print(f"[green]▶[/] serving {config_path.parent.name} at http://{host}:{port}")
    console.print("  [dim]press Ctrl+C to stop[/]")
    flask_app.run(host=host, port=port, debug=debug)
