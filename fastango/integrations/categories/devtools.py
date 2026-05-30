"""Developer tooling integrations."""

from __future__ import annotations

from fastango.integrations.catalog import docs_integration

PRE_COMMIT_CONFIG = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-toml
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
"""

DEVTOOLS_INTEGRATIONS = (
    docs_integration(
        name="pre-commit",
        label="Pre-commit",
        category="devtools",
        description="Adds pre-commit configuration for generated projects.",
        dev_dependencies=("pre-commit>=4.0.0",),
        files=((".pre-commit-config.yaml", PRE_COMMIT_CONFIG),),
        tags=("quality", "git", "lint"),
        aliases=("precommit",),
    ),
    docs_integration(
        name="ruff",
        label="Ruff",
        category="devtools",
        description="Adds Ruff linting and formatting guidance.",
        dev_dependencies=("ruff>=0.8.0",),
        tags=("lint", "format", "quality"),
    ),
    docs_integration(
        name="mypy",
        label="mypy",
        category="devtools",
        description="Adds mypy type-checking dependency and guidance.",
        dev_dependencies=("mypy>=1.10.0",),
        tags=("typing", "quality", "ci"),
    ),
    docs_integration(
        name="pytest",
        label="pytest",
        category="devtools",
        description="Adds richer pytest dependency guidance.",
        dev_dependencies=("pytest-cov>=5.0.0",),
        tags=("tests", "quality", "coverage"),
        aliases=("testing",),
    ),
)
