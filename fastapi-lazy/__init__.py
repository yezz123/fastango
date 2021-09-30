__version__ = "1.0.0"

"""
    fastapi-lazy - A Lazy package-starter for FastAPI applications.
"""

from auth import auth, model
from database import mongo, psql, redis
from generator import generator

__all__ = ["auth", "model", "mongo", "redis", "psql", "generator"]
