from pathlib import Path

import pytest
from pydantic import ValidationError

from fastango.scaffold.config import ProjectConfig, normalize_package_name


def test_normalize_package_name() -> None:
    assert normalize_package_name("Billing API") == "billing_api"
    assert normalize_package_name("123-api") == "app_123_api"


def test_project_config_derives_package_name() -> None:
    config = ProjectConfig(project_name="billing-api", output_dir=Path("/tmp"))

    assert config.package_name == "billing_api"
    assert config.target_dir == Path("/tmp/billing-api")


def test_project_config_rejects_invalid_python_version() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(project_name="billing-api", python_version="3.9")
