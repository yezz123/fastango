"""Data-driven integration catalog primitives."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastango.integrations.base import IntegrationMaturity
from fastango.scaffold.plan import EnvVar, ScaffoldPlan


@dataclass(frozen=True)
class IntegrationMetadata:
    name: str
    label: str
    category: str
    description: str
    tags: tuple[str, ...]
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    maturity: IntegrationMaturity = "stable"


@dataclass(frozen=True)
class CatalogIntegration:
    """Declarative integration for dependency/env/docs-first features."""

    metadata: IntegrationMetadata
    dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    env_vars: tuple[EnvVar, ...] = ()
    files: tuple[tuple[str, str], ...] = ()
    readme: str = ""
    llms: str = ""
    openapi_tags: tuple[tuple[str, str], ...] = ()
    main_imports: tuple[str, ...] = ()
    app_hooks: tuple[str, ...] = ()
    settings_fields: tuple[str, ...] = ()
    middleware_hooks: tuple[str, ...] = ()
    lifespan_hooks: tuple[tuple[str, str], ...] = ()
    router_imports: tuple[str, ...] = ()
    router_includes: tuple[str, ...] = ()
    compose_services: tuple[str, ...] = ()
    compose_volumes: tuple[str, ...] = ()

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def label(self) -> str:
        return self.metadata.label

    @property
    def category(self) -> str:
        return self.metadata.category

    @property
    def description(self) -> str:
        return self.metadata.description

    @property
    def tags(self) -> tuple[str, ...]:
        return self.metadata.tags

    @property
    def supports(self) -> tuple[str, ...]:
        return self.metadata.supports

    @property
    def requires(self) -> tuple[str, ...]:
        return self.metadata.requires

    @property
    def conflicts(self) -> tuple[str, ...]:
        return self.metadata.conflicts

    @property
    def aliases(self) -> tuple[str, ...]:
        return self.metadata.aliases

    @property
    def maturity(self) -> IntegrationMaturity:
        return self.metadata.maturity

    def apply(self, plan: ScaffoldPlan) -> None:
        for dependency in self.dependencies:
            plan.add_dependency(dependency)
        for dependency in self.dev_dependencies:
            plan.add_dev_dependency(dependency)
        for env_var in self.env_vars:
            plan.add_env_var(env_var)
        for path, content in self.files:
            plan.add_file(path, content)
        for name, description in self.openapi_tags:
            plan.add_openapi_tag(name, description)
        for import_line in self.main_imports:
            plan.add_main_import(import_line)
        for statement in self.app_hooks:
            plan.add_app_hook(statement)
        for settings_field in self.settings_fields:
            plan.add_settings_field(settings_field)
        for statement in self.middleware_hooks:
            plan.add_middleware_hook(statement)
        for import_line, statement in self.lifespan_hooks:
            plan.add_lifespan_hook(import_line, statement)
        for import_line, include_statement in zip(
            self.router_imports, self.router_includes, strict=False
        ):
            plan.add_router(import_line, include_statement)
        for service in self.compose_services:
            plan.add_compose_service(service)
        for volume in self.compose_volumes:
            plan.add_compose_volume(volume)
        if self.readme:
            plan.add_readme_section(self.readme)
        if self.llms:
            plan.add_llms_section(self.llms)


@dataclass(frozen=True)
class Preset:
    name: str
    label: str
    description: str
    integrations: tuple[str, ...]
    tags: tuple[str, ...] = field(default_factory=tuple)


PRESETS: tuple[Preset, ...] = (
    Preset(
        name="api-starter",
        label="API Starter",
        description="FastAPI docs, tests, CORS, Ruff, and pre-commit defaults.",
        integrations=("openapi", "tests", "cors", "ruff", "pre-commit"),
        tags=("starter", "api", "quality"),
    ),
    Preset(
        name="saas",
        label="SaaS",
        description="Auth, billing, database, cache, email, analytics, monitoring, and Docker.",
        integrations=(
            "authx",
            "stripe",
            "postgres",
            "redis",
            "resend",
            "posthog",
            "sentry",
            "docker",
        ),
        tags=("saas", "billing", "production"),
    ),
    Preset(
        name="ai-api",
        label="AI API",
        description="LLM providers, vector-ready Postgres, cache, tests, and Docker.",
        integrations=("openai", "anthropic", "pgvector", "postgres", "redis", "tests", "docker"),
        tags=("ai", "llm", "rag"),
    ),
    Preset(
        name="data-api",
        label="Data API",
        description="Postgres, migrations, Redis, Celery, metrics, and tracing.",
        integrations=("postgres", "alembic", "redis", "celery", "prometheus", "opentelemetry"),
        tags=("data", "workers", "observability"),
    ),
    Preset(
        name="production",
        label="Production",
        description="Docker, CI, security headers, Sentry, Prometheus, and health checks.",
        integrations=(
            "docker",
            "github-actions",
            "security-headers",
            "sentry",
            "prometheus",
            "healthchecks",
        ),
        tags=("deploy", "security", "monitoring"),
    ),
)


def docs_integration(
    *,
    name: str,
    label: str,
    category: str,
    description: str,
    dependencies: tuple[str, ...] = (),
    dev_dependencies: tuple[str, ...] = (),
    env_vars: tuple[EnvVar, ...] = (),
    tags: tuple[str, ...] = (),
    requires: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    aliases: tuple[str, ...] = (),
    maturity: IntegrationMaturity = "stable",
    readme: str | None = None,
    llms: str | None = None,
    files: tuple[tuple[str, str], ...] = (),
    openapi_tags: tuple[tuple[str, str], ...] = (),
    main_imports: tuple[str, ...] = (),
    app_hooks: tuple[str, ...] = (),
    settings_fields: tuple[str, ...] = (),
    middleware_hooks: tuple[str, ...] = (),
    lifespan_hooks: tuple[tuple[str, str], ...] = (),
    router_imports: tuple[str, ...] = (),
    router_includes: tuple[str, ...] = (),
    compose_services: tuple[str, ...] = (),
    compose_volumes: tuple[str, ...] = (),
) -> CatalogIntegration:
    """Create a docs-first integration with consistent README and llms guidance."""

    title = label
    readme_text = readme or (
        f"### {title}\n\n{description} Fastango added dependencies, environment placeholders, "
        "and project guidance. Fill in provider-specific credentials before using it in production."
    )
    llms_text = llms or (
        f"{title} is enabled. Keep provider credentials in the generated settings model, "
        "add tests around any new routes, and prefer small service modules over logic in handlers."
    )
    return CatalogIntegration(
        metadata=IntegrationMetadata(
            name=name,
            label=label,
            category=category,
            description=description,
            tags=tags,
            requires=requires,
            conflicts=conflicts,
            aliases=aliases,
            maturity=maturity,
        ),
        dependencies=dependencies,
        dev_dependencies=dev_dependencies,
        env_vars=env_vars,
        files=files,
        readme=readme_text,
        llms=llms_text,
        openapi_tags=openapi_tags,
        main_imports=main_imports,
        app_hooks=app_hooks,
        settings_fields=settings_fields,
        middleware_hooks=middleware_hooks,
        lifespan_hooks=lifespan_hooks,
        router_imports=router_imports,
        router_includes=router_includes,
        compose_services=compose_services,
        compose_volumes=compose_volumes,
    )
