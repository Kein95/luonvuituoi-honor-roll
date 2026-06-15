"""CLI smoke tests: ``lvt-honor init`` scaffolds a valid project, every command imports.

These don't shell out to ``lvt-honor``; they call the Typer app in-process via
``typer.testing.CliRunner`` so failures surface as Python tracebacks (faster,
clearer) and exercise the real code paths the console script binds.
"""

from __future__ import annotations

from pathlib import Path

from luonvuitoi_honor_cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "lvt-honor" in result.stdout


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    # Typer's no_args_is_help prints help and exits 2 (its standard "usage"
    # exit code). The point of this test is that the command list is shown.
    assert result.exit_code in (0, 2)
    assert "init" in (result.stdout + (result.output or ""))
    assert "dev" in (result.stdout + (result.output or ""))


def test_init_scaffolds_valid_project(tmp_path: Path) -> None:
    target = tmp_path / "my-roll"
    result = runner.invoke(
        app,
        [
            "init",
            str(target),
            "--name",
            "My Roll",
            "--slug",
            "my-roll",
            "--locale",
            "vi",
            "--non-interactive",
        ],
    )
    assert result.exit_code == 0, result.stdout
    # Files present
    assert (target / "honor.config.json").exists()
    assert (target / "api" / "index.py").exists()
    assert (target / "requirements.txt").exists()
    # Config round-trips through validation
    from luonvuitoi_honor.config import load_config

    cfg = load_config(target / "honor.config.json")
    assert cfg.project.name == "My Roll"
    assert cfg.project.locale == "vi"


def test_init_refuses_non_empty_target(tmp_path: Path) -> None:
    target = tmp_path / "occupied"
    target.mkdir()
    (target / "blocker.txt").write_text("x", encoding="utf-8")
    result = runner.invoke(app, ["init", str(target), "--non-interactive"])
    assert result.exit_code == 1


def test_init_rejects_bad_slug(tmp_path: Path) -> None:
    target = tmp_path / "x"
    result = runner.invoke(app, ["init", str(target), "--slug", "BAD SLUG", "--non-interactive"])
    assert result.exit_code == 2


def test_init_rejects_bad_locale(tmp_path: Path) -> None:
    target = tmp_path / "x"
    result = runner.invoke(app, ["init", str(target), "--locale", "fr", "--non-interactive"])
    assert result.exit_code == 2


def test_seed_creates_db(tmp_path: Path) -> None:
    # Scaffold first, then seed.
    target = tmp_path / "r"
    runner.invoke(app, ["init", str(target), "--non-interactive"])
    cfg_file = target / "honor.config.json"
    result = runner.invoke(
        app,
        ["seed", "--count", "40", "--config", str(cfg_file), "--db", str(target / "s.db"), "--seed", "42"],
    )
    assert result.exit_code == 0, result.stdout
    assert (target / "s.db").exists()
    from luonvuitoi_honor.config import load_config
    from luonvuitoi_honor.honorroll import stats

    s = stats(load_config(cfg_file), target / "s.db")
    assert s["total_achievements"] >= 1
    # Rows must spread across the scaffold's editions, not all land in one (regression guard).
    assert len(s["editions"]) >= 2
