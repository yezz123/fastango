"""Database, ORM, and migration integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration
from fastango.scaffold.plan import EnvVar

DATABASE_INTEGRATIONS = (
    docs_integration(
        name="sqlite",
        label="SQLite",
        category="database",
        description="Adds local async SQLite dependencies and settings.",
        dependencies=("sqlalchemy[asyncio]>=2.0.0", "aiosqlite>=0.20.0"),
        env_vars=(EnvVar("DATABASE_URL", "sqlite+aiosqlite:///./app.db", "SQLite database URL."),),
        tags=("database", "local", "sqlalchemy"),
        conflicts=("postgres", "mysql", "mongodb", "tortoise"),
    ),
    docs_integration(
        name="mysql",
        label="MySQL",
        category="database",
        description="Adds async MySQL dependencies and settings.",
        dependencies=("sqlalchemy[asyncio]>=2.0.0", "asyncmy>=0.2.9"),
        env_vars=(
            EnvVar(
                "DATABASE_URL",
                "mysql+asyncmy://root:root@localhost:3306/app",
                "MySQL database URL.",
            ),
        ),
        tags=("database", "mysql", "sqlalchemy"),
        conflicts=("postgres", "sqlite", "mongodb", "tortoise"),
    ),
    docs_integration(
        name="mongodb",
        label="MongoDB",
        category="database",
        description="Adds Motor async MongoDB dependencies and settings.",
        dependencies=("motor>=3.6.0",),
        env_vars=(
            EnvVar("MONGODB_URL", "mongodb://localhost:27017/app", "MongoDB connection URL."),
        ),
        tags=("database", "mongodb", "document"),
        aliases=("mongo",),
        conflicts=("postgres", "sqlite", "mysql", "sqlmodel", "tortoise"),
    ),
    docs_integration(
        name="sqlmodel",
        label="SQLModel",
        category="database",
        description="Adds SQLModel dependencies and model guidance.",
        dependencies=("sqlmodel>=0.0.22",),
        tags=("database", "orm", "pydantic"),
        requires=("postgres",),
        conflicts=("tortoise", "mongodb"),
    ),
    docs_integration(
        name="tortoise",
        label="Tortoise ORM",
        category="database",
        description="Adds Tortoise ORM dependencies and settings.",
        dependencies=("tortoise-orm>=0.21.0",),
        tags=("database", "orm", "async"),
        conflicts=("postgres", "sqlite", "mysql", "mongodb", "sqlmodel"),
        maturity="beta",
    ),
    docs_integration(
        name="alembic",
        label="Alembic",
        category="database",
        description="Adds Alembic migration tooling guidance.",
        dependencies=("alembic>=1.13.0",),
        tags=("database", "migrations", "sqlalchemy"),
        requires=("postgres",),
    ),
    docs_integration(
        name="supabase",
        label="Supabase",
        category="database",
        description="Adds Supabase client dependencies and settings.",
        dependencies=("supabase>=2.8.0",),
        env_vars=(
            EnvVar("SUPABASE_URL", "", "Supabase project URL."),
            EnvVar("SUPABASE_KEY", "", "Supabase service or anon key."),
        ),
        tags=("database", "auth", "storage"),
        maturity="beta",
    ),
    docs_integration(
        name="pgvector",
        label="pgvector",
        category="database",
        description="Adds pgvector support for Postgres-backed embeddings.",
        dependencies=("pgvector>=0.3.0",),
        tags=("database", "vector", "ai"),
        requires=("postgres",),
        conflicts=("qdrant", "pinecone", "weaviate"),
    ),
)
