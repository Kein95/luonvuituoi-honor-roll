"""``lvt-honor init``: scaffold a new honor-roll project.

Copies the packaged ``scaffolds/default/`` tree into ``<target>`` and renders
``.j2`` templates with the answers from an interactive Typer prompt (or defaults
when ``--non-interactive`` is passed). The rendered ``honor.config.json`` is
round-tripped through :class:`HonorConfig` so typos can't produce an invalid
project. Atomic staging: a validation failure leaves the target untouched.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from importlib import resources
from pathlib import Path

import typer
from jinja2 import Environment, StrictUndefined
from rich.console import Console

app = typer.Typer(help="Scaffold a new honor-roll project.")
console = Console()

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_SCAFFOLD_PACKAGE = "luonvuitoi_honor_cli.scaffolds.default"


def _slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s or "honor-roll"


def _iter_scaffold_files():
    root = resources.files(_SCAFFOLD_PACKAGE)

    def walk(node, prefix):
        for child in node.iterdir():
            if child.is_dir():
                yield from walk(child, prefix + (child.name,))
            else:
                yield ("/".join(prefix + (child.name,)), child)

    yield from walk(root, ())


def _ctx(name: str, slug: str, locale: str) -> dict[str, str]:
    return {"project_name": name, "project_slug": slug, "project_locale": locale}


@app.callback(invoke_without_command=True)
def init_project(
    target: Path = typer.Argument(..., help="Destination directory for the new project."),
    name: str | None = typer.Option(None, "--name", help="Project display name."),
    slug: str | None = typer.Option(None, "--slug", help="URL-safe slug (lowercase kebab-case)."),
    locale: str = typer.Option("vi", "--locale", help="Default UI locale (en | vi)."),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Skip prompts; rely on --name / --slug / --locale."
    ),
) -> None:
    target = target.expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        console.print(f"[red]ERR[/] {target} exists and is not empty.")
        raise typer.Exit(code=1)

    if not non_interactive:
        name = name or typer.prompt("Project display name", default="LUONVUITUOI HONOR ROLL")
        slug = slug or typer.prompt("URL slug (lowercase kebab-case)", default=_slugify(name))
        locale = typer.prompt("Default locale", default=locale)
    else:
        name = name or "LUONVUITUOI HONOR ROLL"
        slug = slug or _slugify(name)

    if not _SLUG_RE.match(slug):
        console.print(f"[red]ERR[/] slug {slug!r} must be lowercase kebab-case (e.g. ``demo-honor``).")
        raise typer.Exit(code=2)
    if locale not in ("en", "vi"):
        console.print(f"[red]ERR[/] locale must be 'en' or 'vi'; got {locale!r}.")
        raise typer.Exit(code=2)

    env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".lvt-honor-", dir=str(target.parent)))
    try:
        for relative, source in _iter_scaffold_files():
            dest = staging / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith(".j2"):
                rendered = env.from_string(source.read_text(encoding="utf-8")).render(
                    _ctx(name, slug, locale)
                )
                dest.with_suffix("").write_text(rendered, encoding="utf-8")
            else:
                with source.open("rb") as src, dest.open("wb") as out:
                    shutil.copyfileobj(src, out)

        from luonvuitoi_honor.config import load_config

        try:
            load_config(staging / "honor.config.json")
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]ERR[/] rendered config failed validation: {e}")
            raise typer.Exit(code=3) from e

        if target.exists():
            target.rmdir()
        os.rename(staging, target)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    console.print(f"[green]OK[/] scaffolded {name!r} into {target}")
    console.print(
        "  next: [cyan]cd[/] into the project, then [cyan]lvt-honor import[/] and [cyan]lvt-honor dev[/]"
    )
