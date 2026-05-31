import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from fastango.generator.constraints import (
    GenerationConstraintError,
    ProviderSuggestion,
    validate_generation_plan,
    validate_provider_suggestion,
)
from fastango.generator.model_catalog import (
    available_models,
    default_model,
    models_for_provider,
    models_from_api,
    validate_model,
)
from fastango.generator.models import GenerationPlan, GenerationRequest
from fastango.generator.planner import _provider_for, build_generation_plan
from fastango.generator.preview import config_from_plan, generation_preview, security_table
from fastango.generator.providers.anthropic import AnthropicProvider
from fastango.generator.providers.base import ProviderError, parse_provider_suggestion
from fastango.generator.providers.openai import OpenAIProvider
from fastango.generator.skills import get_skill
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

    with pytest.raises(GenerationConstraintError, match="Unsupported template"):
        validate_provider_suggestion(ProviderSuggestion(style="django"), registry)


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


def test_generation_constraints_reject_unknown_ids() -> None:
    registry = IntegrationRegistry.builtins()
    with pytest.raises(GenerationConstraintError, match="Unsupported skill"):
        validate_provider_suggestion(ProviderSuggestion(skills=("unknown",)), registry)
    notes = validate_provider_suggestion(
        ProviderSuggestion(skills=("unknown",), presets=("unknown",)),
        registry,
        allow_experimental_suggestions=True,
    )
    assert "unsupported skill" in notes[0]
    with pytest.raises(GenerationConstraintError, match="Unknown preset"):
        validate_provider_suggestion(ProviderSuggestion(presets=("unknown",)), registry)
    with pytest.raises(GenerationConstraintError, match="Unknown integration"):
        validate_provider_suggestion(ProviderSuggestion(integrations=("unknown",)), registry)
    with pytest.raises(GenerationConstraintError, match="Unsupported template"):
        validate_generation_plan(
            GenerationPlan(prompt="", project_name="demo", style="django"),  # type: ignore[arg-type]
            registry,
        )
    with pytest.raises(GenerationConstraintError, match="Unsupported skill"):
        validate_generation_plan(
            GenerationPlan(prompt="", project_name="demo", style="simple", skills=("unknown",)),
            registry,
        )


def test_get_skill_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown generation skill"):
        get_skill("missing")


def test_provider_merge_path_with_fake_adapter() -> None:
    class FakeProvider:
        model = "fake-model"

        def suggest(self, prompt: str) -> ProviderSuggestion:
            return ProviderSuggestion(
                skills=("crud-api",),
                presets=("api-starter",),
                integrations=("pagination",),
                notes=("Provider note",),
            )

    plan = build_generation_plan(
        GenerationRequest(prompt="records API", provider="openai"),
        provider_adapter=FakeProvider(),
    )

    assert plan.model == "fake-model"
    assert "crud-api" in plan.skills
    assert "Provider note" in plan.not_generated


def test_provider_merge_deduplicates_and_applies_style() -> None:
    class FakeProvider:
        model = "fake-model"

        def suggest(self, prompt: str) -> ProviderSuggestion:
            return ProviderSuggestion(
                skills=("saas-mvp",),
                presets=("saas",),
                integrations=("teams",),
                style="simple",
            )

    plan = build_generation_plan(
        GenerationRequest(prompt="starter MVP", provider="anthropic"),
        provider_adapter=FakeProvider(),
    )

    assert plan.style == "simple"
    assert plan.skills.count("saas-mvp") == 1


def test_provider_merge_adds_new_skill_preset_and_integration() -> None:
    class FakeProvider:
        model = "fake-model"

        def suggest(self, prompt: str) -> ProviderSuggestion:
            return ProviderSuggestion(
                skills=("crud-api",),
                presets=("production",),
                integrations=("sentry",),
            )

    plan = build_generation_plan(
        GenerationRequest(prompt="plain service", provider="openai"),
        provider_adapter=FakeProvider(),
    )

    assert "crud-api" in plan.skills
    assert "production" in plan.presets
    assert "sentry" in plan.integrations


def test_provider_merge_skips_existing_skill_contributions() -> None:
    class FakeProvider:
        model = "fake-model"

        def suggest(self, prompt: str) -> ProviderSuggestion:
            return ProviderSuggestion(skills=("crud-api",))

    plan = build_generation_plan(
        GenerationRequest(prompt="api pagination", provider="openai"),
        provider_adapter=FakeProvider(),
    )

    assert plan.presets.count("api-starter") == 1
    assert plan.integrations.count("pagination") == 1


def test_auto_provider_falls_back_when_anthropic_missing_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ProviderError):
        build_generation_plan(GenerationRequest(prompt="starter MVP", provider="auto"))


def test_provider_factory_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    assert _provider_for("deterministic", None) is None
    assert _provider_for("anthropic", "claude-3-5-haiku-latest") is not None
    assert _provider_for("openai", "gpt-4.1-mini") is not None
    assert _provider_for("missing", None) is None  # type: ignore[arg-type]


def test_provider_factory_auto_returns_none_when_constructor_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import fastango.generator.planner as planner

    class BrokenAnthropicProvider:
        def __init__(self, *, model: str | None = None) -> None:
            raise ProviderError("missing")

    monkeypatch.setattr(planner, "AnthropicProvider", BrokenAnthropicProvider)

    assert planner._provider_for("auto", None) is None  # noqa: SLF001


def test_auto_provider_with_model_validates_openai_after_anthropic_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    provider = _provider_for("auto", "gpt-4.1-mini")

    assert provider is None


def test_openai_provider_sends_selected_model(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, Any] = {}

    def fake_post(*_: Any, **kwargs: Any) -> SimpleNamespace:
        calls.update(kwargs["json"])
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"output": [{"content": [{"text": '{"integrations": ["openapi"]}'}]}]},
        )

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(
        "fastango.generator.providers.openai.import_module",
        lambda name: SimpleNamespace(post=fake_post) if name == "httpx" else __import__(name),
    )

    suggestion = OpenAIProvider(model="gpt-4.1-mini").suggest("starter")

    assert calls["model"] == "gpt-4.1-mini"
    assert suggestion.integrations == ("openapi",)


def test_openai_provider_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ProviderError, match="OPENAI_API_KEY"):
        OpenAIProvider(model="gpt-4.1-mini").suggest("starter")


def test_anthropic_provider_sends_selected_model(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, Any] = {}

    def fake_post(*_: Any, **kwargs: Any) -> SimpleNamespace:
        calls.update(kwargs["json"])
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"content": [{"text": '{"presets": ["api-starter"]}'}]},
        )

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(
        "fastango.generator.providers.anthropic.import_module",
        lambda name: SimpleNamespace(post=fake_post) if name == "httpx" else __import__(name),
    )

    suggestion = AnthropicProvider(model="claude-3-5-haiku-latest").suggest("starter")

    assert calls["model"] == "claude-3-5-haiku-latest"
    assert suggestion.presets == ("api-starter",)


def test_available_models_falls_back_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    models = available_models("openai")

    assert models[0].source == "curated"


def test_model_catalog_provider_none_and_anthropic_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAnthropicResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"data": [{"id": "claude-live", "display_name": "Claude Live"}]}

    fake_httpx = SimpleNamespace(get=lambda *_, **__: FakeAnthropicResponse())
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(
        "fastango.generator.model_catalog.import_module",
        lambda name: fake_httpx if name == "httpx" else __import__(name),
    )

    assert models_for_provider()[0].model
    assert models_from_api("anthropic")[0].model == "claude-live"
    assert available_models(None)[0].source == "api"
    assert default_model("anthropic") == "claude-3-5-haiku-latest"


def test_model_catalog_anthropic_without_key_and_default_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="ANTHROPIC_API_KEY"):
        models_from_api("anthropic")

    import fastango.generator.model_catalog as catalog

    monkeypatch.setattr(
        catalog,
        "SUPPORTED_MODELS",
        (catalog.SupportedModel("openai", "custom", "Custom", "Custom"),),
    )
    assert default_model("openai") == "custom"


def test_rules_cover_alternate_keywords() -> None:
    paddle = build_generation_plan(GenerationRequest(prompt="checkout with paddle"))
    lemon = build_generation_plan(GenerationRequest(prompt="checkout with lemon-squeezy"))
    production = build_generation_plan(
        GenerationRequest(prompt="secure production API key uploads crud")
    )

    assert "paddle" in paddle.integrations
    assert "lemonsqueezy" in lemon.integrations
    assert "production" in production.presets
    assert "api-keys" in production.integrations
    assert "uploads" in production.integrations

    explicit_ai = build_generation_plan(GenerationRequest(prompt="openai anthropic claude"))
    assert "openai" in explicit_ai.integrations
    assert "anthropic" in explicit_ai.integrations


def test_generation_preview_helpers(tmp_path: Path) -> None:
    plan = GenerationPlan(
        prompt="",
        project_name="demo",
        style="simple",
        not_generated=("Not generated: frontend",),
    )

    assert config_from_plan(plan, tmp_path).project_name == "demo"
    assert generation_preview(plan, output_dir=tmp_path)
    assert security_table(plan).row_count == 1
