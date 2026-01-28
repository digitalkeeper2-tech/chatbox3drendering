"""Normalization stage."""

from __future__ import annotations

import json
from pathlib import Path
from copy import deepcopy

from cad_ai.types.drawingjson import DrawingJSON


def normalize_drawing(drawing: DrawingJSON, standards_dir: Path) -> DrawingJSON:
    normalized = deepcopy(drawing)
    layers_path = standards_dir / "layers.json"
    if layers_path.exists():
        layers = json.loads(layers_path.read_text(encoding="utf-8"))
        normalized["layers"] = layers
    return normalized
