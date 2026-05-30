"""Integration protocol used by Fastango's scaffold registry."""

from __future__ import annotations

from typing import Literal, Protocol

from fastango.scaffold.plan import ScaffoldPlan

IntegrationMaturity = Literal["stable", "beta", "experimental"]


class Integration(Protocol):
    """A feature that can modify the generated FastAPI project."""

    name: str
    label: str
    category: str
    description: str
    tags: tuple[str, ...]
    supports: tuple[str, ...]
    requires: tuple[str, ...]
    conflicts: tuple[str, ...]
    aliases: tuple[str, ...]
    maturity: IntegrationMaturity

    def apply(self, plan: ScaffoldPlan) -> None:
        """Mutate the scaffold plan with files, dependencies, and docs."""
