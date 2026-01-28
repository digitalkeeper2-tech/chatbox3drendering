"""Raster reconstruction stage."""

from __future__ import annotations

from pathlib import Path
from cad_ai.types.drawingjson import DrawingJSON, create_placeholder_drawing


def reconstruct_raster(path: Path, drawing_id: str) -> tuple[DrawingJSON, list[str]]:
    metadata = {
        "source": str(path),
        "drawing_id": drawing_id,
        "lane": "raster",
        "note": "Raster reconstruction not implemented; placeholder drawing only.",
    }
    drawing = create_placeholder_drawing(metadata)
    issues = ["Raster reconstruction not implemented"]
    return drawing, issues
