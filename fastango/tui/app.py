"""Rich-powered terminal playground for creating FastAPI projects."""

from __future__ import annotations

from pathlib import Path

from rich.columns import Columns
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.table import Table

from fastango.scaffold.config import ProjectConfig, normalize_package_name
from fastango.scaffold.preview import build_preview
from fastango.scaffold.registry import IntegrationRegistry
from fastango.terminal.tables import categories_table, integrations_table, presets_table
from fastango.terminal.theme import brand_panel, make_console


def _hero_panels() -> Columns:
    return Columns(
        [
            Panel(
                "Simple or MVC FastAPI templates\nuv-first dependencies\nGenerated tests and llms.txt",
                title="Scaffold",
                border_style="fastango.accent",
            ),
            Panel(
                "Searchable catalog\nPresets for SaaS, AI, data, production\nConflict-aware selection",
                title="Integrations",
                border_style="fastango.subtitle",
            ),
            Panel(
                "Live file preview\nEnvironment variables\nNext commands before writing",
                title="Preview",
                border_style="fastango.success",
            ),
        ],
        equal=True,
    )


def _steps_table() -> Table:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="fastango.title")
    table.add_column(style="fastango.muted")
    table.add_row("1", "Name the project and choose a template.")
    table.add_row("2", "Pick presets and browse integrations by category or search.")
    table.add_row("3", "Review generated files, dependencies, and env vars.")
    table.add_row("4", "Generate the project and follow the uv next steps.")
    return table


def run_playground(
    *,
    registry: IntegrationRegistry,
    output_dir: Path,
    force: bool = False,
) -> ProjectConfig | None:
    """Run the branded terminal playground and return a selected config."""

    console = make_console()
    console.print(
        brand_panel(
            "A terminal-first playground for building production-ready FastAPI projects.",
            title="Fastango",
        )
    )
    console.print(_hero_panels())
    console.print(Panel(_steps_table(), title="How It Works", border_style="fastango.accent"))
    console.print(Rule("[fastango.title]Project Basics[/]"))

    project_name = Prompt.ask("[fastango.title]Project name[/]", default="my-api")
    package_name = Prompt.ask(
        "[fastango.title]Package name[/]",
        default=normalize_package_name(project_name),
    )
    style = Prompt.ask(
        "[fastango.title]Template style[/]",
        choices=["simple", "mvc"],
        default="mvc",
    )
    python_version = Prompt.ask(
        "[fastango.title]Python version[/]",
        choices=["3.10", "3.11", "3.12", "3.13"],
        default="3.12",
    )

    console.print(Rule("[fastango.title]Preset Library[/]"))
    console.print(presets_table(registry.presets()))
    preset_text = Prompt.ask(
        "[fastango.title]Presets[/] [fastango.muted](comma-separated, blank for none)[/]",
        default="",
        show_default=False,
    )
    presets = tuple(item.strip() for item in preset_text.split(",") if item.strip())

    console.print(Rule("[fastango.title]Integration Browser[/]"))
    console.print(categories_table(registry.list()))
    category = Prompt.ask(
        "[fastango.title]Filter category[/] [fastango.muted](blank for all)[/]",
        default="",
        show_default=False,
    )
    search = Prompt.ask(
        "[fastango.title]Search integrations[/] [fastango.muted](blank for all)[/]",
        default="",
        show_default=False,
    )
    filtered_integrations = registry.list(
        category=category or None,
        search=search or None,
    )
    console.print(integrations_table(filtered_integrations))
    integration_text = Prompt.ask(
        "[fastango.title]Extra integrations[/] [fastango.muted](comma-separated, blank for none)[/]",
        default="",
        show_default=False,
    )
    integrations = tuple(item.strip() for item in integration_text.split(",") if item.strip())

    config = ProjectConfig(
        project_name=project_name,
        package_name=package_name,
        output_dir=output_dir,
        style=style,  # type: ignore[arg-type]
        python_version=python_version,
        integrations=integrations,
        presets=presets,
        force=force,
    )
    preview = build_preview(config)
    console.print(Rule("[fastango.title]Live Preview[/]"))
    console.print(
        Columns(
            [
                Panel(
                    "\n".join(preview.integrations) or "None",
                    title="Integrations",
                    border_style="fastango.accent",
                ),
                Panel(
                    "\n".join(preview.dependencies[:12]),
                    title="Dependencies",
                    border_style="fastango.subtitle",
                ),
                Panel(
                    "\n".join(preview.files[:18]),
                    title="Files",
                    border_style="fastango.success",
                ),
            ],
            equal=True,
        )
    )
    console.print(
        Panel(
            "\n".join(preview.env_vars) or "No environment variables",
            title="Environment Variables",
            border_style="fastango.muted",
        )
    )

    console.print(Rule("[fastango.title]Confirmation[/]"))
    create_git = Confirm.ask("[fastango.title]Create a Git repository?[/]", default=False)
    config.create_git = create_git
    if not Confirm.ask("[fastango.title]Generate this project?[/]", default=True):
        return None
    return config
