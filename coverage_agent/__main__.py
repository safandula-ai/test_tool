"""Command-line orchestration for coverage analysis."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from config.settings import get_settings
from coverage_agent.analyzer import build_coverage_indexes, generate_coverage_map
from coverage_agent.discovery import PlaywrightDiscoveryEngine
from coverage_agent.gap_analysis import GapAnalysisEngine
from coverage_agent.gap_scaffolder import scaffold_gap_tests
from coverage_agent.manifests import load_manifests
from coverage_agent.suite_layout import ensure_website_suite
from coverage_agent.template_engine import DynamicSuiteAssembler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m coverage_agent")
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Generate coverage_map.json")
    analyze.add_argument("--tests", default="tests")
    analyze.add_argument("--output", default="reports/coverage_map.json")

    discover = commands.add_parser("discover", help="Generate application_map.json")
    discover.add_argument("--base-url", default=get_settings().base_url)
    discover_target = discover.add_mutually_exclusive_group()
    discover_target.add_argument("--path")
    discover_target.add_argument("--file")
    discover.add_argument("--output", default="reports/application_map.json")
    discover.add_argument("--auth-state")
    discover.add_argument("--save-state")
    discover.add_argument("--headed", action="store_true")
    discover.add_argument("--scan-distance", type=int, default=350)
    discover.add_argument("--step-delay-ms", type=int, default=600)
    discover.add_argument("--sniff-interval-ms", type=int, default=100)
    discover.add_argument("--max-scan-steps", type=int, default=100)
    discover.add_argument("--challenge-timeout-ms", type=int, default=15_000)

    gaps = commands.add_parser("gaps", help="Generate gap_report.json")
    gaps.add_argument("--coverage", default="reports/coverage_map.json")
    gaps.add_argument("--application", default="reports/application_map.json")
    gaps.add_argument("--output", default="reports/gap_report.json")

    assemble = commands.add_parser("assemble", help="Assemble templates for a discovered page")
    assemble.add_argument("--application", default="reports/application_map.json")
    assemble.add_argument("--manifests", default="config/test_manifests.json")
    assemble.add_argument("--output", default="reports/assembled_suite.json")

    select = commands.add_parser("select", help="Select tests by page, feature, or template")
    select.add_argument("--coverage", default="reports/coverage_map.json")
    select.add_argument("--page")
    select.add_argument("--feature")
    select.add_argument("--template")

    indexes = commands.add_parser("indexes", help="Build page, feature, and template indexes")
    indexes.add_argument("--coverage", default="reports/coverage_map.json")
    indexes.add_argument("--output", default="reports/coverage_indexes.json")

    scaffold = commands.add_parser("scaffold-gaps", help="Generate executable tests for gaps")
    scaffold.add_argument("--report", default="reports/gap_report.json")
    scaffold.add_argument("--output")
    scaffold.add_argument("--base-url-setting", default="base_url")
    scaffold.add_argument("--feature", default="feature:generated-gap-coverage")
    return parser


async def _discover(args: argparse.Namespace) -> dict[str, object]:
    if not args.base_url:
        raise ValueError("Provide --base-url or set BASE_URL")
    suite = ensure_website_suite(args.base_url)
    engine = PlaywrightDiscoveryEngine(args.base_url)
    if args.file:
        manifest = await engine.scrape_documentation_file(args.file)
        manifest_page = engine.documentation_source_page(args.file)
    else:
        target_path = args.path or "/"
        manifest = await engine.scrape_page(
            target_path,
            auth_state_path=args.auth_state,
            save_state_path=args.save_state,
            headless=not args.headed,
            scan_distance=args.scan_distance,
            step_delay_ms=args.step_delay_ms,
            sniff_interval_ms=args.sniff_interval_ms,
            max_scan_steps=args.max_scan_steps,
            challenge_timeout_ms=args.challenge_timeout_ms,
        )
        manifest_page = target_path
    engine.write_application_manifest(manifest_page, args.output)
    print(f"Website suite: {suite.root}")
    return manifest


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "analyze":
        coverage = generate_coverage_map(args.tests, args.output)
        print(f"Mapped {sum(map(len, coverage.values()))} test target(s) to {args.output}")
    elif args.command == "discover":
        manifest = asyncio.run(_discover(args))
        print(f"Wrote application map to {args.output}")
        if manifest["scan_status"] != "complete":
            print("ERROR Security challenge did not clear; discovery scan was not executed")
            return 2
    elif args.command == "gaps":
        engine = GapAnalysisEngine.from_files(args.coverage, args.application)
        report = engine.write_gap_manifest(args.output)
        print(engine.console_report())
        return 1 if report["errors"] else 0
    elif args.command == "assemble":
        application_map = json.loads(Path(args.application).read_text(encoding="utf-8"))
        suite = DynamicSuiteAssembler().assemble(application_map, load_manifests(args.manifests))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(suite, indent=2) + "\n", encoding="utf-8")
        print(f"Assembled {len(suite['suite'])} template invocation(s) to {args.output}")
        for suggestion in suite["suggestions"]:
            print(f"SUGGEST {suggestion['target']}: {', '.join(suggestion['recommended_templates'])}")
    elif args.command == "select":
        coverage_map = json.loads(Path(args.coverage).read_text(encoding="utf-8"))
        selected = DynamicSuiteAssembler.select_tests(
            coverage_map,
            page=args.page,
            feature=args.feature,
            template=args.template,
        )
        print("\n".join(selected))
    elif args.command == "indexes":
        coverage_map = json.loads(Path(args.coverage).read_text(encoding="utf-8"))
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(build_coverage_indexes(coverage_map), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote coverage indexes to {args.output}")
    else:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        output = args.output
        if output is None:
            base_url = report.get("base_url")
            if not base_url:
                raise ValueError("Gap report has no base_url; pass --output explicitly")
            output = str(ensure_website_suite(base_url).generated_test_file)
        count = scaffold_gap_tests(
            args.report,
            output,
            base_url_setting=args.base_url_setting,
            feature=args.feature,
        )
        print(f"Generated {count} gap test(s) in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
