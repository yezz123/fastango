"""Observability integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

OBSERVABILITY_INTEGRATIONS = (
    docs_integration(
        name="opentelemetry",
        label="OpenTelemetry",
        category="observability",
        description="Adds OpenTelemetry tracing dependencies.",
        dependencies=(
            "opentelemetry-api>=1.28.0",
            "opentelemetry-sdk>=1.28.0",
            "opentelemetry-instrumentation-fastapi>=0.49b0",
        ),
        env_vars=(EnvVar("OTEL_EXPORTER_OTLP_ENDPOINT", "", "OTLP collector endpoint."),),
        tags=("tracing", "metrics", "observability"),
        aliases=("otel",),
    ),
    docs_integration(
        name="prometheus",
        label="Prometheus",
        category="observability",
        description="Adds Prometheus metrics dependencies.",
        dependencies=("prometheus-fastapi-instrumentator>=7.0.0",),
        tags=("metrics", "monitoring", "prometheus"),
    ),
    docs_integration(
        name="structlog",
        label="Structlog",
        category="observability",
        description="Adds structured logging dependencies.",
        dependencies=("structlog>=24.4.0",),
        tags=("logging", "json", "observability"),
    ),
    docs_integration(
        name="logfire",
        label="Pydantic Logfire",
        category="observability",
        description="Adds Pydantic Logfire instrumentation settings.",
        dependencies=("logfire[fastapi]>=2.0.0",),
        env_vars=(EnvVar("LOGFIRE_TOKEN", "", "Logfire write token."),),
        tags=("logging", "pydantic", "observability"),
        maturity="beta",
    ),
    docs_integration(
        name="healthchecks",
        label="Health Checks",
        category="observability",
        description="Adds deeper liveness/readiness probe guidance.",
        tags=("health", "readiness", "monitoring"),
    ),
)
