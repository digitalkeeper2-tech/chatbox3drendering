# cad_ai

Windows-first skeleton for a mixed drawing pipeline that ingests CAD/vector/raster files and emits DXF, PDF previews, and JSON reports.

## Install (Windows PowerShell)

```powershell
cd cad_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Run once

```powershell
python -m cad_ai run --inbox .\inbox\raw --out .\workspace\05_outputs
```

## Watch mode

```powershell
python -m cad_ai run --inbox .\inbox\raw --out .\workspace\05_outputs --watch
```

## Lanes and review queue

- **Vector lane**: DXF/SVG/DWG placeholders. Exports a placeholder DXF and PDF preview.
- **Raster lane**: PNG/JPG and PDFs default to raster/unknown for safety.
- **Review queue**: Any raster/unknown PDF pages, PNG/JPG inputs, or low confidence results (< 0.90) are copied into `workspace/06_review_queue/DRW-<id>/` with the original, preview PDF, report JSON, and an `issues.md` summary.

## Where to add real logic later

- **PDF vector/raster detection**: `cad_ai/pipeline/stages/classify.py`
- **Vector extraction**: `cad_ai/pipeline/stages/extract_vector.py`
- **Raster reconstruction**: `cad_ai/pipeline/stages/reconstruct_raster.py`
- **DXF export**: `cad_ai/pipeline/stages/export_dxf.py`
- **Preview PDF rendering**: `cad_ai/pipeline/stages/export_preview_pdf.py`

## Self-test

```powershell
python -m cad_ai selftest
```
