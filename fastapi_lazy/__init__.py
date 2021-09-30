__version__ = "1.2.0"

"""
    fastapi-lazy - A Lazy package-starter for FastAPI applications.
"""

import fastapi_lazy.auth
import fastapi_lazy.database
import fastapi_lazy.generator
import fastapi_lazy.models

__all__ = [
    "auth",
    "database",
    "generator",
    "models",
]
