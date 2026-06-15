"""Generate the persistent Allure HTML report from collected test results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.allure_report import generate_allure_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="allure-results")
    parser.add_argument("--output", default="allure-report")
    parser.add_argument("--allure-command", default="allure")
    parser.add_argument("--name", default=None, help="Optional report directory name")
    args = parser.parse_args()

    result = generate_allure_report(
        args.results,
        args.output,
        allure_command=args.allure_command,
        report_name=args.name,
    )
    print(result.message)
    return 0 if result.succeeded else result.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
