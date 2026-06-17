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
    untested_ui_elements: list[object] = field(default_factory=list)
    untested_api_endpoints: list[object] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class GapAnalysisEngine:
    """Finds gaps in test coverage by diffing discovery and coverage reports."""

    def __init__(
        self,
        first_map: dict[str, object],
        second_map: dict[str, object],
    ):
        if self._looks_like_application_map(first_map) or not self._looks_like_application_map(second_map):
            self.application_map = first_map
            self.coverage_map = second_map
        else:
            self.application_map = second_map
            self.coverage_map = first_map

    def execute_diff(self) -> dict[str, object]:
        """Compare the application and coverage maps to find untested endpoints."""
        errors: list[str] = []
        if not self.application_map:
            errors.append("Application map is empty or invalid")
        if errors:
            return self._build_report(errors=errors)

        discovered_endpoints = self.application_map.get("discovered_api_endpoints", [])
        normalized_endpoints = [
            self._normalize_api_endpoint(endpoint)
            for endpoint in discovered_endpoints
        ]
        covered_api = self._covered_api_targets()
        untested_api = sorted(
            [
                endpoint
                for endpoint in normalized_endpoints
                if endpoint["target"] not in covered_api
            ],
            key=lambda endpoint: endpoint["target"],
        )

        discovered_ui = set(self.application_map.get("discovered_ui_elements", []))
        ui_presence = self.application_map.get("ui_element_presence", {})
        ui_details = self.application_map.get("ui_element_details", {})
        covered_ui = self._covered_ui_targets()
        untested_ui = sorted(list(discovered_ui - covered_ui))
        normalized_ui = [
            self._normalize_ui_element(
                target,
                presence=str(ui_presence.get(target, "deterministic")),
                observed=ui_details.get(target),
            )
            for target in untested_ui
        ]
        blocking_ui = [
            item for item in normalized_ui
            if str(item.get("presence", "deterministic")) == "deterministic"
        ]
        warnings = [
            self._warning_entry(item)
            for item in normalized_ui
            if str(item.get("presence", "deterministic")) != "deterministic"
        ]
        missing_ui_testids = [
            self._ui_gap_entry(item)
            for item in blocking_ui
        ]
        missing_api_endpoints = [
            self._api_gap_entry(item)
            for item in untested_api
        ]
        discovered_ui_count = len(discovered_ui)
        discovered_api_count = len(normalized_endpoints)
        covered_ui_count = max(discovered_ui_count - len(normalized_ui), 0)
        covered_api_count = max(discovered_api_count - len(untested_api), 0)

        return self._build_report(
            untested_ui_elements=normalized_ui,
            untested_api_endpoints=untested_api,
            warnings=warnings,
            gaps={
                "missing_ui_testids": missing_ui_testids,
                "missing_api_endpoints": missing_api_endpoints,
            },
            metrics={
                "ui_coverage_percent": self._coverage_percent(covered_ui_count, discovered_ui_count),
                "api_coverage_percent": self._coverage_percent(covered_api_count, discovered_api_count),
                "blocking_gap_count": len(blocking_ui) + len(untested_api),
            },
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
            lines.extend(
                f"  - {element['target']}"
                if isinstance(element, dict)
                else f"  - {element}"
                for element in report["untested_ui_elements"]
            )
        if report["warnings"]:
            lines.append("\nWARNINGS:")
            lines.extend(
                f"  - {warning['testid']} ({warning['presence']})"
                for warning in report["warnings"]
            )

        if (
            not report["untested_api_endpoints"]
            and not report["untested_ui_elements"]
            and not report["warnings"]
        ):
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
        warnings: list[dict[str, object]] | None = None,
        gaps: dict[str, list[dict[str, object]]] | None = None,
        metrics: dict[str, float | int] | None = None,
    ) -> dict[str, object]:
        """Build a JSON-serializable gap report."""
        report = GapReport(
            base_url=self.application_map.get("base_url", "N/A"),
            page=self.application_map.get("page", "N/A"),
            untested_ui_elements=untested_ui_elements or [],
            untested_api_endpoints=untested_api_endpoints or [],
            errors=errors or [],
        )
        payload = report.__dict__
        payload["warnings"] = warnings or []
        payload["gaps"] = gaps or {
            "missing_ui_testids": [],
            "missing_api_endpoints": [],
        }
        payload["metrics"] = metrics or {
            "ui_coverage_percent": 0.0,
            "api_coverage_percent": 0.0,
            "blocking_gap_count": 0,
        }
        return payload

    @staticmethod
    def _looks_like_application_map(candidate: dict[str, object]) -> bool:
        """Heuristically distinguish discovery output from coverage output."""
        return any(
            key in candidate
            for key in (
                "page",
                "base_url",
                "discovered_ui_elements",
                "discovered_api_endpoints",
                "ui_element_presence",
                "ui_element_details",
            )
        )

    def _covered_ui_targets(self) -> set[str]:
        """Extract covered UI targets from either legacy or target-indexed coverage maps."""
        if "ui_targets" in self.coverage_map:
            return {str(target) for target in self.coverage_map.get("ui_targets", [])}

        covered: set[str] = set()
        for target, entries in self.coverage_map.items():
            if not isinstance(entries, list):
                continue
            if any(isinstance(entry, dict) and entry.get("type") == "ui" for entry in entries):
                covered.add(str(target))
        return covered

    def _covered_api_targets(self) -> set[str]:
        """Extract covered API targets from either legacy or target-indexed coverage maps."""
        if "api_endpoints" in self.coverage_map:
            return {str(target) for target in self.coverage_map.get("api_endpoints", [])}

        covered: set[str] = set()
        for target, entries in self.coverage_map.items():
            if not isinstance(entries, list):
                continue
            if any(isinstance(entry, dict) and entry.get("type") == "api" for entry in entries):
                covered.add(str(target))
        return covered

    @staticmethod
    def _coverage_percent(covered_count: int, discovered_count: int) -> float:
        """Return a one-decimal percentage or 100% for empty surfaces."""
        if discovered_count == 0:
            return 100.0
        return round((covered_count / discovered_count) * 100, 1)

    def _ui_gap_entry(self, item: dict[str, object]) -> dict[str, object]:
        """Render one blocking UI gap entry with template recommendations."""
        entry: dict[str, object] = {
            "testid": str(item["target"]),
            "presence": str(item.get("presence", "deterministic")),
            "suggested_blueprints": self._recommended_blueprints(str(item["target"]), "ui"),
        }
        if "observed" in item:
            entry["observed"] = item["observed"]
        return entry

    def _api_gap_entry(self, item: dict[str, Any]) -> dict[str, object]:
        """Render one blocking API gap entry with template recommendations."""
        entry = dict(item)
        entry["endpoint"] = str(item["target"])
        entry["suggested_blueprints"] = self._recommended_blueprints(str(item["target"]), "api")
        return entry

    def _warning_entry(self, item: dict[str, object]) -> dict[str, object]:
        """Render one non-blocking warning entry."""
        entry: dict[str, object] = {
            "testid": str(item["target"]),
            "presence": str(item.get("presence", "deterministic")),
        }
        if "observed" in item:
            entry["observed"] = item["observed"]
        return entry

    @staticmethod
    def _recommended_blueprints(target: str, coverage_type: str) -> list[str]:
        """Load template recommendations lazily to avoid circular imports."""
        from coverage_agent.blueprints import recommend_blueprints

        return recommend_blueprints(target, coverage_type)

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

    def _normalize_ui_element(
        self,
        target: str,
        *,
        presence: str,
        observed: object,
    ) -> dict[str, object]:
        """Return a report-ready UI element with snapshot metadata."""
        normalized: dict[str, object] = {
            "target": target,
            "presence": presence,
        }
        if isinstance(observed, dict) and observed:
            normalized["observed"] = observed
        return normalized

    def write_gap_manifest(self, output_file: str | Path) -> dict[str, object]:
        """Write the gap report to a JSON file."""
        report = self.execute_diff()
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report
