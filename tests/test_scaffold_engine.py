from pathlib import Path

import pytest
from pytest import MonkeyPatch

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine
from fastango.scaffold.filesystem import ScaffoldWriteError, write_files
from fastango.scaffold.plan import EnvVar, FileSpec, RenderedFile, ScaffoldPlan
from fastango.scaffold.renderer import TemplateRenderer


def test_simple_project_is_generated(tmp_path: Path) -> None:
    config = ProjectConfig(
        project_name="billing-api", output_dir=tmp_path, integrations=("openapi",)
    )

    result = ScaffoldEngine().create(config)

    assert (result.target_dir / "pyproject.toml").exists()
    assert (result.target_dir / "app/main.py").exists()
    assert (result.target_dir / "tests/test_health.py").exists()
    assert "FastAPI" in (result.target_dir / "llms.txt").read_text(encoding="utf-8")


def test_mvc_project_with_business_integrations_is_generated(tmp_path: Path) -> None:
    config = ProjectConfig(
        project_name="billing-api",
        output_dir=tmp_path,
        style="mvc",
        integrations=("authx", "stripe", "postgres", "redis", "docker", "tests"),
    )

    result = ScaffoldEngine().create(config)

    assert (result.target_dir / "app/api/routes/auth.py").exists()
    assert (result.target_dir / "app/api/routes/billing.py").exists()
    assert (result.target_dir / "app/core/database.py").exists()
    assert (result.target_dir / "app/core/cache.py").exists()
    assert (result.target_dir / "Dockerfile").exists()
    env_example = (result.target_dir / ".env.example").read_text(encoding="utf-8")
    assert "STRIPE_SECRET_KEY=" in env_example
    assert "DATABASE_URL=postgresql+asyncpg" in env_example


def test_dry_run_does_not_write_files(tmp_path: Path) -> None:
    config = ProjectConfig(project_name="preview-api", output_dir=tmp_path)

    result = ScaffoldEngine().create(config, dry_run=True)

    assert result.dry_run is True
    assert result.files
    assert not config.target_dir.exists()


def test_filesystem_rejects_existing_and_writes_executable(tmp_path: Path) -> None:
    rendered = [RenderedFile(path=Path("script.sh"), content="echo hi", executable=True)]  # type: ignore[arg-type]
    result = write_files(tmp_path / "project", rendered)

    script = result.files[0]
    assert script.exists()
    assert script.stat().st_mode & 0o100

    with pytest.raises(ScaffoldWriteError):
        write_files(tmp_path / "project", rendered)


def test_filesystem_rejects_path_traversal(tmp_path: Path) -> None:
    rendered = [RenderedFile(path=Path("../escape.txt"), content="", executable=False)]  # type: ignore[arg-type]

    with pytest.raises(ScaffoldWriteError):
        write_files(tmp_path / "project", rendered)


def test_plan_add_router_and_file_spec() -> None:
    plan = ScaffoldPlan(ProjectConfig(project_name="demo"))
    plan.add_file("app/example.py", "print('{{ project_name }}')")
    plan.add_router("from app.example import router", "app.include_router(router)")

    assert isinstance(plan.files[0], FileSpec)
    assert plan.router_imports == ["from app.example import router"]
    assert plan.router_includes == ["app.include_router(router)"]

    plan.add_dependency("fastapi")
    plan.add_dependency("fastapi")
    plan.add_dev_dependency("pytest")
    plan.add_dev_dependency("pytest")
    plan.add_env_var(plan.env_vars[0] if plan.env_vars else EnvVar("A"))
    plan.add_env_var(EnvVar("A"))
    plan.add_openapi_tag("x", "X")
    plan.add_openapi_tag("x", "X")
    plan.add_main_import("import os")
    plan.add_main_import("import os")
    plan.add_app_hook("pass")
    plan.add_app_hook("pass")
    plan.add_router("from app.example import router", "app.include_router(router)")
    assert plan.dependencies == ["fastapi"]
    assert plan.dev_dependencies == ["pytest"]


def test_renderer_rejects_unsafe_template_path() -> None:
    renderer = TemplateRenderer()

    with pytest.raises(ValueError):
        renderer._render_path("../escape.txt", {})  # noqa: SLF001


def test_renderer_file_specs_render_context() -> None:
    plan = ScaffoldPlan(ProjectConfig(project_name="demo"))
    plan.add_file("{{ package_name }}/value.txt", "{{ project_name }}")

    files = TemplateRenderer()._render_file_specs(plan, plan.context())  # noqa: SLF001

    assert files[0].path.as_posix() == "demo/value.txt"
    assert files[0].content == "demo"


def test_renderer_template_directory_handles_non_j2_and_unknown_resource(
    monkeypatch: MonkeyPatch,
) -> None:
    class FakeResource:
        def __init__(
            self,
            name: str,
            *,
            text: str = "",
            children: list["FakeResource"] | None = None,
            is_file: bool = True,
        ) -> None:
            self.name = name
            self.text = text
            self.children = children or []
            self._is_file = is_file

        def joinpath(self, _: str) -> "FakeResource":
            return self

        def iterdir(self) -> list["FakeResource"]:
            return self.children

        def is_dir(self) -> bool:
            return bool(self.children)

        def is_file(self) -> bool:
            return self._is_file

        def read_text(self, encoding: str | None = None) -> str:
            return self.text

    root = FakeResource(
        "root",
        children=[
            FakeResource("ignored", is_file=False),
            FakeResource("plain.txt", text="hello"),
        ],
        is_file=False,
    )
    monkeypatch.setattr("fastango.scaffold.renderer.resources.files", lambda _: root)
    plan = ScaffoldPlan(ProjectConfig(project_name="demo"))

    files = TemplateRenderer()._render_template_directory(plan, plan.context())  # noqa: SLF001

    assert files[0].path.as_posix() == "plain.txt"


def test_engine_git_init_path(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    calls: list[object] = []
    monkeypatch.setattr(
        "fastango.scaffold.engine.subprocess.run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    config = ProjectConfig(project_name="git-api", output_dir=tmp_path, create_git=True)
    ScaffoldEngine().create(config)

    assert calls
