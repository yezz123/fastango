# Fastango Documentation

Fastango generates FastAPI projects that are ready for `uv`, typed settings, tests, and AI-assisted maintenance through `llms.txt`.

## Commands

```bash
fastango
fastango create
fastango create my-api --style mvc --integration openapi --integration authx --no-interactive
fastango create my-api --preset saas --no-interactive
fastango generate "a starter MVP with auth billing email and analytics"
fastango generate "AI SaaS with vector search" --dry-run --json
fastango generate "AI SaaS with vector search" --provider openai --model gpt-4.1-mini
fastango models --provider anthropic
fastango playground
fastango integrations
fastango integrations --category database
fastango integrations --search vector
fastango integrations --presets
```

## Template Styles

Use `simple` for small APIs and internal tools. Use `mvc` when a project needs clearer separation between routes, schemas, services, repositories, and infrastructure.

## Adding Integrations

Built-in integrations implement `fastango.integrations.base.Integration` and mutate a `ScaffoldPlan`. An integration can add dependencies, dev dependencies, environment variables, files, README sections, and `llms.txt` guidance.

## Catalog

The catalog is metadata-driven and split by category under `fastango/integrations/categories/`. Each integration has a stable name, label, category, tags, maturity, aliases, requirements, and conflicts.

Code-template integrations can now add settings fields, middleware hooks, lifespan hooks, routers, Docker Compose services, tests, README sections, and `llms.txt` guidance through `ScaffoldPlan` instead of ad hoc string edits.

Major code-template packs:

- Production: `sqlalchemy-async`, `alembic-code`, `redis-cache-code`, `healthchecks-code`, `prometheus-code`, `sentry-fastapi`, `request-id`, `makefile-full`, `precommit-full`.
- SaaS: `jwt-auth`, `rbac`, `teams-code`, `stripe-subscriptions`, `password-reset`, `email-verification`, `admin-code`, `audit-log-code`.
- Workers: `celery-worker-code`, `celery-beat-code`, `flower-code`, `background-tasks-code`, `apscheduler-code`.
- Realtime and storage: `websockets-code`, `sse-code`, `uploads-local-code`, `s3-uploads-code`, `r2-uploads-code`, `gcs-uploads-code`, `minio-compose`.
- AI: `pydantic-ai-code`, `litellm-code`, `openai-chat-code`, `anthropic-chat-code`, `rag-pgvector`, `qdrant-rag-code`, `prompt-store`, `conversation-memory`.

Curated presets:

- `api-starter`: OpenAPI, tests, CORS, Ruff, and pre-commit.
- `saas`: AuthX, Stripe, Postgres, Redis, Resend, PostHog, Sentry, and Docker.
- `ai-api`: OpenAI, Anthropic, pgvector, Postgres, Redis, tests, and Docker.
- `data-api`: Postgres, Alembic, Redis, Celery, Prometheus, and OpenTelemetry.
- `production`: Docker, GitHub Actions, security headers, Sentry, Prometheus, and health checks.

The branded terminal playground uses the shared Fastango theme from `fastango/terminal/theme.py` and the same registry as non-interactive CLI commands.

Running `uvx fastango` with no subcommand opens the terminal playground directly. The playground stays fully inside the terminal: project basics, presets, category/search browsing, live dependency and file previews, environment variable previews, and final confirmation all render with Rich panels and tables.

## Constrained AI Generation

`fastango generate` is a constrained FastAPI composer. It does not write arbitrary LLM code to disk. It turns a prompt into a typed plan made from supported Fastango templates, skills, presets, and integrations, then validates that plan through the registry before rendering files.

Supported generation skills:

- `saas-mvp`
- `secure-api`
- `ai-api`
- `marketplace`
- `crud-api`
- `production-api`

Unsupported requests, such as frontend frameworks or unknown services, are preserved as `not_generated` notes in the preview.

Use `fastango models` to list Anthropic and OpenAI model IDs for optional provider enrichment. When `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set, Fastango discovers the models available to that key. Without a key, it shows a curated offline fallback. `--model` is validated against the chosen provider so users cannot accidentally call an unsupported model.
