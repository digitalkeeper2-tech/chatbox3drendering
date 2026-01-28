"""Classification stage."""

from __future__ import annotations

from pathlib import Path


def classify_file(path: Path) -> tuple[str, str, list[dict[str, str]], list[str]]:
    ext = path.suffix.lower().lstrip(".")
    issues: list[str] = []
    pages: list[dict[str, str]] = []

    if ext in {"dxf", "svg"}:
        lane = "vector"
    elif ext in {"dwg"}:
        lane = "vector"
        issues.append("DWG ingestion not implemented; treated as vector placeholder.")
    elif ext in {"png", "jpg", "jpeg"}:
        lane = "raster"
        issues.append("Raster image input.")
    elif ext == "pdf":
        lane = "raster"
        # TODO: detect vector vs raster PDF pages when PDF parsing is implemented.
        pages = [{"page": "1", "lane": "unknown"}]
        issues.append("PDF classification is unknown; defaulting to raster lane.")
    else:
        lane = "raster"
        issues.append(f"Unknown extension '{ext}'; defaulting to raster lane.")

    return ext, lane, pages, issues
