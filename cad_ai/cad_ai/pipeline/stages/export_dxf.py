"""DXF export stage."""

from __future__ import annotations

from pathlib import Path
from cad_ai.types.drawingjson import DrawingJSON


def export_dxf(drawing: DrawingJSON, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "0",
            "SECTION",
            "2",
            "HEADER",
            "9",
            "$COMMENT",
            "1",
            "cad_ai placeholder DXF - export not implemented",
            "0",
            "ENDSEC",
            "0",
            "SECTION",
            "2",
            "ENTITIES",
            "0",
            "ENDSEC",
            "0",
            "EOF",
        ]
    )
    output_path.write_text(content, encoding="utf-8")
