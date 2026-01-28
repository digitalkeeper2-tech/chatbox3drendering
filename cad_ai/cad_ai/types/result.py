"""Pipeline result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StageTiming:
    stage: str
    seconds: float


@dataclass
class DrawingResult:
    drawing_id: str
    original_path: Path
    original_type: str
    lane: str
    sha256: str
    drawingjson_path: Path | None = None
    preview_pdf_path: Path | None = None
    dxf_path: Path | None = None
    report_path: Path | None = None
    issues: list[str] = field(default_factory=list)
    confidence: dict[str, float] = field(default_factory=dict)
    pages: list[dict[str, str]] = field(default_factory=list)
    timings: list[StageTiming] = field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        if self.original_type in {"png", "jpg", "jpeg"}:
            return True
        if any(page.get("lane") in {"raster", "unknown"} for page in self.pages):
            return True
        return self.confidence.get("overall", 1.0) < 0.9
