from __future__ import annotations

import asyncio
import json
import sys

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from coverage_agent.analyzer import CoverageValidationError, build_coverage_indexes, generate_coverage_map
from coverage_agent.blueprints import recommend_blueprints
from coverage_agent.decorators import covers
from coverage_agent.discovery import PlaywrightDiscoveryEngine
from coverage_agent.gap_analysis import GapAnalysisEngine
from coverage_agent.gap_scaffolder import scaffold_gap_tests
from coverage_agent.manifests import load_manifests
from coverage_agent.suite_layout import ensure_website_suite, website_slug
from coverage_agent.template_engine import DynamicSuiteAssembler
from coverage_agent.__main__ import main
from coverage_agent.plugins.automationexercise import AutomationExerciseScraper


@covers(type="api", target="coverage-agent://decorators", priority="high", template="APIContractTemplate")
def test_covers_attaches_validated_metadata():
    @covers(
        type="ui",
        target="login-submit",
        priority="high",
        presence="ephemeral",
    )
    def example():
        pass

    assert example.__coverage__[0]["target"] == "login-submit"
    assert example.__coverage__[0]["presence"] == "ephemeral"
    with pytest.raises(ValueError, match="cannot be empty"):
        covers(type="api", target="")
    with pytest.raises(ValueError, match="presence"):
        covers(type="ui", target="toast", presence="sometimes")


@covers(type="api", target="coverage-agent://analyzer/extraction", priority="high", template="APIContractTemplate")
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
    assert result["form"][0]["presence"] == "deterministic"
    assert json.loads(output.read_text(encoding="utf-8")) == result


@covers(type="api", target="coverage-agent://analyzer/nested-functions", priority="medium", template="APIContractTemplate")
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


@covers(type="api", target="coverage-agent://analyzer/validation", priority="high", template="APIContractTemplate")
def test_analyzer_rejects_missing_required_fields(tmp_path):
    (tmp_path / "test_invalid.py").write_text(
        "@covers(type='ui')\ndef test_invalid(): pass\n",
        encoding="utf-8",
    )
    with pytest.raises(CoverageValidationError, match="target"):
        generate_coverage_map(tmp_path)


@covers(type="api", target="coverage-agent://discovery/network", priority="high", template="APIContractTemplate")
def test_discovery_normalizes_and_filters_api_requests():
    engine = PlaywrightDiscoveryEngine("https://example.test")

    assert engine.endpoint_signature("post", "https://example.test/api/orders?draft=1") == (
        "POST /api/orders"
    )
    assert engine.endpoint_signature("GET", "https://other.test/api/orders") is None
    assert engine.endpoint_signature("GET", "https://example.test/api/analytics/events") is None


@covers(type="api", target="coverage-agent://suite-layout", priority="high", template="APIContractTemplate")
def test_website_suite_layout_creates_config_smoke_performance_and_generated_paths(tmp_path):
    suite = ensure_website_suite(
        "https://www.example-shop.test/catalog",
        tmp_path / "websites",
    )

    assert website_slug("https://www.example-shop.test") == "example_shop_test"
    assert suite.root.name == "example_shop_test"
    assert 'BASE_URL = "https://www.example-shop.test/catalog"' in (
        suite.root / "suite_config.py"
    ).read_text(encoding="utf-8")
    assert (suite.root / "smoke" / "test_smoke.py").exists()
    assert (suite.root / "performance" / "test_performance.py").exists()
    assert (suite.root / "security" / "test_security.py").exists()
    assert suite.generated_test_file.parent.exists()
    smoke_source = (suite.root / "smoke" / "test_smoke.py").read_text(
        encoding="utf-8"
    )
    performance_source = (suite.root / "performance" / "test_performance.py").read_text(
        encoding="utf-8"
    )
    security_source = (suite.root / "security" / "test_security.py").read_text(
        encoding="utf-8"
    )
    assert "playwright.request.new_context" in smoke_source
    assert "test_backend_gateway_health" in smoke_source
    assert "test_homepage_shell_renders" in smoke_source
    assert 'timeout=SMOKE_REQUEST_TIMEOUT_MS' in smoke_source
    assert 'timeout=SMOKE_RENDER_TIMEOUT_MS' in smoke_source
    assert 'timeout=5_000' in smoke_source
    assert 'target="website://example_shop_test/backend-gateway-health"' in smoke_source
    assert "emit_smoke_diagnostics" in smoke_source
    assert "response_headers = response.headers" in smoke_source
    assert "response_headers = await response.all_headers()" in smoke_source
    assert "test_homepage_navigation_performance_metrics" in performance_source
    assert "test_route_renders_under_mobile_throttling" in performance_source
    assert "Network.emulateNetworkConditions" in performance_source
    assert 'target="website://example_shop_test/homepage-loading"' in performance_source
    assert "test_http_security_defense_headers" in security_source
    assert "test_search_rejects_reflected_xss_payload" in security_source
    assert "Missing defense headers" in security_source


@covers(type="api", target="coverage-agent://discovery/security-challenges", priority="high", template="APIContractTemplate")
def test_security_challenge_detection_records_clearance_and_timeout():
    class Locator:
        def __init__(self, count):
            self._count = count

        async def count(self):
            return self._count

    class Page:
        def __init__(self, *, detected, times_out=False):
            self.detected = detected
            self.times_out = times_out
            self.waited_for = None
            self.delays = []

        def locator(self, selector):
            return Locator(1 if self.detected and selector == "#challenge-running" else 0)

        async def wait_for_selector(self, selector, *, state, timeout):
            self.waited_for = (selector, state, timeout)
            if self.times_out:
                raise PlaywrightTimeoutError("challenge remained attached")

        async def wait_for_timeout(self, delay):
            self.delays.append(delay)

    clear_engine = PlaywrightDiscoveryEngine("https://example.test")
    clear_page = Page(detected=True)
    assert asyncio.run(
        clear_engine.handle_security_challenges(clear_page, timeout_ms=500)
    )
    assert clear_engine.security_challenge_status == "cleared"
    assert clear_page.waited_for == ("#challenge-running", "detached", 500)
    assert clear_page.delays == [1_000]

    blocked_engine = PlaywrightDiscoveryEngine("https://example.test")
    assert not asyncio.run(
        blocked_engine.handle_security_challenges(
            Page(detected=True, times_out=True),
            timeout_ms=500,
        )
    )
    assert blocked_engine.security_challenge_status == "unresolved"
    assert blocked_engine.application_manifest("/")["scan_status"] == (
        "blocked_by_security_challenge"
    )

    clean_engine = PlaywrightDiscoveryEngine("https://example.test")
    assert asyncio.run(clean_engine.handle_security_challenges(Page(detected=False)))
    assert clean_engine.security_challenge_status == "not_detected"


@covers(type="api", target="coverage-agent://discovery/progressive-scan", priority="high", template="APIContractTemplate")
def test_progressive_scan_classifies_targets_missing_from_final_dom_as_ephemeral():
    class Element:
        def __init__(self, value):
            self.value = value

        async def get_attribute(self, attribute):
            return self.value

    class Page:
        phase = 0

        async def evaluate(self, script):
            if script == "document.body.scrollHeight":
                return 700
            return None

        async def wait_for_timeout(self, delay):
            if delay == 600:
                self.phase += 1
            await asyncio.sleep(0)

        async def query_selector_all(self, selector):
            if selector != "[data-testid]":
                return []
            values = ["persistent"]
            if self.phase == 1:
                values.append("temporary-toast")
            return [Element(value) for value in values]

    engine = PlaywrightDiscoveryEngine("https://example.test")
    asyncio.run(engine.execute_progressive_multi_pass_scan(Page()))

    assert engine.discovered_ui_elements == {"persistent", "temporary-toast"}
    assert engine.ui_element_presence == {
        "persistent": "deterministic",
        "temporary-toast": "ephemeral",
    }


@covers(type="api", target="coverage-agent://gap-analysis", priority="high", template="APIContractTemplate")
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
    assert report["gaps"]["missing_ui_testids"][0]["testid"] == "email-input"
    assert report["gaps"]["missing_ui_testids"][0]["suggested_blueprints"] == [
        "InputValidationTemplate",
        "FormValidationTemplate",
    ]
    assert report["gaps"]["missing_api_endpoints"][0]["endpoint"] == "POST /api/users"
    assert report["metrics"]["blocking_gap_count"] == 2


@covers(type="api", target="coverage-agent://gap-analysis/stability", priority="high", template="APIContractTemplate")
def test_gap_analysis_warns_for_ephemeral_targets_without_blocking_ci(tmp_path, monkeypatch):
    coverage_path = tmp_path / "coverage.json"
    application_path = tmp_path / "application.json"
    report_path = tmp_path / "report.json"
    coverage_path.write_text("{}", encoding="utf-8")
    application_path.write_text(
        json.dumps(
            {
                "page": "/dynamic",
                "discovered_ui_elements": ["temporary-toast"],
                "ui_element_presence": {"temporary-toast": "ephemeral"},
                "discovered_api_endpoints": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "coverage_agent",
            "gaps",
            "--coverage",
            str(coverage_path),
            "--application",
            str(application_path),
            "--output",
            str(report_path),
        ],
    )

    assert main() == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["errors"] == []
    assert report["warnings"][0]["testid"] == "temporary-toast"


@covers(type="api", target="coverage-agent://gap-analysis/ci-exit", priority="high", template="APIContractTemplate")
def test_gap_analysis_returns_nonzero_for_deterministic_gaps(tmp_path, monkeypatch):
    coverage_path = tmp_path / "coverage.json"
    application_path = tmp_path / "application.json"
    coverage_path.write_text("{}", encoding="utf-8")
    application_path.write_text(
        json.dumps(
            {
                "page": "/login",
                "discovered_ui_elements": ["login-submit"],
                "discovered_api_endpoints": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "coverage_agent",
            "gaps",
            "--coverage",
            str(coverage_path),
            "--application",
            str(application_path),
            "--output",
            str(tmp_path / "report.json"),
        ],
    )

    assert main() == 1


@covers(type="api", target="coverage-agent://templates/recommendations", priority="high", template="APIContractTemplate")
def test_template_matching_recommends_complementary_patterns():
    assert recommend_blueprints("subscription-form", "ui") == [
        "FormValidationTemplate",
        "SubmissionTemplate",
    ]
    assert recommend_blueprints("discount-code", "ui") == [
        "InputValidationTemplate",
        "AppliedCouponAPITemplate",
    ]


@covers(type="api", target="coverage-agent://templates/assembly", priority="high", template="APIContractTemplate")
def test_dynamic_suite_assembly_uses_manifest_and_suggests_unbound_targets():
    manifests = load_manifests("config/test_manifests.json")
    suite = DynamicSuiteAssembler().assemble(
        {
            "page": "/login",
            "discovered_ui_elements": ["subscription-form", "new-button"],
            "discovered_api_endpoints": [],
        },
        manifests,
    )

    assert [item["template"] for item in suite["suite"]] == [
        "FormValidationTemplate",
        "SubmissionTemplate",
    ]
    assert suite["suggestions"] == [
        {
            "target": "new-button",
            "type": "ui",
            "recommended_templates": ["InteractionTemplate"],
        }
    ]


@covers(type="api", target="coverage-agent://templates/selection", priority="high", template="APIContractTemplate")
def test_template_page_and_feature_indexes_select_impacted_tests():
    coverage = {
        "login-submit": [
            {
                "type": "ui",
                "template": "InteractionTemplate",
                "page": "/login",
                "feature": "feature:authentication",
                "file_path": "tests/ui/test_login_flow.py",
                "test_function": "test_login_page_smoke",
            }
        ]
    }

    assert DynamicSuiteAssembler.select_tests(
        coverage, template="InteractionTemplate", feature="feature:authentication"
    ) == ["tests/ui/test_login_flow.py::test_login_page_smoke"]
    assert build_coverage_indexes(coverage)["pages"]["/login"][0]["target"] == "login-submit"


@covers(type="api", target="coverage-agent://gap-scaffolder", priority="high", template="APIContractTemplate")
def test_gap_scaffolder_generates_executable_ui_tests(tmp_path):
    report = tmp_path / "gap_report.json"
    report.write_text(
        json.dumps(
            {
                "page": "/login",
                "base_url": "https://automationexercise.com",
                "untested_ui_elements": ["login-email"],
                "untested_api_endpoints": [],
                "errors": [],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "test_generated.py"

    count = scaffold_gap_tests(
        report,
        output,
        base_url_setting="automation_exercise_base_url",
    )
    source = output.read_text(encoding="utf-8")
    helper = tmp_path / "_test_generated_helpers.py"
    helper_source = helper.read_text(encoding="utf-8")

    assert count == 1
    assert 'target="login-email"' in source
    assert 'template="ComponentVisibilityTemplate"' in source
    assert "DEFAULT_BASE_URL = 'https://automationexercise.com'" in source
    assert 'pytestconfig.getoption("--target-url")' in source
    assert "from ._test_generated_helpers import (" in source
    assert "target = target_locator(browser_page, " in source
    assert "def _target(" not in source
    assert "def target_locator(" in helper_source
    assert "async def assert_visible(target) -> None:" in helper_source
    compile(source, str(output), "exec")
    compile(helper_source, str(helper), "exec")


@covers(type="api", target="coverage-agent://gap-scaffolder/api", priority="high", template="APIContractTemplate")
def test_gap_scaffolder_generates_api_tests_from_gap_report(tmp_path):
    report = tmp_path / "gap_report.json"
    report.write_text(
        json.dumps(
            {
                "page": "/checkout",
                "untested_ui_elements": [],
                "untested_api_endpoints": ["POST /api/checkout"],
                "errors": [],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "test_generated.py"

    scaffold_gap_tests(report, output)
    source = output.read_text(encoding="utf-8")

    assert "async def test_generated_api_post_api_checkout" in source
    assert 'response = await api_client.request("POST", url)' in source
    assert "from ._test_generated_helpers import (" not in source


@covers(type="api", target="coverage-agent://gap-scaffolder/automationexercise", priority="high", template="APIContractTemplate")
def test_gap_scaffolder_generates_automationexercise_payload_and_assertions(tmp_path):
    report = tmp_path / "gap_report.json"
    report.write_text(
        json.dumps(
            {
                "page": "/api_list",
                "base_url": "https://automationexercise.com",
                "untested_ui_elements": [],
                "untested_api_endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/verifyLogin",
                        "name": "POST To Verify Login with valid details",
                        "request_parameters": "email, password",
                        "response_code": "200",
                        "response_payload": "User exists!",
                        "target": "POST /api/verifyLogin :: POST To Verify Login with valid details | status 200",
                    }
                ],
                "errors": [],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "test_generated.py"

    scaffold_gap_tests(report, output)
    source = output.read_text(encoding="utf-8")
    helper = tmp_path / "_test_generated_helpers.py"
    helper_source = helper.read_text(encoding="utf-8")

    assert "from utils.test_diagnostics import httpx_event_hooks" in source
    assert "from ._test_generated_helpers import (" in source
    assert "request_kwargs, cleanup_payload = await automationexercise_request_kwargs(" in source
    assert "request_parameters='email, password'" in source
    assert 'assert response.status_code == 200' in source
    assert 'assert response_payload["responseCode"] == int(\'200\')' in source
    assert 'assert response_payload["message"] == \'User exists!\'' in source
    assert "from api_clients.automation_exercise_client import build_account_payload" in helper_source
    assert "async def automationexercise_request_kwargs(" in helper_source
    assert "async def cleanup_generated_account(" in helper_source
    assert "def _generated_account_payload" not in source
    compile(source, str(output), "exec")
    compile(helper_source, str(helper), "exec")


@covers(type="api", target="coverage-agent://automationexercise-scraper", priority="high", template="APIContractTemplate")
def test_automationexercise_scraper_captures_request_parameters_and_titles():
    class Page:
        async def evaluate(self, script):
            return [
                "\n".join(
                    [
                        "API 7: POST To Verify Login with valid details",
                        "API URL: https://automationexercise.com/api/verifyLogin",
                        "Request Method: POST",
                        "Request Parameters: email, password",
                        "Response Code: 200",
                        "Response Message: User exists!",
                    ]
                )
            ]

    endpoints = asyncio.run(AutomationExerciseScraper().scrape(Page()))

    assert endpoints == [
        {
            "method": "POST",
            "name": "POST To Verify Login with valid details",
            "path": "/api/verifyLogin",
            "request_parameters": "email, password",
            "response_code": "200",
            "response_payload": "User exists!",
            "response_payload_kind": "message",
        }
    ]


@covers(type="api", target="coverage-agent://automationexercise-scraper/json-payload", priority="high", template="APIContractTemplate")
def test_automationexercise_scraper_marks_response_json_payloads():
    class Page:
        async def evaluate(self, script):
            return [
                "\n".join(
                    [
                        "API 99: GET Example JSON Payload",
                        "API URL: https://automationexercise.com/api/example",
                        "Request Method: GET",
                        'Response JSON: {"status":"ok"}',
                    ]
                )
            ]

    endpoints = asyncio.run(AutomationExerciseScraper().scrape(Page()))

    assert endpoints == [
        {
            "method": "GET",
            "name": "GET Example JSON Payload",
            "path": "/api/example",
            "response_payload": '{"status":"ok"}',
            "response_payload_kind": "json",
        }
    ]


@covers(type="api", target="coverage-agent://gap-scaffolder/response-json", priority="high", template="APIContractTemplate")
def test_gap_scaffolder_generates_json_response_assertion(tmp_path):
    report = tmp_path / "gap_report.json"
    report.write_text(
        json.dumps(
            {
                "page": "/api_list",
                "base_url": "https://example.test",
                "untested_ui_elements": [],
                "untested_api_endpoints": [
                    {
                        "method": "GET",
                        "path": "/api/example",
                        "name": "GET Example JSON Payload",
                        "response_payload": '{"status":"ok"}',
                        "response_payload_kind": "json",
                        "target": "GET /api/example :: GET Example JSON Payload",
                    }
                ],
                "errors": [],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "test_generated.py"

    scaffold_gap_tests(report, output)
    source = output.read_text(encoding="utf-8")

    assert 'if \'json\' == "json":' in source
    assert "assert isinstance(payload, (dict, list))" in source
    compile(source, str(output), "exec")


@covers(type="api", target="coverage-agent://gap-analysis/api-scenarios", priority="high", template="APIContractTemplate")
def test_gap_analysis_preserves_distinct_api_scenarios():
    engine = GapAnalysisEngine(
        {
            "base_url": "https://automationexercise.com",
            "page": "/api_list",
            "discovered_ui_elements": [],
            "discovered_api_endpoints": [
                {
                    "method": "POST",
                    "path": "/api/verifyLogin",
                    "name": "POST To Verify Login with valid details",
                    "request_parameters": "email, password",
                    "response_code": "200",
                    "response_payload": "User exists!",
                },
                {
                    "method": "POST",
                    "path": "/api/verifyLogin",
                    "name": "POST To Verify Login without email parameter",
                    "request_parameters": "password",
                    "response_code": "400",
                    "response_payload": "Bad request, email or password parameter is missing in POST request.",
                },
            ],
        },
        {"api_endpoints": []},
    )

    report = engine.execute_diff()

    assert report["untested_api_endpoints"] == [
        {
            "method": "POST",
            "name": "POST To Verify Login with valid details",
            "path": "/api/verifyLogin",
            "request_parameters": "email, password",
            "response_code": "200",
            "response_payload": "User exists!",
            "target": "POST /api/verifyLogin :: POST To Verify Login with valid details | status 200",
        },
        {
            "method": "POST",
            "name": "POST To Verify Login without email parameter",
            "path": "/api/verifyLogin",
            "request_parameters": "password",
            "response_code": "400",
            "response_payload": "Bad request, email or password parameter is missing in POST request.",
            "target": "POST /api/verifyLogin :: POST To Verify Login without email parameter | status 400",
        },
    ]
