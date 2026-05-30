"""Files and object storage integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

STORAGE_INTEGRATIONS = (
    docs_integration(
        name="s3",
        label="Amazon S3",
        category="storage",
        description="Adds S3 upload dependencies and settings.",
        dependencies=("boto3>=1.35.0",),
        env_vars=(
            EnvVar("S3_BUCKET", "", "S3 bucket name."),
            EnvVar("AWS_REGION", "us-east-1", "AWS region."),
        ),
        tags=("files", "uploads", "aws"),
    ),
    docs_integration(
        name="cloudflare-r2",
        label="Cloudflare R2",
        category="storage",
        description="Adds S3-compatible Cloudflare R2 settings.",
        dependencies=("boto3>=1.35.0",),
        env_vars=(
            EnvVar("R2_BUCKET", "", "R2 bucket name."),
            EnvVar("R2_ENDPOINT_URL", "", "R2 S3-compatible endpoint."),
        ),
        tags=("files", "uploads", "cloudflare"),
        aliases=("r2",),
    ),
    docs_integration(
        name="gcs",
        label="Google Cloud Storage",
        category="storage",
        description="Adds Google Cloud Storage dependencies and settings.",
        dependencies=("google-cloud-storage>=2.18.0",),
        env_vars=(EnvVar("GCS_BUCKET", "", "Google Cloud Storage bucket."),),
        tags=("files", "uploads", "gcp"),
    ),
    docs_integration(
        name="local-files",
        label="Local Files",
        category="storage",
        description="Adds local upload directory guidance.",
        env_vars=(EnvVar("UPLOAD_DIR", "uploads", "Local upload directory."),),
        tags=("files", "uploads", "local"),
    ),
    docs_integration(
        name="pillow",
        label="Pillow",
        category="storage",
        description="Adds image processing dependencies.",
        dependencies=("pillow>=11.0.0",),
        tags=("images", "processing", "uploads"),
    ),
)
