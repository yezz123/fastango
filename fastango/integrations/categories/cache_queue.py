"""Cache, queue, and background job integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

CACHE_QUEUE_INTEGRATIONS = (
    docs_integration(
        name="celery",
        label="Celery",
        category="cache-queue",
        description="Adds Celery worker dependencies and Redis broker settings.",
        dependencies=("celery[redis]>=5.4.0",),
        env_vars=(EnvVar("CELERY_BROKER_URL", "redis://localhost:6379/1", "Celery broker URL."),),
        tags=("queue", "worker", "redis"),
        requires=("redis",),
    ),
    docs_integration(
        name="dramatiq",
        label="Dramatiq",
        category="cache-queue",
        description="Adds Dramatiq background worker dependencies.",
        dependencies=("dramatiq[redis]>=1.17.0",),
        env_vars=(
            EnvVar("DRAMATIQ_BROKER_URL", "redis://localhost:6379/2", "Dramatiq broker URL."),
        ),
        tags=("queue", "worker", "redis"),
        requires=("redis",),
    ),
    docs_integration(
        name="arq",
        label="ARQ",
        category="cache-queue",
        description="Adds ARQ async Redis job dependencies.",
        dependencies=("arq>=0.26.0",),
        tags=("queue", "async", "redis"),
        requires=("redis",),
    ),
    docs_integration(
        name="rq",
        label="RQ",
        category="cache-queue",
        description="Adds Redis Queue worker dependencies.",
        dependencies=("rq>=2.0.0",),
        tags=("queue", "worker", "redis"),
        requires=("redis",),
    ),
    docs_integration(
        name="apscheduler",
        label="APScheduler",
        category="cache-queue",
        description="Adds scheduled job dependencies.",
        dependencies=("apscheduler>=3.10.4",),
        tags=("scheduler", "jobs", "cron"),
    ),
    docs_integration(
        name="fastapi-background",
        label="FastAPI Background Tasks",
        category="cache-queue",
        description="Adds examples and guidance for native FastAPI background tasks.",
        tags=("fastapi", "background", "tasks"),
        aliases=("background",),
    ),
)
