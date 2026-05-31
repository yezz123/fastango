from pathlib import Path

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine
from fastango.scaffold.plan import ScaffoldPlan
from fastango.scaffold.preview import build_preview
from fastango.scaffold.registry import IntegrationError, IntegrationRegistry


def test_registry_filters_by_category_and_search() -> None:
    registry = IntegrationRegistry.builtins()

    database_integrations = registry.list(category="database")
    search_results = registry.list(search="vector")

    assert {integration.name for integration in database_integrations} >= {
        "postgres",
        "sqlite",
        "pgvector",
    }
    assert {integration.name for integration in search_results} >= {"pgvector", "qdrant"}


def test_registry_resolves_aliases_and_presets() -> None:
    registry = IntegrationRegistry.builtins()
    config = ProjectConfig(project_name="api", integrations=("psql",), presets=("api-starter",))

    resolved = registry.resolve(config)

    assert {integration.name for integration in resolved} >= {
        "postgres",
        "openapi",
        "tests",
        "cors",
        "ruff",
        "pre-commit",
    }


def test_registry_rejects_conflicting_integrations() -> None:
    registry = IntegrationRegistry.builtins()
    config = ProjectConfig(project_name="api", integrations=("postgres", "sqlite"))

    try:
        registry.resolve(config)
    except IntegrationError as exc:
        assert "conflicts" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected integration conflict")


def test_preview_includes_preset_expansion() -> None:
    config = ProjectConfig(project_name="ai-api", presets=("ai-api",))

    preview = build_preview(config)

    assert "openai" in preview.integrations
    assert "anthropic" in preview.integrations
    assert "pgvector" in preview.integrations
    assert "OPENAI_API_KEY" in preview.env_vars


def test_cors_hook_renders_into_generated_main(tmp_path: Path) -> None:
    config = ProjectConfig(project_name="api", output_dir=tmp_path, integrations=("cors",))

    result = ScaffoldEngine().create(config)

    main_py = (result.target_dir / "app/main.py").read_text(encoding="utf-8")
    assert "CORSMiddleware" in main_py
    assert "app.add_middleware" in main_py


def test_catalog_integration_router_hooks_without_docs() -> None:
    from fastango.integrations.catalog import CatalogIntegration, IntegrationMetadata

    integration = CatalogIntegration(
        metadata=IntegrationMetadata(
            name="router",
            label="Router",
            category="test",
            description="Router",
            tags=(),
        ),
        openapi_tags=(("custom", "Custom tag"),),
        settings_fields=("custom_setting: str = 'x'",),
        middleware_hooks=("app.add_middleware(CustomMiddleware)",),
        lifespan_hooks=(("from app.custom import startup", "startup()"),),
        router_imports=("from app.custom import router",),
        router_includes=("app.include_router(router)",),
        compose_services=("  custom:\n    image: custom\n",),
        compose_volumes=("  custom-data:\n",),
    )
    plan = ScaffoldPlan(ProjectConfig(project_name="demo"))

    integration.apply(plan)

    assert plan.openapi_tags == [{"name": "custom", "description": "Custom tag"}]
    assert plan.settings_fields == ["custom_setting: str = 'x'"]
    assert plan.middleware_hooks == ["app.add_middleware(CustomMiddleware)"]
    assert plan.lifespan_imports == ["from app.custom import startup"]
    assert plan.lifespan_hooks == ["startup()"]
    assert plan.router_imports == ["from app.custom import router"]
    assert plan.compose_services == ["  custom:\n    image: custom\n"]
    assert plan.compose_volumes == ["  custom-data:\n"]
