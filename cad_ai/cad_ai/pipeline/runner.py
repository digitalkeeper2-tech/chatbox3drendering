"""Pipeline runner."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from cad_ai.config import Paths, ensure_workspace_dirs
from cad_ai.types.result import DrawingResult, StageTiming
from cad_ai.pipeline.stages.classify import classify_file
from cad_ai.pipeline.stages.extract_vector import extract_vector
from cad_ai.pipeline.stages.reconstruct_raster import reconstruct_raster
from cad_ai.pipeline.stages.normalize import normalize_drawing
from cad_ai.pipeline.stages.export_dxf import export_dxf
from cad_ai.pipeline.stages.export_preview_pdf import export_preview_pdf
from cad_ai.pipeline.stages.report import write_report
from cad_ai.pipeline.stages.intake import intake_file


SUPPORTED_EXTENSIONS = {".dxf", ".dwg", ".pdf", ".svg", ".png", ".jpg", ".jpeg"}


def list_inbox_files(inbox: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in inbox.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
    )


class PipelineRunner:
    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        ensure_workspace_dirs(paths)
        self._counter = 1

    def run_once(self, inbox: Path, out_dir: Path | None = None) -> list[DrawingResult]:
        results: list[DrawingResult] = []
        for file_path in list_inbox_files(inbox):
            results.append(self._process_file(file_path, out_dir))
        return results

    def run_watch(self, inbox: Path, out_dir: Path | None = None) -> list[DrawingResult]:
        logging.info("Watch mode enabled. Polling inbox every 2 seconds.")
        processed: set[tuple[str, str]] = set()
        collected: list[DrawingResult] = []
        try:
            while True:
                for file_path in list_inbox_files(inbox):
                    sha = self._safe_sha(file_path)
                    key = (sha, file_path.name)
                    if key in processed:
                        continue
                    result = self._process_file(file_path, out_dir)
                    collected.append(result)
                    processed.add(key)
                time.sleep(2)
        except KeyboardInterrupt:
            logging.info("Watch mode terminated by user.")
        return collected

    def _safe_sha(self, path: Path) -> str:
        from cad_ai.pipeline.stages.intake import compute_sha256

        try:
            return compute_sha256(path)
        except FileNotFoundError:
            return ""

    def _process_file(self, file_path: Path, out_dir: Path | None) -> DrawingResult:
        logging.info("Processing %s", file_path.name)
        intake_result = intake_file(file_path, self.paths.intake, self._counter)
        self._counter += 1

        result = DrawingResult(
            drawing_id=intake_result.drawing_id,
            original_path=file_path,
            original_type="",
            lane="",
            sha256=intake_result.sha256,
        )

        stage_start = time.perf_counter()
        original_type, lane, pages, issues = classify_file(intake_result.intake_path)
        result.original_type = original_type
        result.lane = lane
        result.pages = pages
        result.issues.extend(issues)
        result.timings.append(StageTiming("classify", time.perf_counter() - stage_start))

        stage_start = time.perf_counter()
        if lane == "vector":
            drawing = extract_vector(intake_result.intake_path, result.drawing_id)
            result.confidence = {"ocr": 1.0, "dims": 0.95, "symbols": 0.95, "overall": 0.95}
        else:
            drawing, raster_issues = reconstruct_raster(
                intake_result.intake_path, result.drawing_id
            )
            result.issues.extend(raster_issues)
            result.confidence = {"ocr": 0.5, "dims": 0.5, "symbols": 0.5, "overall": 0.5}
        result.timings.append(
            StageTiming(
                "extract_vector" if lane == "vector" else "reconstruct_raster",
                time.perf_counter() - stage_start,
            )
        )

        stage_start = time.perf_counter()
        normalized = normalize_drawing(drawing, self.paths.standards)
        normalized_path = self.paths.normalized / f"{result.drawing_id}.drawing.json"
        normalized_path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
        result.drawingjson_path = normalized_path
        result.timings.append(StageTiming("normalize", time.perf_counter() - stage_start))

        stage_start = time.perf_counter()
        dxf_output_dir = (out_dir or self.paths.outputs) / result.drawing_id
        dxf_path = dxf_output_dir / f"{result.drawing_id}.dxf"
        export_dxf(normalized, dxf_path)
        result.dxf_path = dxf_path
        result.timings.append(StageTiming("export_dxf", time.perf_counter() - stage_start))

        stage_start = time.perf_counter()
        preview_path = dxf_output_dir / f"{result.drawing_id}.preview.pdf"
        export_preview_pdf(preview_path, result.drawing_id, file_path.name, lane)
        result.preview_pdf_path = preview_path
        result.timings.append(
            StageTiming("export_preview_pdf", time.perf_counter() - stage_start)
        )

        stage_start = time.perf_counter()
        report_path = write_report(result, dxf_output_dir)
        result.report_path = report_path
        result.timings.append(StageTiming("report", time.perf_counter() - stage_start))

        if result.needs_review:
            self._create_review_queue(result, intake_result.intake_path)

        logging.info("Completed %s", result.drawing_id)
        return result

    def _create_review_queue(self, result: DrawingResult, intake_path: Path) -> None:
        queue_dir = self.paths.review_queue / result.drawing_id
        queue_dir.mkdir(parents=True, exist_ok=True)
        (queue_dir / intake_path.name).write_bytes(intake_path.read_bytes())
        if result.preview_pdf_path:
            (queue_dir / result.preview_pdf_path.name).write_bytes(
                result.preview_pdf_path.read_bytes()
            )
        if result.report_path:
            (queue_dir / result.report_path.name).write_bytes(
                result.report_path.read_bytes()
            )
        issues_path = queue_dir / "issues.md"
        issues_lines = [
            f"# Review Queue Entry: {result.drawing_id}",
            "",
            f"Original file: {result.original_path.name}",
            f"Lane: {result.lane}",
            f"Needs review: {result.needs_review}",
            "",
            "## Issues",
        ]
        if result.issues:
            issues_lines.extend([f"- {issue}" for issue in result.issues])
        else:
            issues_lines.append("- No issues recorded")
        issues_path.write_text("\n".join(issues_lines), encoding="utf-8")
