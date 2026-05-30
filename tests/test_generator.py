import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from fastango.generator.constraints import (
    GenerationConstraintError,
    ProviderSuggestion,
    validate_provider_suggestion,
)
from fastango.generator.model_catalog import available_models, default_model, validate_model
from fastango.generator.models import GenerationRequest
from fastango.generator.planner import build_generation_plan
from fastango.generator.providers.base import ProviderError, parse_provider_suggestion
from fastango.scaffold.registry import IntegrationRegistry


def test_deterministic_planner_maps_starter_mvp_to_supported_stack() -> None:
    plan = build_generation_plan(
        GenerationRequest(prompt="a starter MVP with auth billing email analytics")
    )

    assert plan.style == "mvc"
    assert "saas-mvp" in plan.skills
    assert "saas" in plan.presets
    assert "teams" in plan.integrations
    assert "admin" in plan.integrations
    assert any(reason.reason for reason in plan.reasons)


def test_planner_records_unsupported_frontend_notes() -> None:
    plan = build_generation_plan(GenerationRequest(prompt="FastAPI MVP with Next.js and Three.js"))

    assert any("frontend frameworks" in note for note in plan.not_generated)


def test_planner_drops_conflicting_payment_provider() -> None:
    plan = build_generation_plan(
        GenerationRequest(prompt="a starter SaaS MVP with Stripe and Polar billing")
    )

    assert "saas" in plan.presets
    assert "polar" not in plan.integrations
    assert any("polar" in note and "conflicts" in note for note in plan.not_generated)


def test_provider_parser_rejects_invalid_json() -> None:
    with pytest.raises(ProviderError):
        parse_provider_suggestion("not json")


def test_provider_constraint_rejects_raw_code() -> None:
    registry = IntegrationRegistry.builtins()

    with pytest.raises(GenerationConstraintError):
        validate_provider_suggestion(
            ProviderSuggestion(raw_code="print('write this')"),
            registry,
        )


def test_provider_constraint_converts_unsupported_when_allowed() -> None:
    registry = IntegrationRegistry.builtins()

    notes = validate_provider_suggestion(
        ProviderSuggestion(integrations=("nextjs",)),
        registry,
        allow_experimental_suggestions=True,
    )

    assert notes == ("Not generated: unsupported integration 'nextjs'.",)


def test_json_plan_is_serializable(tmp_path: Path) -> None:
    plan = build_generation_plan(GenerationRequest(prompt="AI SaaS with vector search"))
    config = plan.to_project_config(output_dir=tmp_path)

    assert config.style == "mvc"
    assert json.dumps({"integrations": plan.integrations})


def test_supported_model_defaults_and_validation() -> None:
    assert default_model("anthropic") == "claude-3-5-haiku-latest"
    assert validate_model("openai", "gpt-4.1-mini") == "gpt-4.1-mini"

    with pytest.raises(ProviderError):
        validate_model("openai", "claude-3-5-haiku-latest")


def test_available_models_discovers_openai_models(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"data": [{"id": "gpt-live-account-model"}]}

    fake_httpx = SimpleNamespace(get=lambda *_, **__: FakeResponse())
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "fastango.generator.model_catalog.import_module",
        lambda name: fake_httpx if name == "httpx" else __import__(name),
    )

    models = available_models("openai")

    assert models[0].model == "gpt-live-account-model"
    assert models[0].source == "api"


def test_validate_model_accepts_api_discovered_model(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"data": [{"id": "gpt-live-account-model"}]}

    fake_httpx = SimpleNamespace(get=lambda *_, **__: FakeResponse())
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "fastango.generator.model_catalog.import_module",
        lambda name: fake_httpx if name == "httpx" else __import__(name),
    )

    assert validate_model("openai", "gpt-live-account-model") == "gpt-live-account-model"
