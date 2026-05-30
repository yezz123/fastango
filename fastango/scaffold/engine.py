"""High-level scaffold orchestration."""

from __future__ import annotations

import subprocess

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.filesystem import WriteResult, write_files
from fastango.scaffold.plan import EnvVar, ScaffoldPlan
from fastango.scaffold.registry import IntegrationRegistry
from fastango.scaffold.renderer import TemplateRenderer

BASE_DEPENDENCIES = [
    "fastapi[standard]>=0.115.0",
    "orjson>=3.10.0",
    "pydantic-settings>=2.5.0",
]


class ScaffoldEngine:
    """Generate FastAPI projects from templates and selected integrations."""

    def __init__(
        self,
        *,
        registry: IntegrationRegistry | None = None,
        renderer: TemplateRenderer | None = None,
    ) -> None:
        self.registry = registry or IntegrationRegistry.builtins()
        self.renderer = renderer or TemplateRenderer()

    def build_plan(self, config: ProjectConfig) -> ScaffoldPlan:
        plan = ScaffoldPlan(config=config)
        for dependency in BASE_DEPENDENCIES:
            plan.add_dependency(dependency)

        plan.add_dev_dependency("pytest>=8.0.0")
        plan.add_dev_dependency("httpx>=0.27.0")
        plan.add_dev_dependency("ruff>=0.8.0")
        plan.add_env_var(EnvVar("APP_NAME", config.project_name, "Application display name."))
        plan.add_env_var(EnvVar("ENVIRONMENT", "local", "Runtime environment name."))
        plan.add_openapi_tag("health", "Health and readiness checks.")
        plan.add_llms_section(
            "Use `uv` for dependency management and command execution. Do not add "
            "`requirements.txt` unless a deployment target explicitly requires it."
        )

        integrations = self.registry.resolve(config)
        for integration in integrations:
            plan.enabled_integrations.append(integration.name)
            integration.apply(plan)

        return plan

    def create(self, config: ProjectConfig, *, dry_run: bool = False) -> WriteResult:
        plan = self.build_plan(config)
        files = self.renderer.render_plan(plan)
        result = write_files(config.target_dir, files, force=config.force, dry_run=dry_run)
        if config.create_git and not dry_run:
            subprocess.run(["git", "init"], cwd=config.target_dir, check=True)
        return result
