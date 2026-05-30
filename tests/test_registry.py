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
