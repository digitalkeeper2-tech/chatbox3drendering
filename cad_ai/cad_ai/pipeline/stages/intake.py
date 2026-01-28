"""Intake stage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil
from datetime import datetime


@dataclass
class IntakeResult:
    drawing_id: str
    intake_path: Path
    sha256: str


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def intake_file(source: Path, intake_dir: Path, counter: int) -> IntakeResult:
    date_stamp = datetime.now().strftime("%Y%m%d")
    drawing_id = f"DRW-{date_stamp}-{counter:06d}"
    intake_dir.mkdir(parents=True, exist_ok=True)
    target = intake_dir / f"{drawing_id}{source.suffix.lower()}"
    shutil.copy2(source, target)
    sha256 = compute_sha256(source)
    return IntakeResult(drawing_id=drawing_id, intake_path=target, sha256=sha256)
