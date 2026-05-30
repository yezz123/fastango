"""Rich table for supported generation models."""

from __future__ import annotations

from collections.abc import Iterable

from rich.table import Table

from fastango.generator.model_catalog import SupportedModel


def models_table(models: Iterable[SupportedModel]) -> Table:
    table = Table(title="Fastango Generation Models", border_style="fastango.accent")
    table.add_column("Provider", style="fastango.subtitle")
    table.add_column("Model", style="fastango.title")
    table.add_column("Source")
    table.add_column("Default")
    table.add_column("Description")
    for model in models:
        table.add_row(
            model.provider,
            model.model,
            model.source,
            "yes" if model.default else "",
            model.description,
        )
    return table
