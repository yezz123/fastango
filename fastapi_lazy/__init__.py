__version__ = "2.0.0"

"""
    fastapi-lazy - A Lazy package-starter for FastAPI applications.
"""

import fastapi_lazy.auth
import fastapi_lazy.database
import fastapi_lazy.generator

__all__ = [
    "auth",
    "database",
    "generator",
]
