"""Deployment integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration

COMPOSE_POSTGRES = """services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
    ports:
      - "5432:5432"
"""

COMPOSE_REDIS = """services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"
"""

KUBERNETES_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ project_slug }}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {{ project_slug }}
  template:
    metadata:
      labels:
        app: {{ project_slug }}
    spec:
      containers:
        - name: api
          image: {{ project_slug }}:latest
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: {{ project_slug }}
spec:
  selector:
    app: {{ project_slug }}
  ports:
    - port: 80
      targetPort: 8000
"""

GENERATED_CI = """name: Generated Project CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - uses: actions/setup-python@v5
        with:
          python-version: "{{ python_version }}"
      - run: uv sync --all-groups
      - run: uv run ruff check .
      - run: uv run pytest
"""

DEPLOY_INTEGRATIONS = (
    docs_integration(
        name="compose-postgres",
        label="Compose Postgres",
        category="deploy",
        description="Adds a Docker Compose overlay for Postgres.",
        files=(("docker-compose.postgres.yml", COMPOSE_POSTGRES),),
        tags=("docker", "postgres", "local-dev"),
        requires=("postgres",),
    ),
    docs_integration(
        name="compose-redis",
        label="Compose Redis",
        category="deploy",
        description="Adds a Docker Compose overlay for Redis.",
        files=(("docker-compose.redis.yml", COMPOSE_REDIS),),
        tags=("docker", "redis", "local-dev"),
        requires=("redis",),
    ),
    docs_integration(
        name="kubernetes",
        label="Kubernetes",
        category="deploy",
        description="Adds basic Kubernetes deployment and service manifests.",
        files=(("deploy/kubernetes.yml", KUBERNETES_DEPLOYMENT),),
        tags=("deploy", "k8s", "production"),
        aliases=("k8s",),
        requires=("docker",),
        maturity="beta",
    ),
    docs_integration(
        name="github-actions",
        label="GitHub Actions",
        category="deploy",
        description="Adds CI workflow for generated projects.",
        files=((".github/workflows/ci.yml", GENERATED_CI),),
        tags=("ci", "github", "quality"),
        aliases=("ci",),
    ),
)
