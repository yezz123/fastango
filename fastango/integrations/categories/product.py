"""Product, SaaS, security, and MVP integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

MAKEFILE = """test:
\tuv run pytest

lint:
\tuv run ruff check .

dev:
\tuv run fastapi dev app/main.py
"""

TASKFILE = """version: '3'

tasks:
  test:
    cmds:
      - uv run pytest
  lint:
    cmds:
      - uv run ruff check .
  dev:
    cmds:
      - uv run fastapi dev app/main.py
"""

EDITORCONFIG = """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 4
"""

DEPENDABOT = """version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
"""

PRODUCT_INTEGRATIONS = (
    docs_integration(
        name="teams",
        label="Teams",
        category="product",
        description="Adds team/account ownership guidance for multi-user SaaS apps.",
        env_vars=(EnvVar("DEFAULT_TEAM_ROLE", "member", "Default role for invited team members."),),
        tags=("saas", "teams", "multi-tenant"),
        requires=("authx",),
    ),
    docs_integration(
        name="admin",
        label="Admin",
        category="product",
        description="Adds admin route guidance with role-check placeholders.",
        tags=("admin", "roles", "backoffice"),
        requires=("roles",),
        readme="### Admin\n\nAdmin scaffolding is enabled. Keep admin routes protected by role dependencies and audit sensitive actions.",
        llms="Admin features must stay behind role checks. Do not expose admin routes without authentication and authorization dependencies.",
    ),
    docs_integration(
        name="audit-log",
        label="Audit Log",
        category="product",
        description="Adds audit event service guidance.",
        tags=("security", "audit", "compliance"),
    ),
    docs_integration(
        name="feature-flags",
        label="Feature Flags",
        category="product",
        description="Adds feature flag guidance with local or PostHog-backed flags.",
        tags=("flags", "posthog", "release"),
    ),
    docs_integration(
        name="subscriptions",
        label="Subscriptions",
        category="product",
        description="Adds subscription domain service guidance over supported billing providers.",
        tags=("billing", "subscriptions", "saas"),
    ),
    docs_integration(
        name="customer-portal",
        label="Customer Portal",
        category="product",
        description="Adds customer billing portal route guidance.",
        tags=("billing", "portal", "saas"),
    ),
    docs_integration(
        name="secure-api",
        label="Secure API",
        category="security",
        description="Bundles supported security controls for production APIs.",
        tags=("security", "production", "bundle"),
        requires=("security-headers", "cors", "rate-limit", "webhooks"),
    ),
    docs_integration(
        name="roles",
        label="Roles",
        category="security",
        description="Adds role-check dependency guidance.",
        tags=("auth", "roles", "authorization"),
        requires=("authx",),
    ),
    docs_integration(
        name="api-keys",
        label="API Keys",
        category="security",
        description="Adds API key auth dependency guidance and placeholders.",
        env_vars=(EnvVar("API_KEY_HEADER", "X-API-Key", "Header used for API key auth."),),
        tags=("auth", "api-keys", "security"),
    ),
    docs_integration(
        name="secrets",
        label="Secrets",
        category="security",
        description="Adds secret rotation and `.env.example` guidance.",
        tags=("security", "env", "secrets"),
    ),
    docs_integration(
        name="makefile",
        label="Makefile",
        category="devtools",
        description="Adds a Makefile with uv-powered commands.",
        files=(("Makefile", MAKEFILE),),
        tags=("dx", "commands", "uv"),
    ),
    docs_integration(
        name="taskfile",
        label="Taskfile",
        category="devtools",
        description="Adds a Taskfile alternative for local commands.",
        files=(("Taskfile.yml", TASKFILE),),
        tags=("dx", "commands", "taskfile"),
    ),
    docs_integration(
        name="editorconfig",
        label="EditorConfig",
        category="devtools",
        description="Adds a consistent `.editorconfig`.",
        files=((".editorconfig", EDITORCONFIG),),
        tags=("dx", "editor", "formatting"),
    ),
    docs_integration(
        name="dependabot",
        label="Dependabot",
        category="devtools",
        description="Adds Dependabot update configuration.",
        files=((".github/dependabot.yml", DEPENDABOT),),
        tags=("dx", "dependencies", "github"),
    ),
    docs_integration(
        name="crud",
        label="CRUD",
        category="product-api",
        description="Adds CRUD route/service/repository guidance.",
        tags=("api", "crud", "resources"),
        requires=("postgres",),
    ),
    docs_integration(
        name="pagination",
        label="Pagination",
        category="product-api",
        description="Adds pagination schema guidance.",
        tags=("api", "pagination", "schemas"),
    ),
    docs_integration(
        name="filters",
        label="Filters",
        category="product-api",
        description="Adds query filtering helper guidance.",
        tags=("api", "filters", "queries"),
    ),
    docs_integration(
        name="uploads",
        label="Uploads",
        category="product-api",
        description="Adds upload endpoint guidance using local or object storage.",
        tags=("api", "uploads", "files"),
        requires=("local-files",),
    ),
)
