"""Provider protocol and structured suggestion parsing."""

from __future__ import annotations

import json
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from fastango.generator.constraints import ProviderSuggestion


class ProviderError(RuntimeError):
    """Raised when an optional LLM provider cannot produce a valid suggestion."""


class GenerationProviderAdapter(Protocol):
    name: str

    def suggest(self, prompt: str) -> ProviderSuggestion:
        """Return constrained provider suggestions."""


class ProviderSuggestionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[str] = Field(default_factory=list)
    presets: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    style: str | None = None
    raw_code: str | None = None
    notes: list[str] = Field(default_factory=list)


def parse_provider_suggestion(payload: str) -> ProviderSuggestion:
    try:
        data = json.loads(payload)
        parsed = ProviderSuggestionPayload.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ProviderError("Provider returned invalid structured JSON.") from exc
    return ProviderSuggestion(
        skills=tuple(parsed.skills),
        presets=tuple(parsed.presets),
        integrations=tuple(parsed.integrations),
        style=parsed.style,
        raw_code=parsed.raw_code,
        notes=tuple(parsed.notes),
    )
