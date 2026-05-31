"""SaaS-oriented code-template integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

AUTH_ROUTE = '''"""JWT auth route placeholders."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login() -> dict[str, str]:
    return {"message": "Wire this route to your user repository and password hasher."}


@router.post("/refresh")
async def refresh_token() -> dict[str, str]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Refresh flow not configured yet.")
'''

RBAC_DEPS = '''"""Role-based access helpers."""

from collections.abc import Callable

from fastapi import HTTPException, status


def require_role(role: str) -> Callable[[], None]:
    def dependency() -> None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role required: {role}")

    return dependency
'''

TEAMS_ROUTE = '''"""Team management route placeholders."""

from fastapi import APIRouter

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
async def list_teams() -> list[dict[str, str]]:
    return []
'''

STRIPE_SUBSCRIPTIONS = '''"""Stripe subscription route placeholders."""

from fastapi import APIRouter, Header, Request, status

router = APIRouter(prefix="/subscriptions", tags=["billing"])


@router.post("/checkout")
async def create_checkout() -> dict[str, str]:
    return {"message": "Configure Stripe price IDs before enabling checkout."}


@router.post("/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def webhook(_: Request, stripe_signature: str = Header(alias="Stripe-Signature")) -> None:
    _ = stripe_signature
'''

TOKEN_ROUTE = '''"""Account token flow placeholders."""

from fastapi import APIRouter

router = APIRouter(prefix="/account", tags=["account"])


@router.post("/password-reset")
async def password_reset() -> dict[str, str]:
    return {"message": "Password reset email queued."}


@router.post("/verify-email")
async def verify_email() -> dict[str, str]:
    return {"message": "Email verification placeholder."}
'''

ADMIN_ROUTE = '''"""Protected admin route placeholders."""

from fastapi import APIRouter, Depends

from app.core.rbac import require_role

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role("admin"))])


@router.get("/summary")
async def summary() -> dict[str, str]:
    return {"status": "admin-ready"}
'''

AUDIT_SERVICE = '''"""Audit logging service boundary."""


async def record_audit_event(actor_id: str, action: str, subject: str) -> dict[str, str]:
    return {"actor_id": actor_id, "action": action, "subject": subject}
'''

SAAS_CODE_INTEGRATIONS = (
    docs_integration(
        name="jwt-auth",
        label="JWT Auth Code",
        category="saas-code",
        description="Adds access/refresh auth route placeholders.",
        dependencies=("python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4"),
        env_vars=(EnvVar("JWT_SECRET_KEY", "change-me", "JWT signing secret."),),
        files=(("app/api/routes/jwt_auth.py", AUTH_ROUTE),),
        settings_fields=('jwt_secret_key: str = "change-me"',),
        router_imports=("from app.api.routes.jwt_auth import router as jwt_auth_router",),
        router_includes=("app.include_router(jwt_auth_router)",),
        tags=("auth", "jwt"),
    ),
    docs_integration(
        name="rbac",
        label="RBAC",
        category="saas-code",
        description="Adds role-based authorization dependency helpers.",
        files=(("app/core/rbac.py", RBAC_DEPS),),
        tags=("auth", "roles"),
    ),
    docs_integration(
        name="teams-code",
        label="Teams Code",
        category="saas-code",
        description="Adds team route placeholders.",
        files=(("app/api/routes/teams.py", TEAMS_ROUTE),),
        router_imports=("from app.api.routes.teams import router as teams_router",),
        router_includes=("app.include_router(teams_router)",),
        tags=("saas", "teams"),
        aliases=("teams-template",),
    ),
    docs_integration(
        name="stripe-subscriptions",
        label="Stripe Subscriptions",
        category="saas-code",
        description="Adds Stripe subscription checkout and webhook route placeholders.",
        dependencies=("stripe>=11.0.0",),
        env_vars=(EnvVar("STRIPE_WEBHOOK_SECRET", "", "Stripe webhook signing secret."),),
        files=(("app/api/routes/subscriptions.py", STRIPE_SUBSCRIPTIONS),),
        router_imports=("from app.api.routes.subscriptions import router as subscriptions_router",),
        router_includes=("app.include_router(subscriptions_router)",),
        tags=("billing", "stripe", "webhooks"),
    ),
    docs_integration(
        name="password-reset",
        label="Password Reset",
        category="saas-code",
        description="Adds password reset route placeholders.",
        files=(("app/api/routes/account_tokens.py", TOKEN_ROUTE),),
        router_imports=(
            "from app.api.routes.account_tokens import router as account_tokens_router",
        ),
        router_includes=("app.include_router(account_tokens_router)",),
        tags=("auth", "email"),
    ),
    docs_integration(
        name="email-verification",
        label="Email Verification",
        category="saas-code",
        description="Adds email verification guidance and account token routes.",
        requires=("password-reset",),
        tags=("auth", "email"),
    ),
    docs_integration(
        name="admin-code",
        label="Admin Code",
        category="saas-code",
        description="Adds protected admin route placeholders.",
        files=(("app/api/routes/admin.py", ADMIN_ROUTE),),
        router_imports=("from app.api.routes.admin import router as admin_router",),
        router_includes=("app.include_router(admin_router)",),
        tags=("admin", "rbac"),
        requires=("rbac",),
    ),
    docs_integration(
        name="audit-log-code",
        label="Audit Log Code",
        category="saas-code",
        description="Adds an audit logging service boundary.",
        files=(("app/services/audit_log.py", AUDIT_SERVICE),),
        tags=("audit", "security"),
    ),
)
