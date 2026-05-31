"""Production-ready code-template integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

HEALTH_ROUTE = '''"""Production health and readiness routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}
'''

REQUEST_ID_MIDDLEWARE = '''"""Request ID middleware for traceable logs."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
'''

SENTRY_INIT = '''"""Sentry initialization helpers."""

import sentry_sdk

from app.core.config import settings


def init_sentry() -> None:
    if settings.sentry_dsn:
        sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)
'''

MAKEFILE = """test:
\tuv run pytest

lint:
\tuv run ruff check .

type:
\tuv run mypy app

dev:
\tuv run fastapi dev app/main.py
"""

PRECOMMIT_FULL = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-toml
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
"""

ALEMBIC_INI = """[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = %(DATABASE_URL)s
"""

ALEMBIC_ENV = '''"""Alembic environment placeholder."""

from alembic import context


def run_migrations_online() -> None:
    context.run_migrations()


run_migrations_online()
'''

PRODUCTION_INTEGRATIONS = (
    docs_integration(
        name="sqlalchemy-async",
        label="SQLAlchemy Async",
        category="production",
        description="Adds async SQLAlchemy session infrastructure.",
        dependencies=("sqlalchemy[asyncio]>=2.0.0", "asyncpg>=0.29.0"),
        env_vars=(
            EnvVar(
                "DATABASE_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/app",
                "Async database URL.",
            ),
        ),
        files=(
            ("app/core/database.py", '"""Async SQLAlchemy session dependency placeholder."""\n'),
        ),
        settings_fields=(
            'database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"',
        ),
        tags=("database", "sqlalchemy", "async"),
    ),
    docs_integration(
        name="alembic-code",
        label="Alembic Code",
        category="production",
        description="Adds Alembic migration files and uv commands.",
        dependencies=("alembic>=1.13.0",),
        files=(("alembic.ini", ALEMBIC_INI), ("alembic/env.py", ALEMBIC_ENV)),
        tags=("database", "migrations"),
        aliases=("alembic-template",),
    ),
    docs_integration(
        name="redis-cache-code",
        label="Redis Cache Code",
        category="production",
        description="Adds Redis cache settings and lifecycle guidance.",
        dependencies=("redis>=5.0.0",),
        env_vars=(EnvVar("REDIS_URL", "redis://localhost:6379/0", "Redis URL."),),
        settings_fields=('redis_url: str = "redis://localhost:6379/0"',),
        tags=("cache", "redis"),
    ),
    docs_integration(
        name="healthchecks-code",
        label="Healthchecks Code",
        category="production",
        description="Adds liveness and readiness routes.",
        files=(("app/api/routes/healthchecks.py", HEALTH_ROUTE),),
        router_imports=("from app.api.routes.healthchecks import router as healthchecks_router",),
        router_includes=("app.include_router(healthchecks_router)",),
        tags=("health", "readiness"),
    ),
    docs_integration(
        name="prometheus-code",
        label="Prometheus Code",
        category="production",
        description="Adds Prometheus FastAPI instrumentation.",
        dependencies=("prometheus-fastapi-instrumentator>=7.0.0",),
        main_imports=("from prometheus_fastapi_instrumentator import Instrumentator",),
        app_hooks=("Instrumentator().instrument(app).expose(app)",),
        tags=("metrics", "prometheus"),
    ),
    docs_integration(
        name="sentry-fastapi",
        label="Sentry FastAPI",
        category="production",
        description="Adds Sentry initialization through settings.",
        dependencies=("sentry-sdk[fastapi]>=2.13.0",),
        env_vars=(EnvVar("SENTRY_DSN", "", "Sentry DSN."),),
        files=(("app/core/sentry.py", SENTRY_INIT),),
        settings_fields=('sentry_dsn: str = ""',),
        lifespan_hooks=(("from app.core.sentry import init_sentry", "init_sentry()"),),
        tags=("errors", "monitoring"),
    ),
    docs_integration(
        name="request-id",
        label="Request ID",
        category="production",
        description="Adds request ID middleware and response header propagation.",
        files=(("app/middleware/request_id.py", REQUEST_ID_MIDDLEWARE),),
        main_imports=("from app.middleware.request_id import RequestIDMiddleware",),
        middleware_hooks=("app.add_middleware(RequestIDMiddleware)",),
        tags=("logging", "middleware", "trace"),
    ),
    docs_integration(
        name="makefile-full",
        label="Makefile Full",
        category="production",
        description="Adds a Makefile with common uv commands.",
        files=(("Makefile", MAKEFILE),),
        tags=("dx", "uv"),
    ),
    docs_integration(
        name="precommit-full",
        label="Pre-commit Full",
        category="production",
        description="Adds a complete pre-commit configuration.",
        dev_dependencies=("pre-commit>=4.0.0",),
        files=((".pre-commit-config.yaml", PRECOMMIT_FULL),),
        tags=("quality", "git"),
    ),
)
