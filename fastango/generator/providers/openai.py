"""OpenAI provider adapter for constrained generation suggestions."""

from __future__ import annotations

import os
from importlib import import_module
from typing import Any

from fastango.generator.constraints import ProviderSuggestion
from fastango.generator.model_catalog import validate_model
from fastango.generator.providers.base import ProviderError, parse_provider_suggestion


class OpenAIProvider:
    name = "openai"

    def __init__(self, *, model: str | None = None) -> None:
        self.model = validate_model("openai", model)

    def suggest(self, prompt: str) -> ProviderSuggestion:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is required for the OpenAI provider.")
        try:
            httpx: Any = import_module("httpx")
        except ImportError as exc:  # pragma: no cover - optional dependency path.
            raise ProviderError("Install Fastango with the `ai` extra to use providers.") from exc

        response = httpx.post(
            "https://api.openai.com/v1/responses",
            headers={"authorization": f"Bearer {api_key}", "content-type": "application/json"},
            json={
                "model": self.model,
                "input": (
                    "Return only JSON with keys skills, presets, integrations, style, notes. "
                    "Use only known Fastango IDs. Do not include raw_code. "
                    f"User prompt: {prompt}"
                ),
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["output"][0]["content"][0]["text"]
        return parse_provider_suggestion(content)
