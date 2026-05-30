"""Built-in integration registry."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from fastango.integrations.base import Integration
from fastango.integrations.builtins import BUILTIN_INTEGRATIONS
from fastango.integrations.catalog import PRESETS, Preset
from fastango.scaffold.config import ProjectConfig


class IntegrationError(ValueError):
    """Raised when requested integrations cannot be resolved."""


@dataclass(frozen=True)
class IntegrationRegistry:
    integrations: dict[str, Integration]

    @classmethod
    def builtins(cls) -> IntegrationRegistry:
        return cls({integration.name: integration for integration in BUILTIN_INTEGRATIONS})

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self.integrations))

    def categories(self) -> tuple[str, ...]:
        return tuple(sorted({integration.category for integration in self.integrations.values()}))

    def presets(self) -> tuple[Preset, ...]:
        return PRESETS

    def preset_names(self) -> tuple[str, ...]:
        return tuple(preset.name for preset in PRESETS)

    def get_preset(self, name: str) -> Preset:
        normalized = name.strip().lower()
        for preset in PRESETS:
            if preset.name == normalized:
                return preset
        available = ", ".join(self.preset_names())
        raise IntegrationError(f"Unknown preset '{name}'. Available: {available}.")

    def get(self, name: str) -> Integration:
        normalized = name.strip().lower().replace("_", "-")
        try:
            return self.integrations[normalized]
        except KeyError:
            for integration in self.integrations.values():
                if normalized in integration.aliases:
                    return integration
            available = ", ".join(self.names())
            raise IntegrationError(
                f"Unknown integration '{name}'. Available: {available}."
            ) from None

    def list(
        self,
        *,
        category: str | None = None,
        search: str | None = None,
    ) -> tuple[Integration, ...]:
        integrations = tuple(sorted(self.integrations.values(), key=lambda item: item.name))
        if category:
            normalized_category = category.strip().lower()
            integrations = tuple(
                integration
                for integration in integrations
                if integration.category == normalized_category
            )
        if search:
            query = search.strip().lower()
            integrations = tuple(
                integration
                for integration in integrations
                if query in integration.name
                or query in integration.label.lower()
                or query in integration.description.lower()
                or any(query in tag for tag in integration.tags)
            )
        return integrations

    def resolve(self, config: ProjectConfig) -> Sequence[Integration]:
        selected = list(config.integrations)
        for preset_name in config.presets:
            selected.extend(self.get_preset(preset_name).integrations)
        integrations: dict[str, Integration] = {}

        index = 0
        while index < len(selected):
            name = selected[index]
            integration = self.get(name)
            if config.style not in integration.supports:
                supported = ", ".join(integration.supports)
                raise IntegrationError(
                    f"Integration '{name}' does not support template '{config.style}'. "
                    f"Supported templates: {supported}."
                )

            for required in integration.requires:
                if required not in selected:
                    selected.append(required)

            integrations.setdefault(integration.name, integration)
            index += 1

        for integration in integrations.values():
            for conflict in integration.conflicts:
                if conflict in integrations:
                    raise IntegrationError(
                        f"Integration '{integration.name}' conflicts with '{conflict}'."
                    )

        return list(integrations.values())
