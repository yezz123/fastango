"""API protocol integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

API_INTEGRATIONS = (
    docs_integration(
        name="graphql",
        label="GraphQL",
        category="api",
        description="Adds Strawberry GraphQL dependencies and routing guidance.",
        dependencies=("strawberry-graphql[fastapi]>=0.250.0",),
        tags=("graphql", "api", "schema"),
    ),
    docs_integration(
        name="websockets",
        label="WebSockets",
        category="api",
        description="Adds WebSocket endpoint guidance.",
        tags=("websocket", "realtime", "api"),
    ),
    docs_integration(
        name="sse",
        label="Server-Sent Events",
        category="api",
        description="Adds SSE streaming response guidance.",
        dependencies=("sse-starlette>=2.1.0",),
        tags=("streaming", "realtime", "api"),
    ),
    docs_integration(
        name="webhooks",
        label="Signed Webhooks",
        category="api",
        description="Adds generic signed webhook receiver guidance.",
        env_vars=(EnvVar("WEBHOOK_SECRET", "change-me", "Generic webhook signing secret."),),
        tags=("webhooks", "security", "api"),
    ),
    docs_integration(
        name="versioning",
        label="API Versioning",
        category="api",
        description="Adds `/api/v1` routing guidance.",
        tags=("routing", "versioning", "api"),
    ),
)
