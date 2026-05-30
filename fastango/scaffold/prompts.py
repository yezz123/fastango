"""Interactive prompts for the Fastango CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.prompt import Confirm, Prompt

from fastango.scaffold.config import ProjectConfig, normalize_package_name
from fastango.scaffold.registry import IntegrationRegistry


def prompt_for_config(
    *,
    project_name: str | None,
    package_name: str | None,
    output_dir: Path,
    style: str | None,
    python_version: str | None,
    integrations: tuple[str, ...],
    create_git: bool,
    force: bool,
    registry: IntegrationRegistry,
) -> ProjectConfig:
    """Collect missing values interactively."""

    resolved_project_name = project_name or Prompt.ask("Project name")
    resolved_package_name = package_name or Prompt.ask(
        "Package name",
        default=normalize_package_name(resolved_project_name),
    )
    resolved_style = style or Prompt.ask(
        "Template style", choices=["simple", "mvc"], default="simple"
    )
    resolved_python = python_version or Prompt.ask(
        "Python version",
        choices=["3.10", "3.11", "3.12", "3.13"],
        default="3.12",
    )
    if resolved_python is None:  # pragma: no cover - Prompt.ask always returns a string here.
        resolved_python = "3.12"

    selected_integrations = list(integrations)
    if not selected_integrations:
        typer.echo(f"Available integrations: {', '.join(registry.names())}")
        raw_integrations = Prompt.ask(
            "Integrations (comma-separated, blank for none)",
            default="",
            show_default=False,
        )
        selected_integrations = [
            item.strip() for item in raw_integrations.split(",") if item.strip()
        ]

    resolved_create_git = create_git or Confirm.ask("Create a Git repository?", default=False)

    return ProjectConfig(
        project_name=resolved_project_name,
        package_name=resolved_package_name,
        output_dir=output_dir,
        style=resolved_style,  # type: ignore[arg-type]
        python_version=resolved_python,
        integrations=tuple(selected_integrations),
        create_git=resolved_create_git,
        force=force,
    )
