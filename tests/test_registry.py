from types import SimpleNamespace

import pytest

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.registry import IntegrationError, IntegrationRegistry


def test_registry_lists_builtin_integrations() -> None:
    registry = IntegrationRegistry.builtins()

    assert "authx" in registry.names()
    assert "stripe" in registry.names()
    assert "docker" in registry.names()


def test_registry_rejects_unknown_integration() -> None:
    registry = IntegrationRegistry.builtins()
    config = ProjectConfig(project_name="api", integrations=("unknown",))

    with pytest.raises(IntegrationError):
        registry.resolve(config)


def test_registry_categories_presets_and_errors() -> None:
    registry = IntegrationRegistry.builtins()

    assert "database" in registry.categories()
    assert "api-starter" in registry.preset_names()
    with pytest.raises(Exception, match="Unknown preset"):
        registry.get_preset("missing")
    with pytest.raises(Exception, match="Unknown integration"):
        registry.resolve(
            ProjectConfig(project_name="demo", style="simple", integrations=("missing",))
        )


def test_registry_unsupported_style_with_custom_integration() -> None:
    integration = IntegrationRegistry.builtins().get("openapi")
    custom = SimpleNamespace(
        **{
            "name": "custom",
            "label": "Custom",
            "category": "test",
            "description": "Custom",
            "tags": (),
            "supports": ("mvc",),
            "requires": (),
            "conflicts": (),
            "aliases": (),
            "maturity": "stable",
            "apply": lambda plan: None,
        }
    )
    registry = IntegrationRegistry({"openapi": integration, "custom": custom})

    with pytest.raises(Exception, match="does not support"):
        registry.resolve(
            ProjectConfig(project_name="demo", style="simple", integrations=("custom",))
        )
