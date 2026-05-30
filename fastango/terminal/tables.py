"""Rich tables for catalog and preview output."""

from __future__ import annotations

from collections.abc import Iterable

from rich.table import Table

from fastango.integrations.base import Integration
from fastango.integrations.catalog import Preset


def integrations_table(integrations: Iterable[Integration]) -> Table:
    table = Table(title="Fastango Integrations", border_style="fastango.accent")
    table.add_column("Name", style="fastango.title")
    table.add_column("Category", style="fastango.subtitle")
    table.add_column("Maturity")
    table.add_column("Tags", style="fastango.muted")
    table.add_column("Description")
    for integration in integrations:
        table.add_row(
            integration.name,
            integration.category,
            integration.maturity,
            ", ".join(integration.tags),
            integration.description,
        )
    return table


def presets_table(presets: Iterable[Preset]) -> Table:
    table = Table(title="Fastango Presets", border_style="fastango.accent")
    table.add_column("Name", style="fastango.title")
    table.add_column("Integrations", style="fastango.subtitle")
    table.add_column("Description")
    for preset in presets:
        table.add_row(preset.name, ", ".join(preset.integrations), preset.description)
    return table


def categories_table(integrations: Iterable[Integration]) -> Table:
    counts: dict[str, int] = {}
    for integration in integrations:
        counts[integration.category] = counts.get(integration.category, 0) + 1

    table = Table(title="Catalog Categories", border_style="fastango.accent")
    table.add_column("Category", style="fastango.title")
    table.add_column("Integrations", justify="right", style="fastango.success")
    for category, count in sorted(counts.items()):
        table.add_row(category, str(count))
    return table
