"""CLI entrypoint."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
import unittest

from cad_ai.config import resolve_paths
from cad_ai.logging_utils import setup_logging
from cad_ai.pipeline.runner import PipelineRunner


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cad_ai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the pipeline")
    run_parser.add_argument("--inbox", type=Path, required=True, help="Inbox path")
    run_parser.add_argument("--out", type=Path, help="Output path")
    run_parser.add_argument("--watch", action="store_true", help="Watch inbox")

    subparsers.add_parser("selftest", help="Run smoke tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    paths = resolve_paths()
    setup_logging(paths.logs)

    if args.command == "selftest":
        logging.info("Running self tests")
        suite = unittest.defaultTestLoader.discover(str(paths.root / "tests"))
        result = unittest.TextTestRunner().run(suite)
        return 0 if result.wasSuccessful() else 1

    runner = PipelineRunner(paths)
    try:
        if args.command == "run":
            if args.watch:
                runner.run_watch(args.inbox, args.out)
            else:
                runner.run_once(args.inbox, args.out)
        return 0
    except Exception:
        logging.exception("Pipeline failed")
        return 2
