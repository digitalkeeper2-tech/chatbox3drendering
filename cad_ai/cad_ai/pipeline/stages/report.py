"""Report stage."""

from __future__ import annotations

import json
from pathlib import Path
from cad_ai.types.result import DrawingResult


def write_report(result: DrawingResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{result.drawing_id}.report.json"
    payload = {
        "id": result.drawing_id,
        "original_filename": result.original_path.name,
        "original_type": result.original_type,
        "pages": result.pages,
        "outputs": {
            "dxf": str(result.dxf_path) if result.dxf_path else None,
            "preview_pdf": str(result.preview_pdf_path) if result.preview_pdf_path else None,
        },
        "needs_review": result.needs_review,
        "issues": result.issues,
        "confidence": result.confidence,
        "timings": [
            {"stage": timing.stage, "seconds": timing.seconds}
            for timing in result.timings
        ],
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path
