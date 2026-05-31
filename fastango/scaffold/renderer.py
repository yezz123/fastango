"""Template rendering for scaffold plans."""

from __future__ import annotations

from collections.abc import Iterable
from importlib import resources
from pathlib import PurePosixPath
from typing import Protocol

from jinja2 import Environment, StrictUndefined

from fastango.scaffold.plan import RenderedFile, ScaffoldPlan


class TraversableResource(Protocol):
    @property
    def name(self) -> str: ...  # pragma: no cover

    def iterdir(self) -> Iterable[TraversableResource]: ...  # pragma: no cover

    def is_dir(self) -> bool: ...  # pragma: no cover

    def is_file(self) -> bool: ...  # pragma: no cover

    def read_text(self, encoding: str | None = None) -> str: ...  # pragma: no cover


class TemplateRenderer:
    """Render packaged project templates and integration file specs."""

    def __init__(self) -> None:
        self.environment = Environment(
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def render_plan(self, plan: ScaffoldPlan) -> list[RenderedFile]:
        context = plan.context()
        rendered = self._render_template_directory(plan, context)
        rendered.extend(self._render_file_specs(plan, context))
        return rendered

    def _render_template_directory(
        self, plan: ScaffoldPlan, context: dict[str, object]
    ) -> list[RenderedFile]:
        root = resources.files("fastango.templates.project").joinpath(plan.config.style)
        files: list[RenderedFile] = []
        for relative_path, resource in self._walk(root):
            output_path = self._render_path(relative_path, context)
            if output_path.endswith(".j2"):
                output_path = output_path.removesuffix(".j2")
            template = self.environment.from_string(resource.read_text(encoding="utf-8"))
            files.append(
                RenderedFile(
                    path=PurePosixPath(output_path),
                    content=template.render(context),
                    executable=False,
                )
            )
        return files

    def _render_file_specs(
        self, plan: ScaffoldPlan, context: dict[str, object]
    ) -> list[RenderedFile]:
        rendered: list[RenderedFile] = []
        for file_spec in plan.files:
            path = self._render_path(file_spec.path, context)
            template = self.environment.from_string(file_spec.content)
            rendered.append(
                RenderedFile(
                    path=PurePosixPath(path),
                    content=template.render(context),
                    executable=file_spec.executable,
                )
            )
        return rendered

    def _render_path(self, path: str, context: dict[str, object]) -> str:
        template = self.environment.from_string(path)
        rendered = template.render(context)
        if rendered.startswith("/") or ".." in PurePosixPath(rendered).parts:
            raise ValueError(f"Unsafe template path generated: {rendered}")
        return rendered

    def _walk(
        self, root: TraversableResource, prefix: str = ""
    ) -> list[tuple[str, TraversableResource]]:
        files: list[tuple[str, TraversableResource]] = []
        for resource in sorted(root.iterdir(), key=lambda item: item.name):
            relative_path = f"{prefix}/{resource.name}" if prefix else resource.name
            if resource.is_dir():
                files.extend(self._walk(resource, relative_path))
            elif resource.is_file():
                files.append((relative_path, resource))
        return files
