"""Built-in Fastango integrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from fastango.integrations.base import Integration, IntegrationMaturity
from fastango.integrations.categories.ai import AI_INTEGRATIONS
from fastango.integrations.categories.api import API_INTEGRATIONS
from fastango.integrations.categories.auth import AUTH_INTEGRATIONS
from fastango.integrations.categories.cache_queue import CACHE_QUEUE_INTEGRATIONS
from fastango.integrations.categories.database import DATABASE_INTEGRATIONS
from fastango.integrations.categories.deploy import DEPLOY_INTEGRATIONS
from fastango.integrations.categories.devtools import DEVTOOLS_INTEGRATIONS
from fastango.integrations.categories.observability import OBSERVABILITY_INTEGRATIONS
from fastango.integrations.categories.payments import PAYMENTS_INTEGRATIONS
from fastango.integrations.categories.product import PRODUCT_INTEGRATIONS
from fastango.integrations.categories.storage import STORAGE_INTEGRATIONS
from fastango.scaffold.plan import EnvVar, ScaffoldPlan


@dataclass(frozen=True)
class OpenAPIIntegration:
    name: str = "openapi"
    label: str = "OpenAPI"
    category: str = "api"
    description: str = "Adds richer OpenAPI metadata and route tags."
    tags: tuple[str, ...] = ("docs", "schema", "api")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ("docs", "swagger")
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_openapi_tag("root", "Application metadata and welcome endpoints.")
        plan.add_readme_section(
            "### OpenAPI\n\nInteractive API docs are available at `/docs` and ReDoc at `/redoc`. "
            "Route tags are generated from the selected Fastango integrations."
        )
        plan.add_llms_section(
            "When adding endpoints, include useful `tags`, `summary`, and `response_model` values "
            "so generated OpenAPI docs stay helpful."
        )


@dataclass(frozen=True)
class TestsIntegration:
    name: str = "tests"
    label: str = "Tests"
    category: str = "devtools"
    description: str = "Adds pytest, HTTPX, Ruff, and coverage-friendly defaults."
    tags: tuple[str, ...] = ("tests", "quality", "pytest")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ("test",)
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_dev_dependency("pytest-cov>=5.0.0")
        plan.add_readme_section(
            "### Testing\n\nRun the generated test suite with `uv run pytest`. "
            "Use `uv run ruff check .` before committing changes."
        )
        plan.add_llms_section(
            "Tests use pytest and HTTPX's ASGI transport. Add tests for every new route under `tests/`."
        )


@dataclass(frozen=True)
class AuthXIntegration:
    name: str = "authx"
    label: str = "AuthX"
    category: str = "auth"
    description: str = "Adds AuthX settings and a protected route example."
    tags: tuple[str, ...] = ("auth", "jwt", "security")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ("jwt", "fastapi-users")
    aliases: tuple[str, ...] = ("auth",)
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_dependency("authx>=1.4.0")
        plan.add_env_var(EnvVar("JWT_SECRET_KEY", "change-me", "Secret key used to sign JWTs."))
        plan.add_env_var(
            EnvVar("JWT_ACCESS_TOKEN_EXPIRES", "900", "Access-token lifetime in seconds.")
        )
        plan.add_openapi_tag("auth", "Authentication and protected route examples.")
        if plan.config.style == "simple":
            plan.add_file(
                "app/auth.py",
                SIMPLE_AUTH_FILE,
            )
            plan.add_file(
                "tests/test_auth.py",
                SIMPLE_AUTH_TEST,
            )
        else:
            plan.add_file(
                "app/core/security.py",
                MVC_SECURITY_FILE,
            )
            plan.add_file(
                "app/api/routes/auth.py",
                MVC_AUTH_ROUTE,
            )
            plan.add_file(
                "tests/test_auth.py",
                MVC_AUTH_TEST,
            )
        plan.add_readme_section(
            "### AuthX\n\nAuthX scaffolding is included with a protected example endpoint. "
            "Set `JWT_SECRET_KEY` in `.env` before using real credentials."
        )
        plan.add_llms_section(
            "Auth is implemented with AuthX. Keep token settings in the generated settings model "
            "and avoid hardcoding JWT secrets in route modules."
        )


@dataclass(frozen=True)
class StripeIntegration:
    name: str = "stripe"
    label: str = "Stripe"
    category: str = "payments"
    description: str = "Adds Stripe checkout and webhook scaffolding."
    tags: tuple[str, ...] = ("billing", "payments", "webhooks")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ("paddle", "polar", "lemonsqueezy")
    aliases: tuple[str, ...] = ("billing",)
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_dependency("stripe>=11.0.0")
        plan.add_env_var(EnvVar("STRIPE_SECRET_KEY", "", "Stripe API secret key."))
        plan.add_env_var(EnvVar("STRIPE_WEBHOOK_SECRET", "", "Stripe webhook signing secret."))
        plan.add_openapi_tag("billing", "Stripe checkout and webhook endpoints.")
        if plan.config.style == "simple":
            plan.add_file("app/stripe_routes.py", SIMPLE_STRIPE_ROUTES)
        else:
            plan.add_file("app/api/routes/billing.py", MVC_STRIPE_ROUTES)
            plan.add_file("app/services/billing.py", MVC_STRIPE_SERVICE)
        plan.add_file("tests/test_stripe.py", STRIPE_TEST)
        plan.add_readme_section(
            "### Stripe\n\nSet `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`, then wire product "
            "and price IDs into your application-specific billing service."
        )
        plan.add_llms_section(
            "Stripe webhook handlers must verify signatures with `STRIPE_WEBHOOK_SECRET` before "
            "trusting payload data."
        )


@dataclass(frozen=True)
class PostgresIntegration:
    name: str = "postgres"
    label: str = "Postgres"
    category: str = "database"
    description: str = "Adds async SQLAlchemy Postgres connection scaffolding."
    tags: tuple[str, ...] = ("database", "sqlalchemy", "async")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ("sqlite", "mysql", "mongodb", "tortoise")
    aliases: tuple[str, ...] = ("postgresql", "psql")
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_dependency("sqlalchemy[asyncio]>=2.0.0")
        plan.add_dependency("asyncpg>=0.29.0")
        package_name = plan.config.package_name or "app"
        plan.add_env_var(
            EnvVar(
                "DATABASE_URL",
                f"postgresql+asyncpg://postgres:postgres@localhost:5432/{package_name}",
                "Async SQLAlchemy database URL.",
            )
        )
        plan.add_openapi_tag("database", "Database health and repository-backed endpoints.")
        if plan.config.style == "simple":
            plan.add_file("app/database.py", SIMPLE_DATABASE_FILE)
        else:
            plan.add_file("app/core/database.py", MVC_DATABASE_FILE)
        plan.add_readme_section(
            "### Postgres\n\nThe generated project uses SQLAlchemy asyncio with `asyncpg`. "
            "Add migrations with Alembic when you introduce persistent models."
        )
        plan.add_llms_section(
            "Use SQLAlchemy async sessions for database access. Keep database setup in the generated "
            "database module and avoid opening engines inside route handlers."
        )


@dataclass(frozen=True)
class RedisIntegration:
    name: str = "redis"
    label: str = "Redis"
    category: str = "cache-queue"
    description: str = "Adds Redis client settings and health-check scaffolding."
    tags: tuple[str, ...] = ("cache", "redis", "queue")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ("cache",)
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_dependency("redis>=5.0.0")
        plan.add_env_var(EnvVar("REDIS_URL", "redis://localhost:6379/0", "Redis connection URL."))
        if plan.config.style == "simple":
            plan.add_file("app/cache.py", SIMPLE_CACHE_FILE)
        else:
            plan.add_file("app/core/cache.py", MVC_CACHE_FILE)
        plan.add_readme_section(
            "### Redis\n\nRedis settings are ready for caching, queues, sessions, or rate limiting. "
            "Use `REDIS_URL` to configure the target instance."
        )
        plan.add_llms_section(
            "Use the generated Redis helper for cache access. Close Redis clients during application shutdown."
        )


@dataclass(frozen=True)
class DockerIntegration:
    name: str = "docker"
    label: str = "Docker"
    category: str = "deploy"
    description: str = "Adds a Dockerfile, compose file, and docker ignore rules."
    tags: tuple[str, ...] = ("deploy", "container", "compose")
    supports: tuple[str, ...] = ("simple", "mvc")
    requires: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ("container",)
    maturity: IntegrationMaturity = "stable"

    def apply(self, plan: ScaffoldPlan) -> None:
        plan.add_file("Dockerfile", DOCKERFILE)
        plan.add_file("docker-compose.yml", DOCKER_COMPOSE)
        plan.add_file(".dockerignore", DOCKERIGNORE)
        plan.add_readme_section(
            "### Docker\n\nBuild and run the service with `docker compose up --build`."
        )
        plan.add_llms_section(
            "Docker support uses uv inside the image. Keep generated runtime commands aligned with `pyproject.toml`."
        )


SIMPLE_AUTH_FILE = '''"""AuthX helpers for the simple template."""

from authx import AuthX, AuthXConfig

from app.settings import settings

config = AuthXConfig(
    JWT_SECRET_KEY=settings.jwt_secret_key,
    JWT_ACCESS_TOKEN_EXPIRES=settings.jwt_access_token_expires,
)
security = AuthX(config=config)
'''

SIMPLE_AUTH_TEST = """from fastapi.testclient import TestClient

from app.main import app


def test_protected_route_requires_credentials() -> None:
    client = TestClient(app)
    response = client.get("/protected")

    assert response.status_code in {401, 403}
"""

MVC_SECURITY_FILE = SIMPLE_AUTH_FILE.replace("from app.settings", "from app.core.config")

MVC_AUTH_ROUTE = '''"""Authentication route examples."""

from fastapi import APIRouter, Depends

from app.core.security import security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/protected")
async def protected(_: object = Depends(security.access_token_required)) -> dict[str, str]:
    return {"message": "You are authenticated."}
'''

MVC_AUTH_TEST = """from fastapi.testclient import TestClient

from app.main import app


def test_protected_route_requires_credentials() -> None:
    client = TestClient(app)
    response = client.get("/auth/protected")

    assert response.status_code in {401, 403}
"""

SIMPLE_STRIPE_ROUTES = '''"""Stripe checkout and webhook routes."""

from fastapi import APIRouter, Header, HTTPException, Request, status
import stripe

from app.settings import settings

router = APIRouter(prefix="/billing", tags=["billing"])
stripe.api_key = settings.stripe_secret_key


@router.post("/checkout")
async def create_checkout_session() -> dict[str, str]:
    return {"message": "Configure prices before creating live checkout sessions."}


@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def stripe_webhook(request: Request, stripe_signature: str = Header(alias="Stripe-Signature")) -> None:
    payload = await request.body()
    try:
        stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc
'''

MVC_STRIPE_ROUTES = SIMPLE_STRIPE_ROUTES.replace("from app.settings", "from app.core.config")

MVC_STRIPE_SERVICE = '''"""Billing service boundary for Stripe workflows."""


class BillingService:
    """Keep Stripe business logic out of route handlers."""

    async def create_checkout_session(self) -> dict[str, str]:
        return {"message": "Configure products and prices before enabling checkout."}
'''

STRIPE_TEST = """from fastapi.testclient import TestClient

from app.main import app


def test_stripe_checkout_placeholder() -> None:
    client = TestClient(app)
    response = client.post("/billing/checkout")

    assert response.status_code == 200
"""

SIMPLE_DATABASE_FILE = '''"""Async SQLAlchemy database setup."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
'''

MVC_DATABASE_FILE = SIMPLE_DATABASE_FILE.replace("from app.settings", "from app.core.config")

SIMPLE_CACHE_FILE = '''"""Redis cache client helpers."""

from redis.asyncio import Redis

from app.settings import settings


def create_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)
'''

MVC_CACHE_FILE = SIMPLE_CACHE_FILE.replace("from app.settings", "from app.core.config")

DOCKERFILE = """FROM ghcr.io/astral-sh/uv:python{{ python_version }}-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev
COPY . .
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
"""

DOCKER_COMPOSE = """services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
"""

DOCKERIGNORE = """.venv
__pycache__
.pytest_cache
.ruff_cache
.env
"""

BUILTIN_INTEGRATIONS = cast(
    tuple[Integration, ...],
    (
        OpenAPIIntegration(),
        TestsIntegration(),
        AuthXIntegration(),
        StripeIntegration(),
        PostgresIntegration(),
        RedisIntegration(),
        DockerIntegration(),
        *AUTH_INTEGRATIONS,
        *DATABASE_INTEGRATIONS,
        *CACHE_QUEUE_INTEGRATIONS,
        *PAYMENTS_INTEGRATIONS,
        *STORAGE_INTEGRATIONS,
        *AI_INTEGRATIONS,
        *OBSERVABILITY_INTEGRATIONS,
        *API_INTEGRATIONS,
        *DEPLOY_INTEGRATIONS,
        *DEVTOOLS_INTEGRATIONS,
        *PRODUCT_INTEGRATIONS,
    ),
)
