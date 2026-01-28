"""PDF preview export stage."""

from __future__ import annotations

from pathlib import Path


def _build_pdf(lines: list[str]) -> bytes:
    def escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    y_start = 760
    y_step = 16
    text_lines = [f"({escape(line)}) Tj" for line in lines]
    text_block = ["BT", "/F1 12 Tf", "72 760 Td"]
    for idx, line in enumerate(text_lines):
        if idx == 0:
            text_block.append(line)
        else:
            text_block.append(f"0 -{y_step} Td")
            text_block.append(line)
    text_block.append("ET")
    stream = "\n".join(text_block)

    objects: list[bytes] = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    )
    stream_bytes = stream.encode("utf-8")
    objects.append(
        f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n{stream}\nendstream\nendobj\n".encode(
            "utf-8"
        )
    )
    objects.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    output = bytearray()
    output.extend(b"%PDF-1.4\n")
    xref_positions = [0]
    for obj in objects:
        xref_positions.append(len(output))
        output.extend(obj)
    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects)+1}\n".encode("utf-8"))
    output.extend(b"0000000000 65535 f \n")
    for pos in xref_positions[1:]:
        output.extend(f"{pos:010d} 00000 n \n".encode("utf-8"))
    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects)+1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_start}\n"
            "%%EOF\n"
        ).encode("utf-8")
    )
    return bytes(output)


def export_preview_pdf(
    output_path: Path,
    drawing_id: str,
    original_filename: str,
    lane: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "cad_ai preview placeholder",
        f"Drawing ID: {drawing_id}",
        f"Original file: {original_filename}",
        f"Lane: {lane}",
    ]
    output_path.write_bytes(_build_pdf(lines))
