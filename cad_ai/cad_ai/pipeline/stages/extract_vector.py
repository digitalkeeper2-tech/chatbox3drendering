"""Vector extraction stage."""

from __future__ import annotations

from pathlib import Path
from cad_ai.types.drawingjson import DrawingJSON, create_placeholder_drawing


def extract_vector(path: Path, drawing_id: str) -> DrawingJSON:
    metadata = {
        "source": str(path),
        "drawing_id": drawing_id,
        "lane": "vector",
        "note": "Vector extraction not implemented; placeholder drawing only.",
    }
    return create_placeholder_drawing(metadata)
