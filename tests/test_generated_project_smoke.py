import os
import subprocess
from pathlib import Path

import pytest

from fastango.generator.models import GenerationRequest
from fastango.generator.planner import build_generation_plan
from fastango.scaffold.config import ProjectConfig
from fastango.scaffold.engine import ScaffoldEngine


@pytest.mark.slow
@pytest.mark.skipif(
    os.environ.get("FASTANGO_RUN_SLOW") != "1",
    reason="Set FASTANGO_RUN_SLOW=1 to run uv-based generated-project smoke tests.",
)
def test_generated_api_starter_project_passes_its_tests(tmp_path: Path) -> None:
    config = ProjectConfig(project_name="smoke-api", output_dir=tmp_path, presets=("api-starter",))
    result = ScaffoldEngine().create(config)

    subprocess.run(["uv", "sync"], cwd=result.target_dir, check=True)
    subprocess.run(["uv", "run", "pytest"], cwd=result.target_dir, check=True)


@pytest.mark.slow
@pytest.mark.skipif(
    os.environ.get("FASTANGO_RUN_SLOW") != "1",
    reason="Set FASTANGO_RUN_SLOW=1 to run uv-based generated-project smoke tests.",
)
def test_generated_starter_mvp_project_passes_its_tests(tmp_path: Path) -> None:
    plan = build_generation_plan(
        GenerationRequest(prompt="a starter MVP with auth billing email analytics")
    )
    config = plan.to_project_config(output_dir=tmp_path)
    result = ScaffoldEngine().create(config)

    subprocess.run(["uv", "sync"], cwd=result.target_dir, check=True)
    subprocess.run(["uv", "run", "pytest"], cwd=result.target_dir, check=True)
