import pytest

from fastango.settings import APISettings


@pytest.fixture
def default_settings():
    return APISettings()


@pytest.fixture
def custom_settings():
    return APISettings(
        debug=True,
        docs_url="/api-docs",
        openapi_prefix="/api",
        openapi_url="/api/openapi.json",
        redoc_url="/api/redoc",
        title="My API",
        version="1.0.0",
        disable_docs=True,
        enable_error_handlers=False,
        simplify_openapi_ids=False,
    )


def test_default_settings(default_settings):
    assert default_settings.debug is False
    assert default_settings.docs_url == "/docs"
    assert default_settings.openapi_prefix == ""
    assert default_settings.openapi_url == "/openapi.json"
    assert default_settings.redoc_url == "/redoc"
    assert default_settings.title == "FastAPI"
    assert default_settings.version == "0.1.0"
    assert default_settings.disable_docs is False
    assert default_settings.enable_error_handlers is True
    assert default_settings.simplify_openapi_ids is True


def test_custom_settings(custom_settings):
    assert custom_settings.debug is True
    assert custom_settings.docs_url == "/api-docs"
    assert custom_settings.openapi_prefix == "/api"
    assert custom_settings.openapi_url == "/api/openapi.json"
    assert custom_settings.redoc_url == "/api/redoc"
    assert custom_settings.title == "My API"
    assert custom_settings.version == "1.0.0"
    assert custom_settings.disable_docs is True
    assert custom_settings.enable_error_handlers is False
    assert custom_settings.simplify_openapi_ids is False


def test_fastapi_kwargs(default_settings, custom_settings):
    assert default_settings.fastapi_kwargs == {
        "debug": False,
        "docs_url": "/docs",
        "openapi_prefix": "",
        "openapi_url": "/openapi.json",
        "redoc_url": "/redoc",
        "title": "FastAPI",
        "version": "0.1.0",
    }
    assert custom_settings.fastapi_kwargs == {
        "debug": True,
        "docs_url": None,
        "openapi_prefix": "/api",
        "openapi_url": None,
        "redoc_url": None,
        "title": "My API",
        "version": "1.0.0",
    }


def test_config_kwargs(default_settings, custom_settings):
    assert default_settings.config_kwargs == {
        "enable_error_handlers": True,
        "services": [],
        "simplify_openapi_ids": True,
    }
    assert custom_settings.config_kwargs == {
        "enable_error_handlers": False,
        "services": [],
        "simplify_openapi_ids": False,
    }
