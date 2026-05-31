"""Worker and background execution integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

CELERY_APP = '''"""Celery application factory."""

from celery import Celery

from app.core.config import settings

celery_app = Celery("worker", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
'''

CELERY_TASKS = '''"""Example Celery tasks."""

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def example_task(self, payload: dict[str, str]) -> dict[str, str]:
    return payload
'''

BACKGROUND_ROUTE = '''"""Native FastAPI BackgroundTasks example."""

from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/background", tags=["background"])


def write_audit_message(message: str) -> None:
    _ = message


@router.post("")
async def queue_background_task(background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(write_audit_message, "queued")
    return {"status": "queued"}
'''

SCHEDULER = '''"""APScheduler setup placeholder."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
'''

CELERY_SERVICE = """  celery_worker:
    build: .
    command: uv run celery -A app.workers.celery_app.celery_app worker --loglevel=info
    env_file:
      - .env
"""

BEAT_SERVICE = """  celery_beat:
    build: .
    command: uv run celery -A app.workers.celery_app.celery_app beat --loglevel=info
    env_file:
      - .env
"""

FLOWER_SERVICE = """  flower:
    image: mher/flower
    command: celery --broker=redis://redis:6379/0 flower
    ports:
      - "5555:5555"
"""

WORKER_INTEGRATIONS = (
    docs_integration(
        name="celery-worker-code",
        label="Celery Worker Code",
        category="workers",
        description="Adds Celery app, retrying task, and compose worker service.",
        dependencies=("celery[redis]>=5.4.0",),
        env_vars=(
            EnvVar("CELERY_BROKER_URL", "redis://localhost:6379/0", "Celery broker URL."),
            EnvVar("CELERY_RESULT_BACKEND", "redis://localhost:6379/0", "Celery result backend."),
        ),
        files=(("app/workers/celery_app.py", CELERY_APP), ("app/workers/tasks.py", CELERY_TASKS)),
        settings_fields=(
            'celery_broker_url: str = "redis://localhost:6379/0"',
            'celery_result_backend: str = "redis://localhost:6379/0"',
        ),
        compose_services=(CELERY_SERVICE,),
        tags=("workers", "celery", "redis"),
    ),
    docs_integration(
        name="celery-beat-code",
        label="Celery Beat Code",
        category="workers",
        description="Adds a Celery beat service to Docker Compose.",
        requires=("celery-worker-code",),
        compose_services=(BEAT_SERVICE,),
        tags=("workers", "scheduler"),
    ),
    docs_integration(
        name="flower-code",
        label="Flower Code",
        category="workers",
        description="Adds Flower monitoring service for Celery.",
        requires=("celery-worker-code",),
        compose_services=(FLOWER_SERVICE,),
        tags=("workers", "monitoring"),
    ),
    docs_integration(
        name="background-tasks-code",
        label="Background Tasks Code",
        category="workers",
        description="Adds a native FastAPI BackgroundTasks route example.",
        files=(("app/api/routes/background.py", BACKGROUND_ROUTE),),
        router_imports=("from app.api.routes.background import router as background_router",),
        router_includes=("app.include_router(background_router)",),
        tags=("fastapi", "background"),
    ),
    docs_integration(
        name="apscheduler-code",
        label="APScheduler Code",
        category="workers",
        description="Adds APScheduler setup placeholder.",
        dependencies=("apscheduler>=3.10.4",),
        files=(("app/workers/scheduler.py", SCHEDULER),),
        lifespan_hooks=(("from app.workers.scheduler import scheduler", "scheduler.start()"),),
        tags=("scheduler", "jobs"),
    ),
)
