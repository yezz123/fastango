"""Safe filesystem writes for generated projects."""

from __future__ import annotations

import stat
from dataclasses import dataclass
from pathlib import Path

from fastango.scaffold.plan import RenderedFile


class ScaffoldWriteError(RuntimeError):
    """Raised when Fastango cannot safely write generated files."""


@dataclass(frozen=True)
class WriteResult:
    target_dir: Path
    files: tuple[Path, ...]
    dry_run: bool = False


def write_files(
    target_dir: Path,
    files: list[RenderedFile],
    *,
    force: bool = False,
    dry_run: bool = False,
) -> WriteResult:
    """Write rendered files into a target directory without path traversal."""

    target_dir = target_dir.resolve()
    paths = tuple(target_dir / file.path for file in files)

    for path in paths:
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(target_dir):
            raise ScaffoldWriteError(f"Refusing to write outside target directory: {path}")
        if path.exists() and not force:
            raise ScaffoldWriteError(
                f"File already exists: {path}. Re-run with --force to overwrite."
            )

    if dry_run:
        return WriteResult(target_dir=target_dir, files=paths, dry_run=True)

    target_dir.mkdir(parents=True, exist_ok=True)
    for file, path in zip(files, paths, strict=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file.content, encoding="utf-8")
        if file.executable:
            path.chmod(path.stat().st_mode | stat.S_IXUSR)

    return WriteResult(target_dir=target_dir, files=paths, dry_run=False)
