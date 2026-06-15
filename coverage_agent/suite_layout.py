"""Filesystem layout for website-specific pytest suites."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


SUITE_DIRECTORIES = ("api", "ui", "smoke", "performance", "security", "generated")


def render_smoke_test_source(suite_name: str) -> str:
    """Render the standard fast-failure smoke checks for a website suite."""
    return f'''"""Critical availability smoke tests for this website suite."""

from urllib.parse import urljoin
from time import perf_counter

import pytest
from playwright.async_api import async_playwright, expect

from coverage_agent.decorators import covers
from tests.websites.helpers import require_live_target, resolve_target_url
from tests.websites.{suite_name}.suite_config import (
    BASE_URL,
    SETTINGS_BASE_URL_ATTR,
    SMOKE_HEALTH_PATH,
    SMOKE_HEALTH_STATUS,
    SMOKE_RENDER_TIMEOUT_MS,
    SMOKE_REQUEST_TIMEOUT_MS,
    SMOKE_ROOT_PATH,
    SMOKE_ROOT_SELECTOR,
)
from utils.smoke_diagnostics import emit_smoke_diagnostics


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
@covers(
    type="api",
    target="website://{suite_name}/backend-gateway-health",
    priority="critical",
    presence="deterministic",
    template="APIContractTemplate",
)
async def test_backend_gateway_health(pytestconfig, settings):
    """Probe the backend without launching a browser rendering context."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    async with async_playwright() as playwright:
        request_context = await playwright.request.new_context(base_url=base_url)
        try:
            started = perf_counter()
            response = await request_context.get(
                SMOKE_HEALTH_PATH,
                timeout=SMOKE_REQUEST_TIMEOUT_MS,
            )
            elapsed_ms = (perf_counter() - started) * 1000
            response_status = response.status
            response_url = response.url
            response_headers = response.headers
        finally:
            await request_context.dispose()
    emit_smoke_diagnostics(
        pytestconfig,
        check="backend-gateway-health",
        method="GET",
        url=response_url,
        status=response_status,
        elapsed_ms=elapsed_ms,
        headers=response_headers,
        details={{"expected_status": SMOKE_HEALTH_STATUS}},
    )
    assert response_status == SMOKE_HEALTH_STATUS, (
        f"Backend gateway probe failed: {{response_status}} "
        f"{{urljoin(base_url + '/', SMOKE_HEALTH_PATH.lstrip('/'))}}"
    )


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.asyncio
@covers(
    type="ui",
    target="website://{suite_name}/homepage-root",
    priority="critical",
    presence="deterministic",
    template="ComponentVisibilityTemplate",
)
async def test_homepage_shell_renders(page_factory, pytestconfig, settings):
    """Fail quickly when navigation or the critical application shell is unavailable."""
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    async with page_factory(base_url) as page:
        started = perf_counter()
        response = await page.goto(
            SMOKE_ROOT_PATH,
            wait_until="domcontentloaded",
            timeout=SMOKE_RENDER_TIMEOUT_MS,
        )
        assert response is not None, "Navigation completed without an HTTP response"
        elapsed_ms = (perf_counter() - started) * 1000
        response_headers = await response.all_headers()
        emit_smoke_diagnostics(
            pytestconfig,
            check="homepage-shell-renders",
            method=response.request.method,
            url=response.url,
            status=response.status,
            elapsed_ms=elapsed_ms,
            headers=response_headers,
            details={{
                "root_path": SMOKE_ROOT_PATH,
                "root_selector": SMOKE_ROOT_SELECTOR,
            }},
        )
        assert response.ok, f"Homepage returned HTTP {{response.status}}"
        await expect(page.locator(SMOKE_ROOT_SELECTOR).first).to_be_visible(timeout=5_000)
'''


def render_performance_test_source(suite_name: str) -> str:
    """Render reusable performance checks for a website suite."""
    return f'''"""Performance tests for this website suite."""

import os
import time
from time import perf_counter

import httpx
import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.helpers import require_live_target, resolve_target_url
from tests.websites.{suite_name}.suite_config import (
    BASE_URL,
    PERF_HOME_PATH,
    PERF_HOME_READY_SELECTOR,
    PERF_MOBILE_PATH,
    PERF_MOBILE_READY_SELECTOR,
    SETTINGS_BASE_URL_ATTR,
)
from utils.test_diagnostics import httpx_event_hooks


@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_target_response_time(
    target_url,
    live_target_enabled,
    settings,
    test_diagnostics,
):
    if not live_target_enabled:
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    maximum_ms = float(os.getenv("PERFORMANCE_MAX_RESPONSE_MS", "5000"))
    started = time.perf_counter()
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        follow_redirects=True,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as client:
        response = await client.get(target_url)
    elapsed_ms = (time.perf_counter() - started) * 1000
    assert response.status_code < 500
    assert elapsed_ms <= maximum_ms, f"Response took {{elapsed_ms:.1f}} ms; limit is {{maximum_ms:.1f}} ms"


@pytest.mark.performance
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="visual",
    target="website://{suite_name}/homepage-loading",
    priority="high",
    template="PerformanceTemplate",
    page="/",
    feature="feature:performance",
)
async def test_homepage_navigation_performance_metrics(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    max_ttfb_ms = float(os.getenv("PERFORMANCE_MAX_TTFB_MS", "800"))
    max_load_ms = float(os.getenv("PERFORMANCE_MAX_LOAD_MS", "3000"))

    async with page_factory(base_url) as page:
        response = await page.goto(PERF_HOME_PATH, wait_until="load")
        assert response is not None and response.ok
        await expect(page.locator(PERF_HOME_READY_SELECTOR).first).to_be_visible(timeout=5000)
        await page.wait_for_load_state("networkidle")
        metrics = await page.evaluate(
            """() => {{
                const nav = performance.getEntriesByType("navigation")[0];
                if (nav) {{
                    return {{
                        time_to_first_byte_ms: nav.responseStart,
                        dom_content_loaded_ms: nav.domContentLoadedEventEnd,
                        load_event_complete_ms: nav.loadEventEnd,
                    }};
                }}
                const timing = performance.timing;
                const navigationStart = timing.navigationStart;
                return {{
                    time_to_first_byte_ms: timing.responseStart - navigationStart,
                    dom_content_loaded_ms: timing.domContentLoadedEventEnd - navigationStart,
                    load_event_complete_ms: timing.loadEventEnd - navigationStart,
                }};
            }}"""
        )
    test_diagnostics.record("performance_metrics", route=PERF_HOME_PATH, **metrics)
    assert metrics["time_to_first_byte_ms"] < max_ttfb_ms, (
        f"SLA violation: TTFB {{metrics['time_to_first_byte_ms']:.1f}} ms exceeds "
        f"{{max_ttfb_ms:.1f}} ms"
    )
    assert metrics["load_event_complete_ms"] < max_load_ms, (
        f"SLA violation: full load {{metrics['load_event_complete_ms']:.1f}} ms exceeds "
        f"{{max_load_ms:.1f}} ms"
    )


@pytest.mark.performance
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="visual",
    target="website://{suite_name}/mobile-throttled-interactive",
    priority="high",
    template="PerformanceTemplate",
    page="/",
    feature="feature:performance",
)
async def test_route_renders_under_mobile_throttling(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    max_interactive_ms = float(os.getenv("PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS", "10000"))

    async with page_factory(base_url) as page:
        client = await page.context.new_cdp_session(page)
        await client.send("Network.enable")
        await client.send(
            "Network.emulateNetworkConditions",
            {{
                "offline": False,
                "latency": 300,
                "downloadThroughput": 400 * 1024 // 8,
                "uploadThroughput": 150 * 1024 // 8,
            }},
        )
        await client.send("Emulation.setCPUThrottlingRate", {{"rate": 4}})
        started = perf_counter()
        response = await page.goto(PERF_MOBILE_PATH, wait_until="domcontentloaded")
        assert response is not None and response.ok
        await expect(page.locator(PERF_MOBILE_READY_SELECTOR).first).to_be_visible(
            timeout=max_interactive_ms
        )
        elapsed_ms = (perf_counter() - started) * 1000
        test_diagnostics.record(
            "performance_mobile_throttling",
            route=PERF_MOBILE_PATH,
            interactive_ms=elapsed_ms,
            cpu_throttle_rate=4,
            network_profile="slow_3g_like",
        )
        assert elapsed_ms <= max_interactive_ms, (
            f"Interactive time {{elapsed_ms:.1f}} ms exceeds {{max_interactive_ms:.1f}} ms"
        )
'''


def render_security_test_source(suite_name: str) -> str:
    """Render reusable security checks for a website suite."""
    return f'''"""Security verification tests for this website suite."""

from __future__ import annotations

import pytest

from coverage_agent.decorators import covers
from tests.websites.helpers import (
    dismiss_consent_if_present,
    require_live_target,
    resolve_target_url,
)
from tests.websites.{suite_name}.suite_config import (
    BASE_URL,
    SECURITY_CONSENT_ACCEPT_SELECTOR,
    SECURITY_CONSENT_OVERLAY_SELECTOR,
    SECURITY_CONSENT_ROOT_SELECTOR,
    SECURITY_SEARCH_INPUT_SELECTOR,
    SECURITY_SEARCH_PATH,
    SECURITY_SEARCH_SUBMIT_SELECTOR,
    SETTINGS_BASE_URL_ATTR,
)


@pytest.mark.security
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="ui",
    target="search-field-injection",
    priority="high",
    template="SecuritySanitizerTemplate",
    page="/",
    feature="feature:security",
)
async def test_search_rejects_reflected_xss_payload(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'

    async with page_factory(base_url) as page:
        await page.goto(SECURITY_SEARCH_PATH, wait_until="domcontentloaded")
        await dismiss_consent_if_present(
            page,
            root_selector=SECURITY_CONSENT_ROOT_SELECTOR,
            accept_selector=SECURITY_CONSENT_ACCEPT_SELECTOR,
            overlay_selector=SECURITY_CONSENT_OVERLAY_SELECTOR,
        )
        await page.wait_for_load_state("networkidle")
        search_input = page.locator(SECURITY_SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SECURITY_SEARCH_SUBMIT_SELECTOR).first
        if await search_input.count() == 0 or await search_submit.count() == 0:
            pytest.skip("Search controls are not available on the target page")
        await search_input.fill(xss_payload)
        await search_submit.click(force=True)
        await page.wait_for_load_state("networkidle")
        script_node = page.locator("script#malicious-xss")
        script_executed = await page.evaluate("() => Boolean(window.__xss_executed)")
        script_node_count = await script_node.count()
        rendered_markup = await page.locator("body").inner_html()
        reflected_input_value = await search_input.input_value()

    test_diagnostics.record(
        "security_xss_probe",
        route=SECURITY_SEARCH_PATH,
        payload=xss_payload,
        script_executed=script_executed,
        script_node_count=script_node_count,
        reflected_input_value=reflected_input_value,
    )
    assert not script_executed, "Executable script injection reached the browser context"
    assert script_node_count == 0, "Injected script tag was inserted into the DOM"
    assert '<script id="malicious-xss">' not in rendered_markup, (
        "Injected script tag was inserted into rendered markup"
    )
    assert reflected_input_value == xss_payload, (
        "Input value was unexpectedly transformed; review whether the target sanitizes or mutates input"
    )


@pytest.mark.security
@pytest.mark.api
@pytest.mark.asyncio
@covers(
    type="api",
    target="security-response-headers",
    priority="medium",
    template="APIContractTemplate",
    page="/",
    feature="feature:security",
)
async def test_http_security_defense_headers(
    page_factory,
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        settings,
        default_base_url=BASE_URL,
        settings_base_url_attr=SETTINGS_BASE_URL_ATTR,
    )
    required_headers = {{
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }}

    async with page_factory(base_url) as page:
        response = await page.goto("/", wait_until="domcontentloaded")
        assert response is not None, "Navigation completed without an HTTP response"
        headers = await response.all_headers()

    missing_headers = [
        f"{{header_name}} ({{description}})"
        for header_name, description in required_headers.items()
        if header_name not in headers
    ]
    test_diagnostics.record(
        "security_headers_audit",
        route="/",
        missing_headers=missing_headers,
        present_headers=sorted(
            header_name for header_name in required_headers if header_name in headers
        ),
    )
    assert not missing_headers, f"Missing defense headers: {{missing_headers}}"
'''


@dataclass(frozen=True)
class WebsiteSuite:
    """Resolved paths for one website test suite."""

    name: str
    base_url: str
    root: Path

    @property
    def generated_test_file(self) -> Path:
        return self.root / "generated" / "test_generated_coverage_gaps.py"


def website_slug(base_url: str) -> str:
    """Convert a URL hostname into a stable Python package name."""
    parsed = urlsplit(base_url if "://" in base_url else f"https://{base_url}")
    hostname = (parsed.hostname or "website").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    slug = re.sub(r"[^a-z0-9]+", "_", hostname).strip("_")
    return slug or "website"


def ensure_website_suite(
    base_url: str,
    tests_root: str | Path = "tests/websites",
) -> WebsiteSuite:
    """Create the standard package and configuration for a website."""
    normalized_url = base_url.rstrip("/")
    name = website_slug(normalized_url)
    root = Path(tests_root) / name
    package_paths = [Path(tests_root), root, *(root / item for item in SUITE_DIRECTORIES)]
    for path in package_paths:
        path.mkdir(parents=True, exist_ok=True)
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")

    config_file = root / "suite_config.py"
    if not config_file.exists():
        config_file.write_text(
            '"""Website-specific suite configuration."""\n\n'
            f"BASE_URL = {json.dumps(normalized_url)}\n"
            "SETTINGS_BASE_URL_ATTR = None\n"
            f"SUITE_NAME = {json.dumps(name)}\n"
            'SMOKE_HEALTH_PATH = "/"\n'
            "SMOKE_HEALTH_STATUS = 200\n"
            'SMOKE_ROOT_PATH = "/"\n'
            'SMOKE_ROOT_SELECTOR = "body"\n'
            "SMOKE_REQUEST_TIMEOUT_MS = 5_000\n"
            "SMOKE_RENDER_TIMEOUT_MS = 8_000\n"
            'PERF_HOME_PATH = "/"\n'
            'PERF_HOME_READY_SELECTOR = "body"\n'
            'PERF_MOBILE_PATH = "/"\n'
            'PERF_MOBILE_READY_SELECTOR = "body"\n'
            'SECURITY_SEARCH_PATH = "/"\n'
            'SECURITY_SEARCH_INPUT_SELECTOR = "input[type=\'search\'], input[name=\'search\'], input[type=\'text\']"\n'
            'SECURITY_SEARCH_SUBMIT_SELECTOR = "button[type=\'submit\'], input[type=\'submit\']"\n'
            'SECURITY_CONSENT_ROOT_SELECTOR = ".fc-consent-root"\n'
            'SECURITY_CONSENT_ACCEPT_SELECTOR = ".fc-cta-consent, button:has-text(\'Consent\'), button:has-text(\'Accept\')"\n'
            'SECURITY_CONSENT_OVERLAY_SELECTOR = ".fc-dialog-overlay"\n',
            encoding="utf-8",
        )

    smoke_file = root / "smoke" / "test_smoke.py"
    smoke_source = smoke_file.read_text(encoding="utf-8") if smoke_file.exists() else ""
    if not smoke_file.exists() or any(
        marker in smoke_source
        for marker in (
            "Generic availability smoke test",
            "Critical availability smoke tests for this website suite.",
        )
    ):
        smoke_file.write_text(render_smoke_test_source(name), encoding="utf-8")

    performance_file = root / "performance" / "test_performance.py"
    if not performance_file.exists():
        performance_file.write_text(render_performance_test_source(name), encoding="utf-8")

    security_file = root / "security" / "test_security.py"
    if not security_file.exists():
        security_file.write_text(render_security_test_source(name), encoding="utf-8")

    return WebsiteSuite(name=name, base_url=normalized_url, root=root)
