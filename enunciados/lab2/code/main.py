from __future__ import annotations

import argparse

from main_sprint1 import main as sprint1_main
from main_sprint2 import main as sprint2_main


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab2 runner")
    parser.add_argument(
        "--sprint",
        choices=["1", "2"],
        default="2",
        help="Choose which sprint script to execute.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only run Sprint 2 analysis logic from CSV (without generating report file).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.report_only:
        try:
            from generate_report import main as report_main
        except Exception as ex:
            raise RuntimeError(
                "generate_report.py não está pronto para execução. "
                "Preencha a lógica de análise antes de usar --report-only."
            ) from ex
        report_main()
        return

    if args.sprint == "1":
        sprint1_main()
        return

    sprint2_main()


if __name__ == "__main__":
    main()
