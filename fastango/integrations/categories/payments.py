"""Payments, SaaS, analytics, and email integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

PAYMENTS_INTEGRATIONS = (
    docs_integration(
        name="paddle",
        label="Paddle",
        category="payments",
        description="Adds Paddle checkout and webhook placeholders.",
        dependencies=("paddle-python-sdk>=1.0.0",),
        env_vars=(
            EnvVar("PADDLE_API_KEY", "", "Paddle API key."),
            EnvVar("PADDLE_WEBHOOK_SECRET", "", "Paddle webhook signing secret."),
        ),
        tags=("billing", "payments", "webhooks"),
        conflicts=("stripe", "polar", "lemonsqueezy"),
        maturity="beta",
    ),
    docs_integration(
        name="polar",
        label="Polar",
        category="payments",
        description="Adds Polar billing placeholders for modern SaaS apps.",
        env_vars=(EnvVar("POLAR_ACCESS_TOKEN", "", "Polar API access token."),),
        tags=("billing", "payments", "saas"),
        conflicts=("stripe", "paddle", "lemonsqueezy"),
        maturity="beta",
    ),
    docs_integration(
        name="lemonsqueezy",
        label="Lemon Squeezy",
        category="payments",
        description="Adds Lemon Squeezy checkout and webhook placeholders.",
        env_vars=(
            EnvVar("LEMONSQUEEZY_API_KEY", "", "Lemon Squeezy API key."),
            EnvVar("LEMONSQUEEZY_WEBHOOK_SECRET", "", "Lemon Squeezy webhook signing secret."),
        ),
        tags=("billing", "payments", "webhooks"),
        conflicts=("stripe", "paddle", "polar"),
        aliases=("lemon-squeezy",),
        maturity="beta",
    ),
    docs_integration(
        name="resend",
        label="Resend",
        category="payments",
        description="Adds Resend transactional email settings.",
        dependencies=("resend>=2.4.0",),
        env_vars=(EnvVar("RESEND_API_KEY", "", "Resend API key."),),
        tags=("email", "transactional", "saas"),
    ),
    docs_integration(
        name="sendgrid",
        label="SendGrid",
        category="payments",
        description="Adds SendGrid transactional email settings.",
        dependencies=("sendgrid>=6.11.0",),
        env_vars=(EnvVar("SENDGRID_API_KEY", "", "SendGrid API key."),),
        tags=("email", "transactional", "saas"),
    ),
    docs_integration(
        name="mailgun",
        label="Mailgun",
        category="payments",
        description="Adds Mailgun transactional email settings.",
        dependencies=("httpx>=0.27.0",),
        env_vars=(
            EnvVar("MAILGUN_API_KEY", "", "Mailgun API key."),
            EnvVar("MAILGUN_DOMAIN", "", "Mailgun sending domain."),
        ),
        tags=("email", "transactional", "saas"),
    ),
    docs_integration(
        name="posthog",
        label="PostHog",
        category="payments",
        description="Adds PostHog analytics and feature flag settings.",
        dependencies=("posthog>=3.7.0",),
        env_vars=(
            EnvVar("POSTHOG_API_KEY", "", "PostHog project API key."),
            EnvVar("POSTHOG_HOST", "https://us.i.posthog.com", "PostHog ingestion host."),
        ),
        tags=("analytics", "feature-flags", "saas"),
    ),
    docs_integration(
        name="sentry",
        label="Sentry",
        category="payments",
        description="Adds Sentry error tracking settings.",
        dependencies=("sentry-sdk[fastapi]>=2.13.0",),
        env_vars=(EnvVar("SENTRY_DSN", "", "Sentry DSN."),),
        tags=("errors", "monitoring", "saas"),
    ),
)
