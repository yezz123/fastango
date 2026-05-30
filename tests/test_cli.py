from pytest import MonkeyPatch
from typer.testing import CliRunner

import fastango.cli
from fastango.cli import app

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

    monkeypatch.setattr(fastango.cli, "launch_playground", fake_launch_playground)

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
