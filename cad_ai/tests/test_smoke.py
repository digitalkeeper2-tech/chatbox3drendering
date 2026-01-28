import tempfile
from pathlib import Path
import unittest

from cad_ai.config import resolve_paths, ensure_workspace_dirs
from cad_ai.pipeline.runner import PipelineRunner


class SmokeTest(unittest.TestCase):
    def test_pipeline_outputs(self) -> None:
        paths = resolve_paths()
        ensure_workspace_dirs(paths)
        runner = PipelineRunner(paths)

        with tempfile.TemporaryDirectory() as inbox_dir, tempfile.TemporaryDirectory() as out_dir:
            inbox_path = Path(inbox_dir)
            out_path = Path(out_dir)
            (inbox_path / "sample.dxf").write_text("0\nEOF", encoding="utf-8")
            (inbox_path / "sample.pdf").write_text("%PDF-1.4", encoding="utf-8")

            results = runner.run_once(inbox_path, out_path)

            self.assertEqual(len(results), 2)
            for result in results:
                output_dir = out_path / result.drawing_id
                self.assertTrue((output_dir / f"{result.drawing_id}.dxf").exists())
                self.assertTrue((output_dir / f"{result.drawing_id}.preview.pdf").exists())
                self.assertTrue((output_dir / f"{result.drawing_id}.report.json").exists())


if __name__ == "__main__":
    unittest.main()
