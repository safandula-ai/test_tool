from __future__ import annotations

import json

import pytest

from coverage_agent.analyzer import CoverageValidationError, generate_coverage_map
from coverage_agent.decorators import covers
from coverage_agent.discovery import PlaywrightDiscoveryEngine
from coverage_agent.gap_analysis import GapAnalysisEngine


def test_covers_attaches_validated_metadata():
    @covers(type="ui", target="login-submit", priority="high")
    def example():
        pass

    assert example.__coverage__[0]["target"] == "login-submit"
    with pytest.raises(ValueError, match="cannot be empty"):
        covers(type="api", target="")


def test_analyzer_extracts_sync_async_and_stacked_decorators(tmp_path):
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        """
from coverage_agent.decorators import covers

@covers(type="ui", target="submit", priority="high")
@covers(type="visual", target="form")
async def test_form():
    pass
""",
        encoding="utf-8",
    )

    output = tmp_path / "coverage.json"
    result = generate_coverage_map(tmp_path, output)

    assert set(result) == {"submit", "form"}
    assert result["form"][0]["priority"] == "medium"
    assert json.loads(output.read_text(encoding="utf-8")) == result


def test_analyzer_ignores_nested_decorated_helpers(tmp_path):
    (tmp_path / "test_nested.py").write_text(
        """
def test_outer():
    @covers(type="ui", target="not-a-pytest-test")
    def helper():
        pass
""",
        encoding="utf-8",
    )

    assert generate_coverage_map(tmp_path) == {}


def test_analyzer_rejects_missing_required_fields(tmp_path):
    (tmp_path / "test_invalid.py").write_text(
        "@covers(type='ui')\ndef test_invalid(): pass\n",
        encoding="utf-8",
    )
    with pytest.raises(CoverageValidationError, match="target"):
        generate_coverage_map(tmp_path)


def test_discovery_normalizes_and_filters_api_requests():
    engine = PlaywrightDiscoveryEngine("https://example.test")

    assert engine.endpoint_signature("post", "https://example.test/api/orders?draft=1") == (
        "POST /api/orders"
    )
    assert engine.endpoint_signature("GET", "https://other.test/api/orders") is None
    assert engine.endpoint_signature("GET", "https://example.test/api/analytics/events") is None


def test_gap_analysis_reports_missing_targets_and_blueprints():
    engine = GapAnalysisEngine(
        {"submit-button": [{"type": "ui"}], "GET /api/users": [{"type": "api"}]},
        {
            "page": "/users",
            "discovered_ui_elements": ["submit-button", "email-input"],
            "discovered_api_endpoints": ["GET /api/users", "POST /api/users"],
        },
    )

    report = engine.execute_diff()

    assert report["metrics"]["ui_coverage_percent"] == 50.0
    assert report["gaps"]["missing_ui_testids"] == [
        {"testid": "email-input", "suggested_blueprint": "FormValidationTemplate"}
    ]
    assert report["gaps"]["missing_api_endpoints"][0]["endpoint"] == "POST /api/users"
