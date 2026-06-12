"""Correlation and reporting for application and test coverage maps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coverage_agent.blueprints import recommend_blueprint


class GapAnalysisEngine:
    """Compare discovered UI/API targets with statically mapped tests."""

    def __init__(self, coverage_map: dict[str, Any], application_map: dict[str, Any]):
        self.coverage_map = coverage_map
        self.application_map = application_map

    @classmethod
    def from_files(cls, coverage_map_path: str | Path, application_map_path: str | Path):
        """Load both input maps from JSON files."""
        return cls(cls._load_json(coverage_map_path), cls._load_json(application_map_path))

    @staticmethod
    def _load_json(path: str | Path) -> dict[str, Any]:
        with Path(path).open(encoding="utf-8") as file:
            value = json.load(file)
        if not isinstance(value, dict):
            raise ValueError(f"Expected a JSON object in {path}")
        return value

    def execute_diff(self) -> dict[str, Any]:
        """Return deterministic coverage metrics and missing target details."""
        discovered_ui = set(self.application_map.get("discovered_ui_elements", []))
        discovered_api = set(self.application_map.get("discovered_api_endpoints", []))
        covered_ui = self._covered(discovered_ui, {"ui", "visual"})
        covered_api = self._covered(discovered_api, {"api"})
        missing_ui = sorted(discovered_ui - covered_ui)
        missing_api = sorted(discovered_api - covered_api)

        return {
            "page": self.application_map.get("page", "unknown"),
            "metrics": {
                "ui_coverage_percent": self._percentage(len(covered_ui), len(discovered_ui)),
                "api_coverage_percent": self._percentage(len(covered_api), len(discovered_api)),
                "covered_ui": len(covered_ui),
                "total_ui": len(discovered_ui),
                "covered_api": len(covered_api),
                "total_api": len(discovered_api),
            },
            "gaps": {
                "missing_ui_testids": [
                    {"testid": target, "suggested_blueprint": recommend_blueprint(target, "ui")}
                    for target in missing_ui
                ],
                "missing_api_endpoints": [
                    {"endpoint": target, "suggested_blueprint": recommend_blueprint(target, "api")}
                    for target in missing_api
                ],
            },
        }

    def _covered(self, targets: set[str], accepted_types: set[str]) -> set[str]:
        return {
            target
            for target in targets
            if any(item.get("type") in accepted_types for item in self.coverage_map.get(target, []))
        }

    @staticmethod
    def _percentage(covered: int, total: int) -> float:
        return round(covered / total * 100, 1) if total else 100.0

    def write_gap_manifest(self, output_file: str | Path) -> dict[str, Any]:
        """Write and return the machine-readable gap report."""
        report = self.execute_diff()
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    def console_report(self) -> str:
        """Render a concise page-level report suitable for CI logs."""
        report = self.execute_diff()
        metrics = report["metrics"]
        gaps = report["gaps"]
        lines = [
            f"Coverage gap analysis for {report['page']}",
            f"UI: {metrics['ui_coverage_percent']:.1f}% ({metrics['covered_ui']}/{metrics['total_ui']})",
            f"API: {metrics['api_coverage_percent']:.1f}% ({metrics['covered_api']}/{metrics['total_api']})",
        ]
        for item in gaps["missing_ui_testids"]:
            lines.append(f"MISSING UI {item['testid']} -> {item['suggested_blueprint']}")
        for item in gaps["missing_api_endpoints"]:
            lines.append(f"MISSING API {item['endpoint']} -> {item['suggested_blueprint']}")
        return "\n".join(lines)
