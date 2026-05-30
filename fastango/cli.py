"""Command-line interface for Fastango."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.prompt import Confirm

from fastango import __version__
from fastango.generator.constraints import GenerationConstraintError
from fastango.generator.model_catalog import ModelProvider, available_models
from fastango.generator.models import GenerationProvider, GenerationRequest
from fastango.generator.planner import build_generation_plan
from fastango.generator.preview import (
    generation_preview,
    plan_to_json,
    reasons_table,
    security_table,
)
from fastango.generator.providers.base import ProviderError
from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine
from fastango.scaffold.filesystem import ScaffoldWriteError
from fastango.scaffold.prompts import prompt_for_config
from fastango.scaffold.registry import IntegrationError, IntegrationRegistry
from fastango.terminal.models import models_table
from fastango.terminal.tables import integrations_table, presets_table
from fastango.terminal.theme import make_console
from fastango.tui.app import run_playground

app = typer.Typer(
    help="Generate FastAPI projects with uv-first templates.",
    invoke_without_command=True,
    no_args_is_help=False,
)
console = make_console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"fastango {__version__}")
        raise typer.Exit


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, help="Show Fastango version."),
    ] = None,
) -> None:
    """Fastango CLI root command."""

    if ctx.invoked_subcommand is None:
        launch_playground(output_dir=Path.cwd(), dry_run=False, force=False)


def launch_playground(*, output_dir: Path, dry_run: bool, force: bool) -> None:
    registry = IntegrationRegistry.builtins()
    config = run_playground(registry=registry, output_dir=output_dir, force=force)
    if config is None:
        console.print("[fastango.muted]Cancelled.[/]")
        raise typer.Exit
    result = ScaffoldEngine(registry=registry).create(config, dry_run=dry_run)
    if dry_run:
        console.print(
            f"[fastango.success]Dry run complete.[/] {len(result.files)} files would be generated:"
        )
        for path in result.files:
            console.print(f"  {path.relative_to(result.target_dir)}")
        return
    console.print(f"[fastango.success]Created FastAPI project at {result.target_dir}[/]")
    console.print("\nNext steps:")
    console.print(f"  cd {result.target_dir}")
    console.print("  uv sync")
    console.print("  cp .env.example .env")
    console.print("  uv run fastapi dev app/main.py")


@app.command("integrations")
def integrations(
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Filter integrations by category."),
    ] = None,
    search: Annotated[
        str | None,
        typer.Option("--search", "-s", help="Search integrations by name, tag, or description."),
    ] = None,
    show_presets: Annotated[
        bool,
        typer.Option("--presets", help="Show curated presets instead of integrations."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print machine-readable JSON."),
    ] = False,
) -> None:
    """List built-in integrations."""

    registry = IntegrationRegistry.builtins()
    if show_presets:
        presets = registry.presets()
        if json_output:
            console.print_json(
                json.dumps(
                    [
                        {
                            "name": preset.name,
                            "label": preset.label,
                            "description": preset.description,
                            "integrations": preset.integrations,
                            "tags": preset.tags,
                        }
                        for preset in presets
                    ]
                )
            )
            return
        console.print(presets_table(presets))
        return

    filtered = registry.list(category=category, search=search)
    if json_output:
        console.print_json(
            json.dumps(
                [
                    {
                        "name": integration.name,
                        "label": integration.label,
                        "category": integration.category,
                        "description": integration.description,
                        "tags": integration.tags,
                        "supports": integration.supports,
                        "requires": integration.requires,
                        "conflicts": integration.conflicts,
                        "aliases": integration.aliases,
                        "maturity": integration.maturity,
                    }
                    for integration in filtered
                ]
            )
        )
        return
    console.print(integrations_table(filtered))


@app.command()
def playground(
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", "-o", help="Parent directory for the generated project."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview the selected project without writing files."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite files if they already exist."),
    ] = False,
) -> None:
    """Launch the branded interactive Fastango playground."""

    launch_playground(output_dir=output_dir or Path.cwd(), dry_run=dry_run, force=force)


@app.command("models")
def models(
    provider: Annotated[
        ModelProvider | None,
        typer.Option("--provider", help="Filter models by provider: anthropic or openai."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print supported models as JSON."),
    ] = False,
    static: Annotated[
        bool,
        typer.Option("--static", help="Show Fastango's curated offline model list."),
    ] = False,
) -> None:
    """List AI generation models from API keys, with curated fallback."""

    supported = available_models(provider, live=not static)
    if json_output:
        console.print_json(
            json.dumps(
                [
                    {
                        "provider": model.provider,
                        "model": model.model,
                        "label": model.label,
                        "description": model.description,
                        "default": model.default,
                        "source": model.source,
                    }
                    for model in supported
                ]
            )
        )
        return
    console.print(models_table(supported))


@app.command()
def generate(
    prompt: Annotated[
        str,
        typer.Argument(help="Natural-language FastAPI project idea."),
    ],
    provider: Annotated[
        GenerationProvider,
        typer.Option(
            "--provider",
            help="Generation provider: deterministic, anthropic, openai, or auto.",
        ),
    ] = "deterministic",
    model: Annotated[
        str | None,
        typer.Option("--model", help="Supported model ID for Anthropic/OpenAI providers."),
    ] = None,
    style: Annotated[
        str | None,
        typer.Option("--style", help="Template style: simple or mvc."),
    ] = None,
    project_name: Annotated[
        str | None,
        typer.Option("--project-name", help="Project name to use instead of inferring one."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", "-o", help="Parent directory for the generated project."),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Generate without an interactive confirmation."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview files without writing them."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Print the generation plan as JSON."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite files if they already exist."),
    ] = False,
    allow_experimental_suggestions: Annotated[
        bool,
        typer.Option(
            "--allow-experimental-suggestions",
            help="Keep unsupported provider suggestions as notes instead of failing.",
        ),
    ] = False,
) -> None:
    """Generate a constrained FastAPI project from a natural-language prompt."""

    resolved_output_dir = output_dir or Path.cwd()
    try:
        request = GenerationRequest(
            prompt=prompt,
            provider=provider,
            model=model,
            style=style,  # type: ignore[arg-type]
            project_name=project_name,
            output_dir=resolved_output_dir,
            yes=yes,
            dry_run=dry_run,
            json_output=json_output,
            force=force,
            allow_experimental_suggestions=allow_experimental_suggestions,
        )
        plan = build_generation_plan(request)
    except (GenerationConstraintError, IntegrationError, ProviderError, ValueError) as exc:
        console.print(f"[fastango.error]Error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        console.print_json(plan_to_json(plan))
        if dry_run:
            return

    if not json_output:
        console.print(generation_preview(plan, output_dir=resolved_output_dir, force=force))
        console.print(reasons_table(plan))
        console.print(security_table(plan))

    if (
        not yes
        and not dry_run
        and not Confirm.ask(
            "[fastango.title]Generate this constrained FastAPI project?[/]", default=True
        )
    ):
        console.print("[fastango.muted]Cancelled.[/]")
        raise typer.Exit

    config = plan.to_project_config(output_dir=resolved_output_dir, force=force)
    result = ScaffoldEngine().create(config, dry_run=dry_run)
    if dry_run:
        console.print(
            f"[fastango.success]Dry run complete.[/] {len(result.files)} files would be generated:"
        )
        for path in result.files:
            console.print(f"  {path.relative_to(result.target_dir)}")
        return

    console.print(f"[fastango.success]Generated FastAPI project at {result.target_dir}[/]")
    console.print("\nNext steps:")
    console.print(f"  cd {result.target_dir}")
    console.print("  uv sync")
    console.print("  cp .env.example .env")
    console.print("  uv run fastapi dev app/main.py")


@app.command()
def create(
    project_name: Annotated[
        str | None,
        typer.Argument(help="Project name and destination directory."),
    ] = None,
    package_name: Annotated[
        str | None,
        typer.Option("--package-name", help="Python package name for generated imports."),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", "-o", help="Parent directory for the generated project."),
    ] = None,
    style: Annotated[
        str,
        typer.Option("--style", help="Template style: simple or mvc."),
    ] = "simple",
    python_version: Annotated[
        str,
        typer.Option("--python", help="Python version for the generated project."),
    ] = "3.12",
    integration: Annotated[
        list[str] | None,
        typer.Option("--integration", "-i", help="Integration to include. Repeat this option."),
    ] = None,
    preset: Annotated[
        list[str] | None,
        typer.Option("--preset", "-p", help="Curated preset to include. Repeat this option."),
    ] = None,
    with_docker: Annotated[
        bool,
        typer.Option("--with-docker", help="Shortcut for --integration docker."),
    ] = False,
    create_git: Annotated[
        bool,
        typer.Option(
            "--git/--no-git", help="Initialize a Git repository in the generated project."
        ),
    ] = False,
    interactive: Annotated[
        bool,
        typer.Option("--interactive/--no-interactive", help="Prompt for missing choices."),
    ] = True,
    basic: Annotated[
        bool,
        typer.Option("--basic", help="Use basic prompts instead of the branded playground."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print files that would be generated without writing them."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite files if they already exist."),
    ] = False,
) -> None:
    """Create a new FastAPI project."""

    registry = IntegrationRegistry.builtins()
    resolved_output_dir = output_dir or Path.cwd()
    selected_integrations = list(integration or [])
    if with_docker:
        selected_integrations.append("docker")

    try:
        if interactive and project_name is None and not basic:
            config = run_playground(registry=registry, output_dir=resolved_output_dir, force=force)
            if config is None:
                console.print("[fastango.muted]Cancelled.[/]")
                raise typer.Exit
        elif interactive and project_name is None:
            config = prompt_for_config(
                project_name=project_name,
                package_name=package_name,
                output_dir=resolved_output_dir,
                style=style,
                python_version=python_version,
                integrations=tuple(selected_integrations),
                create_git=create_git,
                force=force,
                registry=registry,
            )
        else:
            if project_name is None:
                raise typer.BadParameter("PROJECT_NAME is required when --no-interactive is used.")
            config = ProjectConfig(
                project_name=project_name,
                package_name=package_name,
                output_dir=resolved_output_dir,
                style=style,  # type: ignore[arg-type]
                python_version=python_version,
                integrations=tuple(selected_integrations),
                presets=tuple(preset or []),
                create_git=create_git,
                force=force,
            )

        result = ScaffoldEngine(registry=registry).create(config, dry_run=dry_run)
    except (IntegrationError, ScaffoldWriteError, ValueError) as exc:
        console.print(f"[fastango.error]Error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if dry_run:
        console.print(
            f"[fastango.success]Dry run complete.[/] {len(result.files)} files would be generated:"
        )
        for path in result.files:
            console.print(f"  {path.relative_to(result.target_dir)}")
        return

    console.print(f"[fastango.success]Created FastAPI project at {result.target_dir}[/]")
    console.print("\nNext steps:")
    console.print(f"  cd {result.target_dir}")
    console.print("  uv sync")
    console.print("  cp .env.example .env")
    console.print("  uv run fastapi dev app/main.py")
