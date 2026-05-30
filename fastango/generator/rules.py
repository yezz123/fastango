"""Deterministic prompt rules for constrained generation."""

from __future__ import annotations

import re

from fastango.generator.models import ChoiceReason, GenerationPlan, SecurityPolicy
from fastango.generator.skills import infer_skills
from fastango.scaffold.config import TemplateStyle
from fastango.scaffold.registry import IntegrationRegistry


def infer_project_name(prompt: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", prompt.lower())
    ignored = {"a", "an", "the", "with", "for", "and", "api", "fastapi"}
    useful = [word for word in words if word not in ignored][:3]
    return "-".join(useful or ["fastango-app"])


def deterministic_plan(
    *,
    prompt: str,
    registry: IntegrationRegistry,
    project_name: str | None = None,
    style: TemplateStyle | None = None,
) -> GenerationPlan:
    lowered = prompt.lower()
    words = set(re.findall(r"[a-z0-9]+", lowered))
    skills = infer_skills(prompt)
    selected_presets: list[str] = []
    selected_integrations: list[str] = []
    reasons: list[ChoiceReason] = []
    security_notes = list(SecurityPolicy().notes)
    not_generated: list[str] = []

    def add_preset(name: str, reason: str) -> None:
        if name not in selected_presets:
            selected_presets.append(name)
            reasons.append(ChoiceReason(name=name, reason=reason))

    def add_integration(name: str, reason: str) -> None:
        if name not in selected_integrations:
            selected_integrations.append(name)
            reasons.append(ChoiceReason(name=name, reason=reason))

    if any(term in lowered for term in ("mvp", "starter", "saas")):
        add_preset("saas", "The prompt describes an MVP or SaaS product.")
    if "api" in lowered and not selected_presets:
        add_preset("api-starter", "The prompt asks for an API starter.")

    for skill in skills:
        for preset in skill.presets:
            add_preset(preset, f"Selected by the `{skill.name}` Fastango skill.")
        for integration in skill.integrations:
            add_integration(integration, f"Selected by the `{skill.name}` Fastango skill.")
        security_notes.extend(skill.security_notes)

    if any(term in lowered for term in ("billing", "subscription", "checkout", "payment")):
        if "polar" in lowered:
            add_integration("polar", "The prompt explicitly mentions Polar billing.")
        elif "lemon" in lowered or "lemonsqueezy" in lowered or "lemon-squeezy" in lowered:
            add_integration("lemonsqueezy", "The prompt explicitly mentions Lemon Squeezy.")
        elif "paddle" in lowered:
            add_integration("paddle", "The prompt explicitly mentions Paddle.")
        else:
            add_integration("stripe", "Stripe is the default supported billing provider.")
        add_integration("subscriptions", "Subscription workflows need a billing domain service.")

    keyword_integrations = {
        "auth": ("authx", "Auth keywords map to the supported AuthX scaffold."),
        "login": ("authx", "Login keywords map to the supported AuthX scaffold."),
        "team": ("teams", "Team keywords map to the Teams scaffold."),
        "email": ("resend", "Resend is the default transactional email provider."),
        "invite": ("resend", "Invites need transactional email support."),
        "analytics": ("posthog", "Analytics keywords map to PostHog."),
        "events": ("posthog", "Event tracking keywords map to PostHog."),
        "monitoring": ("sentry", "Monitoring keywords map to Sentry error tracking."),
        "errors": ("sentry", "Error tracking keywords map to Sentry."),
        "admin": ("admin", "Admin keywords map to the admin route scaffold."),
        "backoffice": ("admin", "Backoffice keywords map to the admin route scaffold."),
        "upload": ("uploads", "Upload keywords map to upload scaffolding."),
        "crud": ("crud", "CRUD keywords map to CRUD route/service guidance."),
        "pagination": ("pagination", "Pagination keywords map to pagination helpers."),
        "filter": ("filters", "Filter keywords map to query filtering helpers."),
        "webhook": ("webhooks", "Webhook keywords map to signed webhook guidance."),
        "api key": ("api-keys", "API key keywords map to API key auth scaffolding."),
    }
    for keyword, (integration, reason) in keyword_integrations.items():
        if keyword in lowered:
            add_integration(integration, reason)

    if any(term in lowered for term in ("secure", "production")):
        add_preset("production", "Secure or production keywords map to the production preset.")
        add_integration("secure-api", "Secure API skill applies security middleware and guidance.")

    if words & {"ai", "llm", "chat", "rag", "vector", "agent"}:
        add_preset("ai-api", "AI keywords map to the AI API preset.")
    if "openai" in lowered:
        add_integration("openai", "The prompt explicitly mentions OpenAI.")
    if "anthropic" in lowered or "claude" in lowered:
        add_integration("anthropic", "The prompt explicitly mentions Anthropic or Claude.")
    if any(term in lowered for term in ("vector", "rag")):
        add_integration("pgvector", "Vector/RAG keywords map to pgvector with Postgres.")

    if any(
        term in lowered for term in ("nextjs", "next.js", "react", "vue", "threejs", "three.js")
    ):
        not_generated.append(
            "Not generated: frontend frameworks are not currently supported templates."
        )

    resolved_integrations, skipped = _drop_conflicting_integrations(
        selected_integrations,
        selected_presets,
        registry,
    )
    not_generated.extend(skipped)
    inferred_style: TemplateStyle = style or (
        "mvc" if len(selected_presets) + len(resolved_integrations) > 3 else "simple"
    )

    return GenerationPlan(
        prompt=prompt,
        project_name=project_name or infer_project_name(prompt),
        style=inferred_style,
        skills=tuple(skill.name for skill in skills),
        presets=tuple(selected_presets),
        integrations=tuple(resolved_integrations),
        reasons=tuple(reasons),
        security_notes=tuple(dict.fromkeys(security_notes)),
        not_generated=tuple(not_generated),
        provider="deterministic",
    )


def _drop_conflicting_integrations(
    integrations: list[str],
    presets: list[str],
    registry: IntegrationRegistry,
) -> tuple[list[str], list[str]]:
    accepted = {name for preset in presets for name in registry.get_preset(preset).integrations}
    resolved: list[str] = []
    skipped: list[str] = []
    for name in integrations:
        integration = registry.get(name)
        if integration.name in accepted:
            continue
        conflicts = set(integration.conflicts) & accepted
        reverse_conflicts = {
            existing
            for existing in accepted
            if integration.name in registry.get(existing).conflicts
        }
        if conflicts or reverse_conflicts:
            conflict_names = ", ".join(sorted(conflicts | reverse_conflicts))
            skipped.append(
                f"Not generated: `{integration.name}` conflicts with selected integration `{conflict_names}`."
            )
            continue
        accepted.add(integration.name)
        resolved.append(integration.name)
    return resolved, skipped
