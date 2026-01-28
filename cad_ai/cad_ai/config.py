"""Configuration helpers for cad_ai."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    root: Path
    workspace: Path
    logs: Path
    standards: Path
    inbox: Path

    @property
    def intake(self) -> Path:
        return self.workspace / "00_intake"

    @property
    def classified(self) -> Path:
        return self.workspace / "01_classified"

    @property
    def extracted(self) -> Path:
        return self.workspace / "02_extracted"

    @property
    def reconstructed(self) -> Path:
        return self.workspace / "03_reconstructed"

    @property
    def normalized(self) -> Path:
        return self.workspace / "04_normalized"

    @property
    def outputs(self) -> Path:
        return self.workspace / "05_outputs"

    @property
    def review_queue(self) -> Path:
        return self.workspace / "06_review_queue"


def resolve_paths(root: Path | None = None) -> Paths:
    repo_root = (root or Path(__file__).resolve().parents[1]).resolve()
    return Paths(
        root=repo_root,
        workspace=repo_root / "workspace",
        logs=repo_root / "logs",
        standards=repo_root / "standards",
        inbox=repo_root / "inbox" / "raw",
    )


def ensure_workspace_dirs(paths: Paths) -> None:
    for directory in [
        paths.workspace,
        paths.intake,
        paths.classified,
        paths.extracted,
        paths.reconstructed,
        paths.normalized,
        paths.outputs,
        paths.review_queue,
        paths.logs,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
