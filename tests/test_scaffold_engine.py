from pathlib import Path

from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine


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
