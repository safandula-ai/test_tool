"""Command-line orchestration for coverage analysis."""

from __future__ import annotations

import argparse
import asyncio

from coverage_agent.analyzer import generate_coverage_map
from coverage_agent.discovery import PlaywrightDiscoveryEngine
from coverage_agent.gap_analysis import GapAnalysisEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m coverage_agent")
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Generate coverage_map.json")
    analyze.add_argument("--tests", default="tests")
    analyze.add_argument("--output", default="reports/coverage_map.json")

    discover = commands.add_parser("discover", help="Generate application_map.json")
    discover.add_argument("--base-url", required=True)
    discover.add_argument("--path", default="/")
    discover.add_argument("--output", default="reports/application_map.json")
    discover.add_argument("--auth-state")
    discover.add_argument("--save-state")
    discover.add_argument("--headed", action="store_true")

    gaps = commands.add_parser("gaps", help="Generate gap_report.json")
    gaps.add_argument("--coverage", default="reports/coverage_map.json")
    gaps.add_argument("--application", default="reports/application_map.json")
    gaps.add_argument("--output", default="reports/gap_report.json")
    return parser


async def _discover(args: argparse.Namespace) -> None:
    engine = PlaywrightDiscoveryEngine(args.base_url)
    await engine.scrape_page(
        args.path,
        auth_state_path=args.auth_state,
        save_state_path=args.save_state,
        headless=not args.headed,
    )
    engine.write_application_manifest(args.path, args.output)


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "analyze":
        coverage = generate_coverage_map(args.tests, args.output)
        print(f"Mapped {sum(map(len, coverage.values()))} test target(s) to {args.output}")
    elif args.command == "discover":
        asyncio.run(_discover(args))
        print(f"Wrote application map to {args.output}")
    else:
        engine = GapAnalysisEngine.from_files(args.coverage, args.application)
        engine.write_gap_manifest(args.output)
        print(engine.console_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
