"""Allowlist validation for generated Fastango plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastango.generator.models import GenerationPlan
from fastango.generator.skills import skill_names
from fastango.scaffold.registry import IntegrationError, IntegrationRegistry

SUPPORTED_TEMPLATES = ("simple", "mvc")


class GenerationConstraintError(ValueError):
    """Raised when a generated plan escapes Fastango's supported surface."""


@dataclass(frozen=True)
class ProviderSuggestion:
    skills: tuple[str, ...] = ()
    presets: tuple[str, ...] = ()
    integrations: tuple[str, ...] = ()
    style: str | None = None
    raw_code: str | None = None
    notes: tuple[str, ...] = ()


def validate_provider_suggestion(
    suggestion: ProviderSuggestion,
    registry: IntegrationRegistry,
    *,
    allow_experimental_suggestions: bool = False,
) -> tuple[str, ...]:
    """Validate provider output and return unsupported notes."""

    unsupported: list[str] = []
    if suggestion.raw_code:
        raise GenerationConstraintError("Provider output included raw code, which is not allowed.")
    if suggestion.style and suggestion.style not in SUPPORTED_TEMPLATES:
        raise GenerationConstraintError(f"Unsupported template '{suggestion.style}'.")
    for skill in suggestion.skills:
        if skill not in skill_names():
            if allow_experimental_suggestions:
                unsupported.append(f"Not generated: unsupported skill '{skill}'.")
            else:
                raise GenerationConstraintError(f"Unsupported skill '{skill}'.")
    for preset in suggestion.presets:
        try:
            registry.get_preset(preset)
        except IntegrationError as exc:
            if allow_experimental_suggestions:
                unsupported.append(f"Not generated: unsupported preset '{preset}'.")
            else:
                raise GenerationConstraintError(str(exc)) from exc
    for integration in suggestion.integrations:
        try:
            registry.get(integration)
        except IntegrationError as exc:
            if allow_experimental_suggestions:
                unsupported.append(f"Not generated: unsupported integration '{integration}'.")
            else:
                raise GenerationConstraintError(str(exc)) from exc
    return tuple(unsupported)


def validate_generation_plan(plan: GenerationPlan, registry: IntegrationRegistry) -> None:
    if plan.style not in SUPPORTED_TEMPLATES:
        raise GenerationConstraintError(f"Unsupported template '{plan.style}'.")
    for skill in plan.skills:
        if skill not in skill_names():
            raise GenerationConstraintError(f"Unsupported skill '{skill}'.")
    for preset in plan.presets:
        registry.get_preset(preset)
    for integration in plan.integrations:
        registry.get(integration)
    registry.resolve(plan.to_project_config(output_dir=Path(".")))
