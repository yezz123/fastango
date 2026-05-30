"""Validated user choices for generated FastAPI projects."""

from __future__ import annotations

import keyword
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TemplateStyle = Literal["simple", "mvc"]
PackageManager = Literal["uv"]

PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
PYTHON_VERSION_RE = re.compile(r"^3\.(10|11|12|13)$")


def normalize_package_name(project_name: str) -> str:
    """Convert a project display name into a valid Python package name."""

    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", project_name).strip("_").lower()
    normalized = re.sub(r"_+", "_", normalized)
    if normalized and normalized[0].isdigit():
        normalized = f"app_{normalized}"
    return normalized or "app"


class ProjectConfig(BaseModel):
    """All choices needed to render a FastAPI project."""

    model_config = ConfigDict()

    project_name: str = Field(description="Display name and destination directory name.")
    package_name: str | None = Field(default=None, description="Import-safe Python package name.")
    output_dir: Path = Field(default=Path.cwd(), description="Parent directory for the project.")
    style: TemplateStyle = "simple"
    python_version: str = "3.12"
    integrations: tuple[str, ...] = Field(default_factory=tuple)
    presets: tuple[str, ...] = Field(default_factory=tuple)
    package_manager: PackageManager = "uv"
    create_git: bool = False
    force: bool = False

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Project name is required.")
        if not PROJECT_NAME_RE.match(value):
            raise ValueError(
                "Project name may only contain letters, numbers, dots, dashes, and underscores."
            )
        return value

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value.isidentifier() or keyword.iskeyword(value):
            raise ValueError("Package name must be a valid Python identifier.")
        return value

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, value: str) -> str:
        if not PYTHON_VERSION_RE.match(value):
            raise ValueError("Python version must be one of 3.10, 3.11, 3.12, or 3.13.")
        return value

    @field_validator("integrations", "presets", mode="before")
    @classmethod
    def normalize_slug_tuple(cls, value: object) -> tuple[str, ...]:
        if value in (None, ""):
            return ()
        if isinstance(value, str):
            raw_values = [item.strip() for item in value.split(",")]
        elif isinstance(value, Iterable):
            raw_values = list(value)
        else:
            raise TypeError("Integrations must be a string or iterable of strings.")

        seen: set[str] = set()
        integrations: list[str] = []
        for item in raw_values:
            name = str(item).strip().lower().replace("_", "-")
            if name and name not in seen:
                integrations.append(name)
                seen.add(name)
        return tuple(integrations)

    @model_validator(mode="after")
    def set_package_name(self) -> ProjectConfig:
        if self.package_name is None:
            package_name = normalize_package_name(self.project_name)
            if not package_name.isidentifier() or keyword.iskeyword(package_name):
                raise ValueError("Could not derive a valid package name from the project name.")
            self.package_name = package_name
        return self

    @property
    def project_slug(self) -> str:
        return self.project_name.lower().replace("_", "-")

    @property
    def target_dir(self) -> Path:
        return self.output_dir / self.project_name
