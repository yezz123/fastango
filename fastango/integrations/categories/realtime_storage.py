"""Realtime API and storage code-template integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

WEBSOCKET_ROUTE = '''"""WebSocket route example."""

from fastapi import APIRouter, WebSocket

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_text("connected")
    await websocket.close()
'''

SSE_ROUTE = '''"""Server-sent events route example."""

from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/events", tags=["realtime"])


async def stream_events() -> AsyncIterator[dict[str, str]]:
    yield {"event": "ready", "data": "connected"}


@router.get("")
async def events() -> EventSourceResponse:
    return EventSourceResponse(stream_events())
'''

UPLOAD_ROUTE = '''"""Local upload route example."""

from pathlib import Path

from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("")
async def upload_file(file: UploadFile) -> dict[str, str]:
    target = Path("uploads") / file.filename
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(await file.read())
    return {"filename": file.filename}
'''

STORAGE_SERVICE = '''"""Object storage service boundary."""


async def create_presigned_upload_url(key: str) -> dict[str, str]:
    return {"key": key, "url": "configure-object-storage-provider"}
'''

MINIO_SERVICE = """  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
"""

REALTIME_STORAGE_INTEGRATIONS = (
    docs_integration(
        name="websockets-code",
        label="WebSockets Code",
        category="realtime-storage",
        description="Adds a WebSocket route example.",
        files=(("app/api/routes/websockets.py", WEBSOCKET_ROUTE),),
        router_imports=("from app.api.routes.websockets import router as websockets_router",),
        router_includes=("app.include_router(websockets_router)",),
        tags=("websockets", "realtime"),
    ),
    docs_integration(
        name="sse-code",
        label="SSE Code",
        category="realtime-storage",
        description="Adds a Server-Sent Events route example.",
        dependencies=("sse-starlette>=2.1.0",),
        files=(("app/api/routes/sse.py", SSE_ROUTE),),
        router_imports=("from app.api.routes.sse import router as sse_router",),
        router_includes=("app.include_router(sse_router)",),
        tags=("sse", "realtime"),
    ),
    docs_integration(
        name="uploads-local-code",
        label="Local Uploads Code",
        category="realtime-storage",
        description="Adds a local UploadFile route example.",
        files=(("app/api/routes/uploads.py", UPLOAD_ROUTE),),
        router_imports=("from app.api.routes.uploads import router as uploads_router",),
        router_includes=("app.include_router(uploads_router)",),
        tags=("uploads", "files"),
    ),
    docs_integration(
        name="s3-uploads-code",
        label="S3 Uploads Code",
        category="realtime-storage",
        description="Adds S3 upload service boundary.",
        dependencies=("boto3>=1.35.0",),
        env_vars=(EnvVar("S3_BUCKET", "", "S3 bucket."),),
        files=(("app/services/storage.py", STORAGE_SERVICE),),
        settings_fields=('s3_bucket: str = ""',),
        tags=("s3", "uploads"),
    ),
    docs_integration(
        name="r2-uploads-code",
        label="R2 Uploads Code",
        category="realtime-storage",
        description="Adds Cloudflare R2 S3-compatible settings.",
        requires=("s3-uploads-code",),
        env_vars=(EnvVar("R2_ENDPOINT_URL", "", "R2 S3-compatible endpoint."),),
        settings_fields=('r2_endpoint_url: str = ""',),
        tags=("r2", "uploads"),
    ),
    docs_integration(
        name="gcs-uploads-code",
        label="GCS Uploads Code",
        category="realtime-storage",
        description="Adds Google Cloud Storage service boundary.",
        dependencies=("google-cloud-storage>=2.18.0",),
        env_vars=(EnvVar("GCS_BUCKET", "", "GCS bucket."),),
        settings_fields=('gcs_bucket: str = ""',),
        files=(("app/services/storage.py", STORAGE_SERVICE),),
        tags=("gcs", "uploads"),
    ),
    docs_integration(
        name="minio-compose",
        label="MinIO Compose",
        category="realtime-storage",
        description="Adds local MinIO object storage to Docker Compose.",
        compose_services=(MINIO_SERVICE,),
        tags=("minio", "object-storage"),
    ),
)
