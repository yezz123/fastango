from pathlib import Path
from typing import Any

from pytest import MonkeyPatch
from rich.prompt import Confirm, Prompt

from fastango.scaffold.registry import IntegrationRegistry
from fastango.tui.app import run_playground


def test_playground_builds_project_config(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    answers = iter(["demo-api", "demo_api", "mvc", "3.12", "api-starter", "", "", "redis"])

    def fake_prompt(*_: Any, **__: Any) -> str:
        return next(answers)

    def fake_confirm(*_: Any, **__: Any) -> bool:
        return True

    monkeypatch.setattr(Prompt, "ask", fake_prompt)
    monkeypatch.setattr(Confirm, "ask", fake_confirm)

    config = run_playground(
        registry=IntegrationRegistry.builtins(),
        output_dir=tmp_path,
    )

    assert config is not None
    assert config.project_name == "demo-api"
    assert config.style == "mvc"
    assert config.presets == ("api-starter",)
    assert config.integrations == ("redis",)
    assert config.create_git is True
