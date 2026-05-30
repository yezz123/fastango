"""Reusable scaffold preview summaries."""

from __future__ import annotations

from dataclasses import dataclass

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine


@dataclass(frozen=True)
class ScaffoldPreview:
    project_name: str
    style: str
    integrations: tuple[str, ...]
    dependencies: tuple[str, ...]
    dev_dependencies: tuple[str, ...]
    env_vars: tuple[str, ...]
    files: tuple[str, ...]


def build_preview(config: ProjectConfig, engine: ScaffoldEngine | None = None) -> ScaffoldPreview:
    resolved_engine = engine or ScaffoldEngine()
    plan = resolved_engine.build_plan(config)
    rendered_files = resolved_engine.renderer.render_plan(plan)
    return ScaffoldPreview(
        project_name=config.project_name,
        style=config.style,
        integrations=tuple(plan.enabled_integrations),
        dependencies=tuple(sorted(plan.dependencies)),
        dev_dependencies=tuple(sorted(plan.dev_dependencies)),
        env_vars=tuple(env_var.name for env_var in plan.env_vars),
        files=tuple(str(file.path) for file in rendered_files),
    )
