"""Rich previews for constrained generation plans."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from fastango.generator.models import GenerationPlan
from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.preview import build_preview


def plan_to_dict(plan: GenerationPlan) -> dict[str, Any]:
    return {
        "project_name": plan.project_name,
        "style": plan.style,
        "skills": plan.skills,
        "presets": plan.presets,
        "integrations": plan.integrations,
        "reasons": [{"name": reason.name, "reason": reason.reason} for reason in plan.reasons],
        "security_notes": plan.security_notes,
        "not_generated": plan.not_generated,
        "model": plan.model,
    }


def plan_to_json(plan: GenerationPlan) -> str:
    return json.dumps(plan_to_dict(plan), indent=2)


def generation_preview(
    plan: GenerationPlan,
    *,
    output_dir: Path,
    force: bool = False,
) -> Columns:
    config = plan.to_project_config(output_dir=output_dir, force=force)
    preview = build_preview(config)
    return Columns(
        [
            Panel(
                f"Project: {plan.project_name}\nTemplate: {plan.style}\n"
                f"Provider: {plan.provider}\nModel: {plan.model or 'n/a'}",
                title="Generation",
                border_style="fastango.accent",
            ),
            Panel(
                "\n".join([*plan.presets, *plan.integrations]) or "None",
                title="Selected Stack",
                border_style="fastango.subtitle",
            ),
            Panel(
                "\n".join(preview.files[:16]),
                title="Files",
                border_style="fastango.success",
            ),
        ],
        equal=True,
    )


def reasons_table(plan: GenerationPlan) -> Table:
    table = Table(title="Why Fastango selected this stack", border_style="fastango.accent")
    table.add_column("Item", style="fastango.title")
    table.add_column("Reason")
    for reason in plan.reasons:
        table.add_row(reason.name, reason.reason)
    return table


def security_table(plan: GenerationPlan) -> Table:
    table = Table(title="Security and Unsupported Notes", border_style="fastango.accent")
    table.add_column("Type", style="fastango.title")
    table.add_column("Note")
    for note in plan.security_notes:
        table.add_row("security", note)
    for note in plan.not_generated:
        table.add_row("not generated", note)
    return table


def config_from_plan(plan: GenerationPlan, output_dir: Path, force: bool = False) -> ProjectConfig:
    return plan.to_project_config(output_dir=output_dir, force=force)
