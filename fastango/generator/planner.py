"""Generation planner that merges deterministic and optional provider suggestions."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

from fastango.generator.constraints import (
    ProviderSuggestion,
    validate_generation_plan,
    validate_provider_suggestion,
)
from fastango.generator.model_catalog import validate_model
from fastango.generator.models import (
    ChoiceReason,
    GenerationPlan,
    GenerationProvider,
    GenerationRequest,
)
from fastango.generator.providers.anthropic import AnthropicProvider
from fastango.generator.providers.base import GenerationProviderAdapter, ProviderError
from fastango.generator.providers.openai import OpenAIProvider
from fastango.generator.rules import deterministic_plan
from fastango.generator.skills import get_skill
from fastango.scaffold.config import TemplateStyle
from fastango.scaffold.registry import IntegrationRegistry


def build_generation_plan(
    request: GenerationRequest,
    *,
    registry: IntegrationRegistry | None = None,
    provider_adapter: GenerationProviderAdapter | None = None,
) -> GenerationPlan:
    resolved_registry = registry or IntegrationRegistry.builtins()
    plan = deterministic_plan(
        prompt=request.prompt,
        registry=resolved_registry,
        project_name=request.project_name,
        style=request.style,
    )
    provider = provider_adapter or _provider_for(request.provider, request.model)
    if provider is not None:
        suggestion = provider.suggest(request.prompt)
        unsupported = validate_provider_suggestion(
            suggestion,
            resolved_registry,
            allow_experimental_suggestions=request.allow_experimental_suggestions,
        )
        plan = _merge_provider_suggestion(plan, suggestion, unsupported)
        plan = replace(
            plan, provider=request.provider, model=getattr(provider, "model", request.model)
        )
    elif request.model:
        raise ProviderError("--model can only be used with --provider anthropic, openai, or auto.")

    validate_generation_plan(plan, resolved_registry)
    return plan


def _provider_for(
    provider: GenerationProvider, model: str | None
) -> GenerationProviderAdapter | None:
    if provider == "deterministic":
        return None
    if provider == "anthropic":
        return AnthropicProvider(model=model)
    if provider == "openai":
        return OpenAIProvider(model=model)
    if provider == "auto":
        try:
            return AnthropicProvider(model=model)
        except ProviderError:
            if model:
                validate_model("openai", model)
            return None
    return None


def _merge_provider_suggestion(
    plan: GenerationPlan,
    suggestion: ProviderSuggestion,
    unsupported: tuple[str, ...],
) -> GenerationPlan:
    skills = list(plan.skills)
    presets = list(plan.presets)
    integrations = list(plan.integrations)
    reasons = list(plan.reasons)
    security_notes = list(plan.security_notes)
    not_generated = list(plan.not_generated)

    for skill_name in suggestion.skills:
        if skill_name not in skills:
            skill = get_skill(skill_name)
            skills.append(skill.name)
            reasons.append(ChoiceReason(skill.name, "Suggested by the configured AI provider."))
            for preset in skill.presets:
                if preset not in presets:
                    presets.append(preset)
            for integration in skill.integrations:
                if integration not in integrations:
                    integrations.append(integration)
            security_notes.extend(skill.security_notes)
    for preset in suggestion.presets:
        if preset not in presets:
            presets.append(preset)
            reasons.append(ChoiceReason(preset, "Suggested by the configured AI provider."))
    for integration in suggestion.integrations:
        if integration not in integrations:
            integrations.append(integration)
            reasons.append(ChoiceReason(integration, "Suggested by the configured AI provider."))
    not_generated.extend(unsupported)
    not_generated.extend(suggestion.notes)

    return replace(
        plan,
        skills=tuple(skills),
        presets=tuple(presets),
        integrations=tuple(integrations),
        reasons=tuple(reasons),
        security_notes=tuple(dict.fromkeys(security_notes)),
        not_generated=tuple(dict.fromkeys(not_generated)),
        style=cast(TemplateStyle, suggestion.style)
        if suggestion.style in ("simple", "mvc")
        else plan.style,
    )
