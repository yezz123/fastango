from pathlib import Path

import pytest
import typer
from pytest import MonkeyPatch
from rich.prompt import Confirm, Prompt
from typer.testing import CliRunner

import fastango.cli as cli
from fastango.cli import app
from fastango.generator.model_catalog import available_models
from fastango.scaffold.config import ProjectConfig
from fastango.terminal.models import models_table

runner = CliRunner()


def test_cli_lists_integrations() -> None:
    result = runner.invoke(app, ["integrations"])

    assert result.exit_code == 0
    assert "authx" in result.stdout
    assert "stripe" in result.stdout


def test_cli_create_dry_run() -> None:
    result = runner.invoke(app, ["create", "demo-api", "--no-interactive", "--dry-run"])

    assert result.exit_code == 0
    assert "Dry run complete" in result.stdout
    assert "pyproject.toml" in result.stdout


def test_cli_filters_integrations_by_category() -> None:
    result = runner.invoke(app, ["integrations", "--category", "database"])

    assert result.exit_code == 0
    assert "postgres" in result.stdout
    assert "sqlite" in result.stdout


def test_cli_lists_presets_as_json() -> None:
    result = runner.invoke(app, ["integrations", "--presets", "--json"])

    assert result.exit_code == 0
    assert "api-starter" in result.stdout
    assert "saas" in result.stdout


def test_cli_create_with_preset_dry_run() -> None:
    result = runner.invoke(
        app,
        ["create", "demo-api", "--preset", "saas", "--no-interactive", "--dry-run"],
    )

    assert result.exit_code == 0
    assert "app/auth.py" in result.stdout
    assert "app/stripe_routes.py" in result.stdout


def test_cli_no_args_launches_playground(monkeypatch: MonkeyPatch) -> None:
    called = False

    def fake_launch_playground(**_: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "launch_playground", fake_launch_playground)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert called is True


def test_cli_generate_dry_run() -> None:
    result = runner.invoke(app, ["generate", "a starter MVP", "--dry-run", "--yes"])

    assert result.exit_code == 0
    assert "Dry run complete" in result.stdout
    assert "app/core/security.py" in result.stdout


def test_cli_generate_json_dry_run() -> None:
    result = runner.invoke(app, ["generate", "AI SaaS with vector search", "--dry-run", "--json"])

    assert result.exit_code == 0
    assert '"skills"' in result.stdout
    assert "ai-api" in result.stdout


def test_cli_lists_supported_models() -> None:
    result = runner.invoke(app, ["models", "--provider", "anthropic", "--static", "--json"])

    assert result.exit_code == 0
    assert "claude-3-5-haiku-latest" in result.stdout


def test_cli_rejects_model_without_provider() -> None:
    result = runner.invoke(
        app,
        ["generate", "starter MVP", "--model", "gpt-4.1-mini", "--dry-run"],
    )

    assert result.exit_code == 1
    assert "--model can only be used" in result.stdout


def test_version_callback_prints_and_exits() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "fastango" in result.stdout


def test_launch_playground_cancel(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "run_playground", lambda **_: None)

    with pytest.raises(typer.Exit):
        cli.launch_playground(output_dir=tmp_path, dry_run=False, force=False)


def test_launch_playground_dry_run(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    config = ProjectConfig(project_name="demo", output_dir=tmp_path)
    monkeypatch.setattr(cli, "run_playground", lambda **_: config)

    cli.launch_playground(output_dir=tmp_path, dry_run=True, force=False)


def test_launch_playground_writes_project(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    config = ProjectConfig(project_name="demo", output_dir=tmp_path)
    monkeypatch.setattr(cli, "run_playground", lambda **_: config)

    cli.launch_playground(output_dir=tmp_path, dry_run=False, force=False)

    assert (tmp_path / "demo" / "pyproject.toml").exists()


def test_playground_command_delegates(monkeypatch: MonkeyPatch) -> None:
    called: dict[str, bool] = {}

    def fake_launch_playground(**_: object) -> None:
        called["ok"] = True

    monkeypatch.setattr(cli, "launch_playground", fake_launch_playground)

    result = runner.invoke(app, ["playground", "--dry-run"])

    assert result.exit_code == 0
    assert called["ok"] is True


def test_models_cli_table_branch() -> None:
    result = runner.invoke(app, ["models", "--provider", "openai", "--static"])

    assert result.exit_code == 0
    assert "gpt-4.1-mini" in result.stdout


def test_models_table_rendering() -> None:
    table = models_table(available_models("openai", live=False))

    assert table.row_count >= 1


def test_integrations_json_and_presets_table() -> None:
    integrations_result = runner.invoke(app, ["integrations", "--search", "auth", "--json"])
    presets_result = runner.invoke(app, ["integrations", "--presets"])

    assert integrations_result.exit_code == 0
    assert "authx" in integrations_result.stdout
    assert presets_result.exit_code == 0
    assert "api-starter" in presets_result.stdout


def test_create_non_interactive_requires_project_name() -> None:
    result = runner.invoke(app, ["create", "--no-interactive"])

    assert result.exit_code != 0
    assert "PROJECT_NAME is required" in result.output


def test_create_interactive_cancel(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "run_playground", lambda **_: None)

    result = runner.invoke(app, ["create"])

    assert result.exit_code == 0
    assert "Cancelled" in result.stdout


def test_create_interactive_playground_success(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    config = ProjectConfig(project_name="interactive-api", output_dir=tmp_path)
    monkeypatch.setattr(cli, "run_playground", lambda **_: config)

    result = runner.invoke(app, ["create"])

    assert result.exit_code == 0
    assert (tmp_path / "interactive-api" / "pyproject.toml").exists()


def test_create_non_dry_success_and_with_docker(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "created-api",
            "--with-docker",
            "--no-interactive",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "created-api" / "Dockerfile").exists()
    assert "Next steps" in result.stdout


def test_create_invalid_integration_error(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "create",
            "bad-api",
            "--integration",
            "missing",
            "--no-interactive",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 1
    assert "Unknown integration" in result.stdout


def test_create_basic_prompt_flow(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    answers = iter(["demo-api", "demo_api", "openapi"])
    monkeypatch.setattr(Prompt, "ask", lambda *_, **__: next(answers))
    monkeypatch.setattr(Confirm, "ask", lambda *_, **__: False)

    result = runner.invoke(
        app,
        ["create", "--basic", "--output-dir", str(tmp_path), "--dry-run"],
    )

    assert result.exit_code == 0
    assert "Dry run complete" in result.stdout


def test_generate_confirmation_cancel(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(Confirm, "ask", lambda *_, **__: False)

    result = runner.invoke(app, ["generate", "starter MVP"])

    assert result.exit_code == 0
    assert "Cancelled" in result.stdout


def test_generate_non_dry_success(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "small API", "--yes", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert (tmp_path / "small" / "pyproject.toml").exists()
    assert "Next steps" in result.stdout


def test_generate_json_non_dry_success(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["generate", "small API", "--json", "--yes", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert '"project_name"' in result.stdout
    assert (tmp_path / "small" / "pyproject.toml").exists()
