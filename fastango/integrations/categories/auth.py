"""Auth and security integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

SECURITY_HEADERS_FILE = '''"""Security header middleware."""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response
'''

AUTH_INTEGRATIONS = (
    docs_integration(
        name="fastapi-users",
        label="FastAPI Users",
        category="auth",
        description="Adds FastAPI Users dependencies and account-management guidance.",
        dependencies=("fastapi-users[sqlalchemy]>=14.0.0",),
        env_vars=(EnvVar("AUTH_SECRET", "change-me", "Secret for auth flows."),),
        tags=("auth", "users", "accounts"),
        conflicts=("jwt",),
        aliases=("users",),
    ),
    docs_integration(
        name="oauth",
        label="OAuth",
        category="auth",
        description="Adds OAuth client configuration placeholders.",
        dependencies=("authlib>=1.3.0",),
        env_vars=(
            EnvVar("OAUTH_CLIENT_ID", "", "OAuth client ID."),
            EnvVar("OAUTH_CLIENT_SECRET", "", "OAuth client secret."),
        ),
        tags=("auth", "oauth", "social-login"),
        maturity="beta",
    ),
    docs_integration(
        name="jwt",
        label="JWT",
        category="auth",
        description="Adds lightweight JWT dependencies and security guidance.",
        dependencies=("pyjwt[crypto]>=2.9.0", "passlib[bcrypt]>=1.7.4"),
        env_vars=(EnvVar("JWT_SECRET_KEY", "change-me", "Secret key used to sign JWTs."),),
        tags=("auth", "jwt", "security"),
        conflicts=("authx", "fastapi-users"),
    ),
    docs_integration(
        name="cors",
        label="CORS",
        category="auth",
        description="Adds CORS middleware configuration.",
        tags=("security", "middleware", "browser"),
        main_imports=("from fastapi.middleware.cors import CORSMiddleware",),
        app_hooks=(
            "app.add_middleware(\n"
            "    CORSMiddleware,\n"
            '    allow_origins=["*"],\n'
            "    allow_credentials=True,\n"
            '    allow_methods=["*"],\n'
            '    allow_headers=["*"],\n'
            ")",
        ),
        readme="### CORS\n\nCORS middleware is enabled for local development. Restrict `allow_origins` before deploying.",
        llms="CORS is enabled in `app/main.py`. Replace wildcard origins with explicit frontend domains for production.",
    ),
    docs_integration(
        name="rate-limit",
        label="Rate Limiting",
        category="auth",
        description="Adds SlowAPI-compatible rate-limiting dependencies and guidance.",
        dependencies=("slowapi>=0.1.9",),
        env_vars=(EnvVar("RATE_LIMIT", "100/minute", "Default API rate limit."),),
        tags=("security", "redis", "limits"),
        aliases=("ratelimit", "slowapi"),
        maturity="beta",
    ),
    docs_integration(
        name="csrf",
        label="CSRF",
        category="auth",
        description="Adds CSRF guidance for cookie and session-based APIs.",
        dependencies=("fastapi-csrf-protect>=1.0.0",),
        env_vars=(EnvVar("CSRF_SECRET_KEY", "change-me", "CSRF signing secret."),),
        tags=("security", "cookies", "forms"),
        maturity="experimental",
    ),
    docs_integration(
        name="security-headers",
        label="Security Headers",
        category="auth",
        description="Adds middleware for common HTTP security headers.",
        files=(
            ("app/middleware/__init__.py", '"""Application middleware."""\n'),
            ("app/middleware/security_headers.py", SECURITY_HEADERS_FILE),
        ),
        main_imports=("from app.middleware.security_headers import SecurityHeadersMiddleware",),
        app_hooks=("app.add_middleware(SecurityHeadersMiddleware)",),
        tags=("security", "headers", "middleware"),
        aliases=("headers",),
    ),
)
