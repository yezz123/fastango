# Fastango

<!-- markdownlint-disable MD033 -->
<p align="center">
  <img src="https://raw.githubusercontent.com/yezz123/fastango/fa66a81b925515f2a3777c91d66132b8998b9421/docs/logo.png" alt="Fastango logo" width="240">
</p>
<!-- markdownlint-enable MD033 -->

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)
![Pydantic](https://img.shields.io/badge/pydantic-v2-e92063)
![uv](https://img.shields.io/badge/package%20manager-uv-654ff0)
![Ruff](https://img.shields.io/badge/linting-ruff-d7ff64)
![License](https://img.shields.io/badge/license-MIT-green)

Fastango is a `uv`-first CLI for generating FastAPI projects with polished terminal flows,
safe AI-assisted planning, selectable templates, and a growing integration catalog.

It helps teams start a serious FastAPI codebase quickly without copying random boilerplate,
hardcoding secrets, or letting an AI write unchecked files.

## Why Fastango

| Need | What Fastango Gives You |
| --- | --- |
| Start a FastAPI app quickly | `simple` and `mvc` templates with settings, routes, tests, README, and `llms.txt`. |
| Add common infrastructure | A searchable catalog for auth, billing, databases, queues, storage, observability, AI, deployment, and dev tools. |
| Generate from product ideas | `fastango generate "a starter MVP"` maps prompts to supported templates, skills, presets, and integrations. |
| Keep generation safe | The generator only uses Fastango-supported tools and validates provider suggestions before writing files. |
| Work like modern Python teams | Generated projects use `uv`, Ruff, pytest, typed settings, and clear next-step commands. |

## Highlights

- Branded interactive terminal playground when you run `uvx fastango`.
- Manual project creation with repeatable flags for CI and documentation.
- Constrained AI generator for prompt-first FastAPI scaffolding.
- Live model discovery for Anthropic and OpenAI API keys.
- Curated presets for starter APIs, SaaS apps, AI APIs, data APIs, and production setups.
- Generated `llms.txt` so AI assistants understand the project conventions.
- Validation for integration requirements, conflicts, unsupported tools, and unsafe provider output.

## Install

```bash
uv tool install fastango
```

During local development:

```bash
uv sync --all-groups
uv run fastango --help
```

## Quick Start

Run Fastango with no subcommand to open the terminal playground:

```bash
uvx fastango
```

You can also launch the playground explicitly:

```bash
fastango playground
```

Create a project without prompts:

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

Run the generated app:

```bash
cd billing-api
uv sync
cp .env.example .env
uv run fastapi dev app/main.py
```

## Generate From A Prompt

Fastango can infer a constrained FastAPI scaffold from a natural-language prompt.
It does not write arbitrary LLM code directly to disk. It converts your prompt into a typed
plan made from supported templates, skills, presets, and integrations.

```bash
fastango generate "a starter MVP with auth, billing, email, analytics and secure webhooks"
fastango generate "AI SaaS with vector search" --dry-run --json
```

Optional provider enrichment is available when configured:

```bash
fastango generate "marketplace MVP with billing and uploads" --provider anthropic
fastango generate "AI SaaS with vector search" --provider openai --model gpt-4.1-mini
```

Provider output is validated against the same supported catalog before any files are written.
Unsupported requests are kept as `not_generated` notes in the preview.

## Model Discovery

If the matching API key is set, Fastango asks the provider which models your key can access.
If no key is available, it falls back to a curated offline list.

```bash
fastango models
fastango models --provider anthropic
fastango models --provider openai --json
fastango models --provider openai --static
```

| Provider | Environment Variable | Model Source |
| --- | --- | --- |
| Anthropic | `ANTHROPIC_API_KEY` | Live `/v1/models` discovery with curated fallback. |
| OpenAI | `OPENAI_API_KEY` | Live `/v1/models` discovery with curated fallback. |

## Templates

| Template | Best For | Includes |
| --- | --- | --- |
| `simple` | Small APIs, internal services, demos, first FastAPI apps. | `app/main.py`, routes, schemas, settings, tests, README, `.env.example`, `llms.txt`. |
| `mvc` | SaaS apps, production APIs, larger teams, integration-heavy projects. | API routes, core settings, services, repositories, schemas, tests, README, `.env.example`, `llms.txt`. |

## Presets

| Preset | Purpose | Typical Stack |
| --- | --- | --- |
| `api-starter` | A clean FastAPI baseline. | OpenAPI, tests, CORS, Ruff, pre-commit. |
| `saas` | Product-ready SaaS API. | AuthX, Stripe, Postgres, Redis, Resend, PostHog, Sentry, Docker. |
| `ai-api` | AI or RAG-ready backend. | OpenAI, Anthropic, pgvector, Postgres, Redis, tests, Docker. |
| `data-api` | Data-heavy API with workers. | Postgres, Alembic, Redis, Celery, Prometheus, OpenTelemetry. |
| `production` | Production hardening. | Docker, GitHub Actions, security headers, Sentry, Prometheus, health checks. |

## Integration Catalog

List, filter, search, and inspect integrations:

```bash
uv run fastango integrations
uv run fastango integrations --category database
uv run fastango integrations --search vector
uv run fastango integrations --presets
uv run fastango integrations --json
```

| Category | Examples |
| --- | --- |
| Auth and security | AuthX, FastAPI Users, OAuth, JWT, CORS, rate limiting, CSRF, security headers, roles, API keys. |
| Databases and ORM | Postgres, SQLite, MySQL, MongoDB, SQLModel, Tortoise, Alembic, Supabase, pgvector. |
| Cache and jobs | Redis, Celery, Dramatiq, ARQ, RQ, APScheduler, FastAPI background tasks. |
| SaaS and payments | Stripe, Paddle, Polar, Lemon Squeezy, subscriptions, customer portal, Resend, PostHog, Sentry. |
| Storage | S3, Cloudflare R2, Google Cloud Storage, local files, Pillow, uploads. |
| AI and search | OpenAI, Anthropic, Ollama, LangChain, LlamaIndex, Qdrant, Pinecone, Weaviate, Elasticsearch. |
| Observability | OpenTelemetry, Prometheus, Structlog, Logfire, health checks, audit logs. |
| API protocols | OpenAPI, GraphQL, WebSockets, SSE, signed webhooks, versioning. |
| Deployment and dev tools | Docker, Compose overlays, Kubernetes, GitHub Actions, pre-commit, Ruff, mypy, pytest, Dependabot. |

## Generation Skills

Skills are internal, allowlisted generation capabilities. They map product intents to supported
Fastango templates and integrations.

| Skill | What It Builds |
| --- | --- |
| `saas-mvp` | Auth, teams, subscriptions, billing provider, email, analytics, monitoring. |
| `secure-api` | CORS, security headers, rate limiting, signed webhooks, API keys, secure settings. |
| `ai-api` | LLM provider, vector store, RAG-ready services, cache, background jobs. |
| `marketplace` | Users, teams, payments, uploads, webhooks, audit logs. |
| `crud-api` | Database, CRUD routes, pagination, filters, tests. |
| `production-api` | Docker, GitHub Actions, health checks, observability, dependency hygiene. |

## Safety Model

| Rule | Why It Matters |
| --- | --- |
| No arbitrary raw code from providers | LLMs can suggest supported IDs, but Fastango writes files only through templates and integration hooks. |
| Secrets stay in settings and `.env.example` | Generated code avoids hardcoded tokens, API keys, and webhook secrets. |
| Registry validation before writes | Presets, aliases, integration requirements, and conflicts are resolved before the filesystem is touched. |
| Unsupported tech becomes a note | Requests for unsupported frameworks are shown in previews instead of silently generated. |

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run mypy fastango
```

## Status

Fastango is early and evolving quickly. The current focus is a great terminal experience,
a reliable integration catalog, and safe prompt-to-FastAPI scaffolding.
