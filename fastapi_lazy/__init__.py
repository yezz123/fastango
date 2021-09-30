__version__ = "1.0.0"

"""
    fastapi-lazy - A Lazy package-starter for FastAPI applications.
"""

from fastapi_lazy.auth import auth, model
from fastapi_lazy.database import mongo, psql, redis
from fastapi_lazy.generator import generator

__all__ = ["auth", "model", "mongo", "redis", "psql", "generator"]
