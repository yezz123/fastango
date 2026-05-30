"""Supported LLM model catalog for optional generation providers."""

from __future__ import annotations

import os
from contextlib import suppress
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

from fastango.generator.providers.base import ProviderError

ModelProvider = Literal["anthropic", "openai"]
ModelSource = Literal["curated", "api"]


@dataclass(frozen=True)
class SupportedModel:
    provider: ModelProvider
    model: str
    label: str
    description: str
    default: bool = False
    source: ModelSource = "curated"


SUPPORTED_MODELS: tuple[SupportedModel, ...] = (
    SupportedModel(
        provider="anthropic",
        model="claude-3-5-haiku-latest",
        label="Claude 3.5 Haiku",
        description="Fast and cost-conscious planning for normal scaffolds.",
        default=True,
    ),
    SupportedModel(
        provider="anthropic",
        model="claude-3-5-sonnet-latest",
        label="Claude 3.5 Sonnet",
        description="Stronger reasoning for larger MVP prompts.",
    ),
    SupportedModel(
        provider="anthropic",
        model="claude-3-7-sonnet-latest",
        label="Claude 3.7 Sonnet",
        description="Advanced planning for complex product scaffolds.",
    ),
    SupportedModel(
        provider="openai",
        model="gpt-4.1-mini",
        label="GPT-4.1 mini",
        description="Fast and cost-conscious planning for normal scaffolds.",
        default=True,
    ),
    SupportedModel(
        provider="openai",
        model="gpt-4.1",
        label="GPT-4.1",
        description="Stronger planning for more complex MVP prompts.",
    ),
    SupportedModel(
        provider="openai",
        model="gpt-4o-mini",
        label="GPT-4o mini",
        description="General-purpose planning with broad availability.",
    ),
)


def models_for_provider(provider: ModelProvider | None = None) -> tuple[SupportedModel, ...]:
    if provider is None:
        return SUPPORTED_MODELS
    return tuple(model for model in SUPPORTED_MODELS if model.provider == provider)


def models_from_api(provider: ModelProvider) -> tuple[SupportedModel, ...]:
    if provider == "anthropic":
        return _anthropic_models_from_api()
    return _openai_models_from_api()


def available_models(
    provider: ModelProvider | None = None,
    *,
    live: bool = True,
) -> tuple[SupportedModel, ...]:
    if not live:
        return models_for_provider(provider)
    if provider is not None:
        try:
            return models_from_api(provider)
        except ProviderError:
            return models_for_provider(provider)

    models: list[SupportedModel] = []
    for candidate in ("anthropic", "openai"):
        try:
            models.extend(models_from_api(candidate))
        except ProviderError:
            models.extend(models_for_provider(candidate))
    return tuple(models)


def default_model(provider: ModelProvider) -> str:
    for model in SUPPORTED_MODELS:
        if model.provider == provider and model.default:
            return model.model
    return models_for_provider(provider)[0].model


def validate_model(provider: ModelProvider, model: str | None) -> str:
    selected = model or default_model(provider)
    supported = {item.model for item in models_for_provider(provider)}
    if selected not in supported:
        with suppress(ProviderError):
            supported.update(item.model for item in models_from_api(provider))
    if selected not in supported:
        available = ", ".join(sorted(supported))
        raise ProviderError(
            f"Model '{selected}' is not supported for provider '{provider}'. Available: {available}."
        )
    return selected


def _httpx() -> Any:
    try:
        return import_module("httpx")
    except ImportError as exc:  # pragma: no cover - optional dependency path.
        raise ProviderError(
            "Install Fastango with the `ai` extra to discover provider models."
        ) from exc


def _anthropic_models_from_api() -> tuple[SupportedModel, ...]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderError("ANTHROPIC_API_KEY is required to discover Anthropic models.")
    response = _httpx().get(
        "https://api.anthropic.com/v1/models",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()
    return tuple(
        SupportedModel(
            provider="anthropic",
            model=str(item["id"]),
            label=str(item.get("display_name") or item["id"]),
            description="Discovered from the configured Anthropic API key.",
            source="api",
        )
        for item in response.json().get("data", [])
        if item.get("id")
    )


def _openai_models_from_api() -> tuple[SupportedModel, ...]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY is required to discover OpenAI models.")
    response = _httpx().get(
        "https://api.openai.com/v1/models",
        headers={"authorization": f"Bearer {api_key}", "content-type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return tuple(
        SupportedModel(
            provider="openai",
            model=str(item["id"]),
            label=str(item["id"]),
            description="Discovered from the configured OpenAI API key.",
            source="api",
        )
        for item in response.json().get("data", [])
        if item.get("id")
    )
