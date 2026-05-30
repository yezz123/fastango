"""Anthropic provider adapter for constrained generation suggestions."""

from __future__ import annotations

import os
from importlib import import_module
from typing import Any

from fastango.generator.constraints import ProviderSuggestion
from fastango.generator.model_catalog import validate_model
from fastango.generator.providers.base import ProviderError, parse_provider_suggestion


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, *, model: str | None = None) -> None:
        self.model = validate_model("anthropic", model)

    def suggest(self, prompt: str) -> ProviderSuggestion:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderError("ANTHROPIC_API_KEY is required for the Anthropic provider.")
        try:
            httpx: Any = import_module("httpx")
        except ImportError as exc:  # pragma: no cover - optional dependency path.
            raise ProviderError("Install Fastango with the `ai` extra to use providers.") from exc

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 800,
                "messages": [{"role": "user", "content": _provider_prompt(prompt)}],
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["content"][0]["text"]
        return parse_provider_suggestion(content)


def _provider_prompt(prompt: str) -> str:
    return (
        "Return only JSON with keys skills, presets, integrations, style, notes. "
        "Use only known Fastango IDs. Do not include raw_code. "
        f"User prompt: {prompt}"
    )
