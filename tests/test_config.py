from pathlib import Path

import pytest
from pydantic import ValidationError
from pytest import MonkeyPatch
from rich.prompt import Confirm, Prompt

import fastango.scaffold.config as config_module
from fastango.scaffold.config import ProjectConfig, normalize_package_name
from fastango.scaffold.prompts import prompt_for_config
from fastango.scaffold.registry import IntegrationRegistry


def test_normalize_package_name() -> None:
    assert normalize_package_name("Billing API") == "billing_api"
    assert normalize_package_name("123-api") == "app_123_api"


def test_project_config_derives_package_name() -> None:
    config = ProjectConfig(project_name="billing-api", output_dir=Path("/tmp"))

    assert config.package_name == "billing_api"
    assert config.target_dir == Path("/tmp/billing-api")


def test_project_config_rejects_invalid_python_version() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(project_name="billing-api", python_version="3.9")


def test_prompt_for_config_uses_existing_integrations(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    answers = iter(["demo-api", "demo_api"])
    monkeypatch.setattr(Prompt, "ask", lambda *_, **__: next(answers))
    monkeypatch.setattr(Confirm, "ask", lambda *_, **__: True)

    config = prompt_for_config(
        project_name=None,
        package_name=None,
        output_dir=tmp_path,
        style="mvc",
        python_version="3.12",
        integrations=("openapi",),
        create_git=False,
        force=True,
        registry=IntegrationRegistry.builtins(),
    )

    assert config.create_git is True
    assert config.integrations == ("openapi",)


def test_prompt_for_config_prompts_for_integrations(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    answers = iter(["openapi,redis"])
    monkeypatch.setattr(Prompt, "ask", lambda *_, **__: next(answers))
    monkeypatch.setattr(Confirm, "ask", lambda *_, **__: False)

    config = prompt_for_config(
        project_name="demo-api",
        package_name="demo_api",
        output_dir=tmp_path,
        style="simple",
        python_version="3.12",
        integrations=(),
        create_git=False,
        force=False,
        registry=IntegrationRegistry.builtins(),
    )

    assert config.integrations == ("openapi", "redis")


def test_project_config_validation_edges(monkeypatch: MonkeyPatch) -> None:
    with pytest.raises(ValidationError, match="Project name is required"):
        ProjectConfig(project_name="")
    with pytest.raises(ValidationError, match="dots, dashes"):
        ProjectConfig(project_name="bad name")
    with pytest.raises(ValidationError, match="Package name"):
        ProjectConfig(project_name="demo", package_name="class")
    with pytest.raises(TypeError, match="Integrations"):
        ProjectConfig.normalize_slug_tuple(123)

    monkeypatch.setattr(config_module, "normalize_package_name", lambda _: "class")
    with pytest.raises(ValidationError, match="Could not derive"):
        ProjectConfig(project_name="demo")
    monkeypatch.undo()

    assert ProjectConfig(project_name="demo", integrations=None).integrations == ()  # type: ignore[arg-type]
    config = ProjectConfig(project_name="demo", integrations="openapi, openapi, redis")
    assert config.integrations == ("openapi", "redis")
