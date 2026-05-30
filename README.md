# Fastango

<!-- markdownlint-disable MD033 -->
<p align="center">
  <img src="docs/logo.png" alt="Fastango logo">
</p>
<!-- markdownlint-enable MD033 -->

Fastango is a `uv`-first CLI for generating FastAPI projects with selectable templates and optional integrations.

## Install

```bash
uv tool install fastango
```

During local development:

```bash
uv sync --all-groups
uv run fastango --help
```

## Create A Project

Interactive mode:

```bash
uvx fastango
```

Running `fastango` with no subcommand opens the branded terminal playground. You can also launch it explicitly:

```bash
fastango playground
```

Non-interactive mode:

```bash
fastango create billing-api \
  --style mvc \
  --python 3.12 \
  --preset saas \
  --integration openapi \
  --integration authx \
  --integration stripe \
  --with-docker \
  --no-interactive
```

Generated projects use `uv`:

```bash
cd billing-api
uv sync
cp .env.example .env
uv run fastapi dev app/main.py
```

## Generate From A Prompt

Fastango can infer a constrained FastAPI scaffold from a natural-language prompt:

```bash
fastango generate "a starter MVP with auth, billing, email, analytics and secure webhooks"
fastango generate "AI SaaS with vector search" --dry-run --json
```

The generator is intentionally constrained. It only composes supported Fastango templates, skills, presets, and integrations. Unsupported requests are shown as `not generated` notes instead of being written as arbitrary code.

Optional provider enrichment is available when configured:

```bash
fastango generate "marketplace MVP with billing and uploads" --provider anthropic
fastango generate "AI SaaS with vector search" --provider openai --model gpt-4.1-mini
```

Provider output is validated against the same supported catalog before any files are written.

List provider models. If the matching API key is set, Fastango asks the provider which models
your key can access; otherwise it falls back to the curated offline list.

```bash
fastango models
fastango models --provider anthropic
fastango models --provider openai --json
fastango models --provider openai --static
```

## Templates

- `simple`: compact FastAPI app with settings, routes, schemas, tests, README, and `llms.txt`.
- `mvc`: structured app with `api`, `core`, `schemas`, `services`, `repositories`, tests, README, and `llms.txt`.

## Built-In Integrations

List, filter, search, and inspect presets:

```bash
uv run fastango integrations
uv run fastango integrations --category database
uv run fastango integrations --search vector
uv run fastango integrations --presets
uv run fastango integrations --json
```

Fastango includes a broad catalog across:

- Auth and security: AuthX, FastAPI Users, OAuth, JWT, CORS, rate limiting, CSRF, security headers.
- Databases: Postgres, SQLite, MySQL, MongoDB, SQLModel, Tortoise, Alembic, Supabase, pgvector.
- Cache and jobs: Redis, Celery, Dramatiq, ARQ, RQ, APScheduler, FastAPI background tasks.
- SaaS: Stripe, Paddle, Polar, Lemon Squeezy, Resend, SendGrid, Mailgun, PostHog, Sentry.
- Storage: S3, Cloudflare R2, Google Cloud Storage, local files, Pillow.
- AI and search: OpenAI, Anthropic, Ollama, LangChain, LlamaIndex, Qdrant, Pinecone, Weaviate, Elasticsearch.
- Observability: OpenTelemetry, Prometheus, Structlog, Logfire, health checks.
- API protocols: OpenAPI, GraphQL, WebSockets, SSE, signed webhooks, versioning.
- Deployment and dev tools: Docker, Compose overlays, Kubernetes, GitHub Actions, pre-commit, Ruff, mypy, pytest.

Presets:

- `api-starter`
- `saas`
- `ai-api`
- `data-api`
- `production`

Generation skills:

- `saas-mvp`
- `secure-api`
- `ai-api`
- `marketplace`
- `crud-api`
- `production-api`

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run mypy fastango
```
