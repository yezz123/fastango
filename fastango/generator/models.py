"""Typed models for constrained Fastango generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from fastango.scaffold.config import ProjectConfig, TemplateStyle, normalize_package_name

GenerationProvider = Literal["deterministic", "anthropic", "openai", "auto"]


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    provider: GenerationProvider = "deterministic"
    model: str | None = None
    style: TemplateStyle | None = None
    project_name: str | None = None
    output_dir: Path = field(default_factory=Path.cwd)
    yes: bool = False
    dry_run: bool = False
    json_output: bool = False
    force: bool = False
    allow_experimental_suggestions: bool = False


@dataclass(frozen=True)
class ChoiceReason:
    name: str
    reason: str


@dataclass(frozen=True)
class SecurityPolicy:
    notes: tuple[str, ...] = (
        "Secrets are generated only as environment placeholders.",
        "Webhook integrations must verify provider signatures.",
        "Keep business logic in services and use FastAPI dependencies for request boundaries.",
    )


@dataclass(frozen=True)
class GenerationPlan:
    prompt: str
    project_name: str
    style: TemplateStyle
    skills: tuple[str, ...] = ()
    presets: tuple[str, ...] = ()
    integrations: tuple[str, ...] = ()
    reasons: tuple[ChoiceReason, ...] = ()
    security_notes: tuple[str, ...] = ()
    not_generated: tuple[str, ...] = ()
    provider: GenerationProvider = "deterministic"
    model: str | None = None

    def to_project_config(self, *, output_dir: Path, force: bool = False) -> ProjectConfig:
        return ProjectConfig(
            project_name=self.project_name,
            package_name=normalize_package_name(self.project_name),
            output_dir=output_dir,
            style=self.style,
            integrations=self.integrations,
            presets=self.presets,
            force=force,
        )
