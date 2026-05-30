"""Mutable scaffold plan assembled before rendering files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from fastango.scaffold.config import ProjectConfig


@dataclass(frozen=True)
class EnvVar:
    name: str
    default: str = ""
    description: str = ""


@dataclass(frozen=True)
class FileSpec:
    path: str
    content: str
    executable: bool = False


@dataclass(frozen=True)
class RenderedFile:
    path: PurePosixPath
    content: str
    executable: bool = False


@dataclass
class ScaffoldPlan:
    config: ProjectConfig
    dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)
    files: list[FileSpec] = field(default_factory=list)
    env_vars: list[EnvVar] = field(default_factory=list)
    readme_sections: list[str] = field(default_factory=list)
    llms_sections: list[str] = field(default_factory=list)
    post_create_messages: list[str] = field(default_factory=list)
    openapi_tags: list[dict[str, str]] = field(default_factory=list)
    enabled_integrations: list[str] = field(default_factory=list)
    main_imports: list[str] = field(default_factory=list)
    app_hooks: list[str] = field(default_factory=list)
    router_imports: list[str] = field(default_factory=list)
    router_includes: list[str] = field(default_factory=list)

    def add_dependency(self, dependency: str) -> None:
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def add_dev_dependency(self, dependency: str) -> None:
        if dependency not in self.dev_dependencies:
            self.dev_dependencies.append(dependency)

    def add_env_var(self, env_var: EnvVar) -> None:
        if env_var.name not in {existing.name for existing in self.env_vars}:
            self.env_vars.append(env_var)

    def add_file(self, path: str, content: str, *, executable: bool = False) -> None:
        self.files.append(FileSpec(path=path, content=content, executable=executable))

    def add_readme_section(self, section: str) -> None:
        self.readme_sections.append(section.strip())

    def add_llms_section(self, section: str) -> None:
        self.llms_sections.append(section.strip())

    def add_openapi_tag(self, name: str, description: str) -> None:
        tag = {"name": name, "description": description}
        if tag not in self.openapi_tags:
            self.openapi_tags.append(tag)

    def add_main_import(self, import_line: str) -> None:
        if import_line not in self.main_imports:
            self.main_imports.append(import_line)

    def add_app_hook(self, statement: str) -> None:
        if statement not in self.app_hooks:
            self.app_hooks.append(statement)

    def add_router(self, import_line: str, include_statement: str) -> None:
        if import_line not in self.router_imports:
            self.router_imports.append(import_line)
        if include_statement not in self.router_includes:
            self.router_includes.append(include_statement)

    def context(self) -> dict[str, Any]:
        package_name = self.config.package_name
        if package_name is None:  # pragma: no cover - ProjectConfig always fills this.
            raise RuntimeError("Package name has not been resolved.")
        return {
            "project_name": self.config.project_name,
            "project_slug": self.config.project_slug,
            "package_name": package_name,
            "style": self.config.style,
            "python_version": self.config.python_version,
            "dependencies": sorted(self.dependencies),
            "dev_dependencies": sorted(self.dev_dependencies),
            "env_vars": self.env_vars,
            "readme_sections": self.readme_sections,
            "llms_sections": self.llms_sections,
            "openapi_tags": self.openapi_tags,
            "enabled_integrations": self.enabled_integrations,
            "main_imports": self.main_imports,
            "app_hooks": self.app_hooks,
            "router_imports": self.router_imports,
            "router_includes": self.router_includes,
        }
