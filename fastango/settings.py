from typing import Any, Dict, List

from pydantic import ImportString
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """
    This class is used to configure the FastAPI instance that will be created by the `fastango` module.

    Args:
        BaseSettings (BaseSettings): The base settings class from which this class inherits.

    Returns:
        APISettings: A class that can be used to configure the FastAPI instance that will be created by the `fastango` module.
    """

    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI"
    version: str = "0.1.0"
    disable_docs: bool = False

    enable_error_handlers: bool = True
    services: List[ImportString] = []
    simplify_openapi_ids: bool = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        """
        This property returns a dictionary of the most commonly used keyword arguments when initializing a FastAPI instance.
        If `self.disable_docs` is True, the various docs-related arguments are disabled, preventing your spec from being
        published.

        Args:
            None

        Returns:
            Dict[str, Any]: A dictionary of the most commonly used keyword arguments when initializing a FastAPI instance
            If `self.disable_docs` is True, the various docs-related arguments are disabled, preventing your spec from being
            published.
        """
        fastapi_kwargs = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
        if self.disable_docs:
            fastapi_kwargs.update(
                {"docs_url": None, "openapi_url": None, "redoc_url": None}
            )
        return fastapi_kwargs

    @property
    def config_kwargs(self) -> Dict[str, Any]:
        """
        Returns a dictionary of configuration keyword arguments based on the current settings.

        Returns:
            Dict[str, Any]: A dictionary containing the configuration keyword arguments.
        """
        return {
            "enable_error_handlers": self.enable_error_handlers,
            "services": self.services,
            "simplify_openapi_ids": self.simplify_openapi_ids,
        }

    model_config = SettingsConfigDict(validate_assignment=True, env_prefix="FASTAPI_")
