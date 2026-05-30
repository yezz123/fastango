"""Allowlisted Fastango generation skills."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationSkill:
    name: str
    description: str
    templates: tuple[str, ...]
    presets: tuple[str, ...]
    integrations: tuple[str, ...]
    security_notes: tuple[str, ...]
    keywords: tuple[str, ...]


SKILLS: tuple[GenerationSkill, ...] = (
    GenerationSkill(
        name="saas-mvp",
        description="Auth, teams, billing, email, analytics, monitoring, and secure defaults.",
        templates=("mvc",),
        presets=("saas",),
        integrations=("teams", "subscriptions", "customer-portal", "admin", "audit-log"),
        security_notes=(
            "Billing webhooks must verify signatures before mutating subscription state.",
        ),
        keywords=("mvp", "saas", "subscription", "billing", "startup"),
    ),
    GenerationSkill(
        name="secure-api",
        description="CORS, security headers, rate limiting, signed webhooks, and API keys.",
        templates=("simple", "mvc"),
        presets=("production",),
        integrations=("secure-api", "roles", "api-keys", "secrets"),
        security_notes=(
            "API keys and role checks must use dependency injection, not inline checks.",
        ),
        keywords=("secure", "security", "production", "webhook", "api key"),
    ),
    GenerationSkill(
        name="ai-api",
        description="LLM providers, vector search, cache, background jobs, and RAG-ready guidance.",
        templates=("mvc",),
        presets=("ai-api",),
        integrations=("openai", "anthropic", "pgvector"),
        security_notes=("Provider API keys must stay in settings and environment variables.",),
        keywords=("ai", "llm", "chat", "rag", "vector", "agent"),
    ),
    GenerationSkill(
        name="marketplace",
        description="Users, teams, payments, uploads, webhooks, and audit logs.",
        templates=("mvc",),
        presets=("saas",),
        integrations=("teams", "uploads", "webhooks", "audit-log", "roles"),
        security_notes=("Marketplace actions should be scoped by team/account ownership.",),
        keywords=("marketplace", "seller", "buyer", "vendor", "multi-tenant"),
    ),
    GenerationSkill(
        name="crud-api",
        description="Database, CRUD routes, pagination, filters, and tests.",
        templates=("simple", "mvc"),
        presets=("api-starter",),
        integrations=("postgres", "crud", "pagination", "filters"),
        security_notes=("Validate request and response models with Pydantic schemas.",),
        keywords=("crud", "resource", "records", "admin api", "dashboard"),
    ),
    GenerationSkill(
        name="production-api",
        description="Docker, CI, health checks, observability, and dependency hygiene.",
        templates=("mvc",),
        presets=("production",),
        integrations=("makefile", "dependabot", "editorconfig"),
        security_notes=("Generated production scaffolds should include CI and health probes.",),
        keywords=("deploy", "production", "ci", "docker", "monitoring"),
    ),
)


def skill_names() -> tuple[str, ...]:
    return tuple(skill.name for skill in SKILLS)


def get_skill(name: str) -> GenerationSkill:
    normalized = name.strip().lower()
    for skill in SKILLS:
        if skill.name == normalized:
            return skill
    available = ", ".join(skill_names())
    raise ValueError(f"Unknown generation skill '{name}'. Available: {available}.")


def infer_skills(prompt: str) -> tuple[GenerationSkill, ...]:
    lowered = prompt.lower()
    words = set(re.findall(r"[a-z0-9]+", lowered))
    selected: list[GenerationSkill] = []
    for skill in SKILLS:
        if any(
            keyword in lowered if " " in keyword else keyword in words for keyword in skill.keywords
        ):
            selected.append(skill)
    return tuple(selected)
