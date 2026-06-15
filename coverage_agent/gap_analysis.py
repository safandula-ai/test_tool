"""Diff the application and coverage maps to find untested surface area."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GapReport:
    """A summary of the coverage gaps for a given application map."""

    base_url: str
    page: str
    untested_ui_elements: list[str] = field(default_factory=list)
    untested_api_endpoints: list[object] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class GapAnalysisEngine:
    """Finds gaps in test coverage by diffing discovery and coverage reports."""

    def __init__(
        self,
        application_map: dict[str, object],
        coverage_map: dict[str, object],
    ):
        self.application_map = application_map
        self.coverage_map = coverage_map

    def execute_diff(self) -> dict[str, object]:
        """Compare the application and coverage maps to find untested endpoints."""
        errors: list[str] = []
        if not self.application_map:
            errors.append("Application map is empty or invalid")
        if not self.coverage_map:
            errors.append("Coverage map is empty or invalid")
        if errors:
            return self._build_report(errors=errors)

        discovered_endpoints = self.application_map.get("discovered_api_endpoints", [])
        normalized_endpoints = [
            self._normalize_api_endpoint(endpoint)
            for endpoint in discovered_endpoints
        ]
        covered_api = set(self.coverage_map.get("api_endpoints", []))
        untested_api = sorted(
            [
                endpoint
                for endpoint in normalized_endpoints
                if endpoint["target"] not in covered_api
            ],
            key=lambda endpoint: endpoint["target"],
        )

        discovered_ui = set(self.application_map.get("discovered_ui_elements", []))
        covered_ui = set(self.coverage_map.get("ui_targets", []))
        untested_ui = sorted(list(discovered_ui - covered_ui))

        return self._build_report(
            untested_ui_elements=untested_ui,
            untested_api_endpoints=untested_api,
        )

    def console_report(self) -> str:
        """Generate a simple, printable report of the coverage gaps."""
        report = self.execute_diff()
        if report["errors"]:
            return "ERROR(S):\n" + "\n".join(report["errors"])

        lines: list[str] = [
            f"Coverage Gap Report for {report['base_url']}{report['page']}",
            "=" * 80,
        ]
        if report["untested_api_endpoints"]:
            lines.append("\nUNTESTED API ENDPOINTS:")
            lines.extend(
                f"  - {endpoint['target']}" if isinstance(endpoint, dict) else f"  - {endpoint}"
                for endpoint in report["untested_api_endpoints"]
            )
        if report["untested_ui_elements"]:
            lines.append("\nUNTESTED UI ELEMENTS:")
            lines.extend(f"  - {element}" for element in report["untested_ui_elements"])

        if not report["untested_api_endpoints"] and not report["untested_ui_elements"]:
            return "No coverage gaps detected."

        return "\n".join(lines)

    @classmethod
    def from_files(cls, coverage_map_path: str, application_map_path: str) -> GapAnalysisEngine:
        """Load the application and coverage maps from JSON files."""
        try:
            application_map = json.loads(Path(application_map_path).read_text(encoding="utf-8"))
        except (IOError, json.JSONDecodeError) as e:
            application_map = {"errors": [f"Failed to load application map: {e}"]}

        try:
            coverage_map = json.loads(Path(coverage_map_path).read_text(encoding="utf-8"))
        except (IOError, json.JSONDecodeError) as e:
            coverage_map = {"errors": [f"Failed to load coverage map: {e}"]}

        return cls(application_map, coverage_map)

    def _build_report(
        self,
        untested_ui_elements: list[str] | None = None,
        untested_api_endpoints: list[object] | None = None,
        errors: list[str] | None = None,
    ) -> dict[str, object]:
        """Build a JSON-serializable gap report."""
        report = GapReport(
            base_url=self.application_map.get("base_url", "N/A"),
            page=self.application_map.get("page", "N/A"),
            untested_ui_elements=untested_ui_elements or [],
            untested_api_endpoints=untested_api_endpoints or [],
            errors=errors or [],
        )
        return report.__dict__

    def _normalize_api_endpoint(self, endpoint: object) -> dict[str, Any]:
        """Return a report-ready API endpoint with a stable scenario target."""
        if isinstance(endpoint, str):
            return {"target": endpoint}
        if not isinstance(endpoint, dict):
            return {"target": str(endpoint)}

        normalized = dict(endpoint)
        method = str(normalized.get("method", "")).upper()
        path = str(normalized.get("path", ""))
        base_target = f"{method} {path}".strip()

        scenario_parts: list[str] = []
        name = str(normalized.get("name", "")).strip()
        if name:
            scenario_parts.append(name)
        response_code = str(normalized.get("response_code", "")).strip()
        if response_code:
            scenario_parts.append(f"status {response_code}")

        if scenario_parts:
            normalized["target"] = f"{base_target} :: {' | '.join(scenario_parts)}"
        else:
            normalized["target"] = base_target
        return normalized

    def write_gap_manifest(self, output_file: str | Path) -> dict[str, object]:
        """Write the gap report to a JSON file."""
        report = self.execute_diff()
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report
