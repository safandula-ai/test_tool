from __future__ import annotations

from .base import SuitePlugin


class SabreSuitePlugin(SuitePlugin):
    """Suite-layout overrides for sabre.com."""

    def render_suite_config_source(
        self,
        normalized_url: str,
        name: str,
    ) -> str:
        """Return the minimal Sabre suite config source."""
        return (
            '"""Website-specific suite configuration."""\n\n'
            "import os\n\n"
            f'BASE_URL = "{normalized_url}"\n'
            f'SUITE_NAME = "{name}"\n'
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
            'PERFORMANCE_MAX_RESPONSE_MS = float(os.getenv("PERFORMANCE_MAX_RESPONSE_MS", "5000"))\n'
            'PERFORMANCE_MAX_TTFB_MS = float(os.getenv("PERFORMANCE_MAX_TTFB_MS", "800"))\n'
            'PERFORMANCE_MAX_LOAD_MS = float(os.getenv("PERFORMANCE_MAX_LOAD_MS", "3000"))\n'
            'PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS = '
            'float(os.getenv("PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS", "10000"))\n'
            'PERFORMANCE_WARMUP_RUNS = int(os.getenv("PERFORMANCE_WARMUP_RUNS", "1"))\n'
            'PERFORMANCE_SAMPLE_COUNT = int(os.getenv("PERFORMANCE_SAMPLE_COUNT", "3"))\n'
            'PERFORMANCE_MOBILE_LATENCY_MS = int(os.getenv("PERFORMANCE_MOBILE_LATENCY_MS", "300"))\n'
            'PERFORMANCE_MOBILE_DOWNLOAD_KBPS = int(os.getenv("PERFORMANCE_MOBILE_DOWNLOAD_KBPS", "400"))\n'
            'PERFORMANCE_MOBILE_UPLOAD_KBPS = int(os.getenv("PERFORMANCE_MOBILE_UPLOAD_KBPS", "150"))\n'
            'PERFORMANCE_MOBILE_CPU_THROTTLE_RATE = int(os.getenv("PERFORMANCE_MOBILE_CPU_THROTTLE_RATE", "4"))\n'
            'PERFORMANCE_MOBILE_PROFILE_NAME = os.getenv("PERFORMANCE_MOBILE_PROFILE_NAME", "slow_3g_like")\n'
        )

    def render_security_test_source(self, suite_name: str) -> str:
        """Return the Sabre-specific security test module."""
        return f'''"""Security verification tests for this website suite."""

from __future__ import annotations

import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.{suite_name}.helpers import dismiss_sabre_consent
from tests.websites.{suite_name}.suite_config import BASE_URL


SEARCH_TRIGGER_SELECTOR = "a.search"
SEARCH_TRIGGER_ACTIVE_SELECTOR = "a.search.is-active"
SEARCH_PANEL_ACTIVE_SELECTOR = ".site-header__main--search-panel.is-active"
SEARCH_INPUT_SELECTOR = (
    "form[action='https://www.sabre.com/'] input[name='s']"
)
SEARCH_SUBMIT_SELECTOR = "form[action='https://www.sabre.com/'] button[type='submit']"


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
    test_diagnostics,
):
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'

    async with page_factory(BASE_URL) as page:
        await page.goto("/", wait_until="domcontentloaded")
        await dismiss_sabre_consent(page)
        await page.locator(SEARCH_TRIGGER_SELECTOR).first.click(force=True)
        await expect(page.locator(SEARCH_TRIGGER_ACTIVE_SELECTOR).first).to_be_visible(timeout=5_000)
        await expect(page.locator(SEARCH_PANEL_ACTIVE_SELECTOR).first).to_be_visible(timeout=5_000)
        search_input = page.locator(SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SEARCH_SUBMIT_SELECTOR).first
        await expect(search_input).to_be_visible(timeout=5_000)
        await expect(search_submit).to_be_visible(timeout=5_000)
        test_diagnostics.record(
            "security_search_surface",
            trigger_selector=SEARCH_TRIGGER_SELECTOR,
            input_selector=SEARCH_INPUT_SELECTOR,
            submit_selector=SEARCH_SUBMIT_SELECTOR,
        )
        await search_input.fill(xss_payload)
        await search_submit.click(force=True)
        await page.wait_for_load_state("domcontentloaded")
        await dismiss_sabre_consent(page)
        script_node = page.locator("script#malicious-xss")
        script_executed = await page.evaluate("() => Boolean(window.__xss_executed)")
        script_node_count = await script_node.count()
        reflected_input_value = await page.locator(SEARCH_INPUT_SELECTOR).first.input_value()
        rendered_markup = await page.locator("body").inner_html()

    test_diagnostics.record(
        "security_xss_probe",
        route="/",
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
    assert reflected_input_value == xss_payload


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
    test_diagnostics,
):
    required_headers = {{
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }}

    async with page_factory(BASE_URL) as page:
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

    def render_helpers_source(self, suite_name: str) -> str:
        """Return the Sabre-specific helper module."""
        return '''"""Sabre-specific website helpers."""

from __future__ import annotations

from playwright.async_api import Page


CONSENT_ROOT_SELECTOR = "#onetrust-consent-sdk"
CONSENT_OVERLAY_SELECTOR = ".onetrust-pc-dark-filter"
CONSENT_ACCEPT_SELECTOR = "#onetrust-accept-btn-handler"
CONSENT_REJECT_SELECTOR = "#onetrust-reject-all-handler"


async def dismiss_sabre_consent(page: Page) -> None:
    """Dismiss and suppress the Sabre OneTrust consent layer."""
    await page.wait_for_timeout(500)

    for selector in (CONSENT_ACCEPT_SELECTOR, CONSENT_REJECT_SELECTOR):
        button = page.locator(selector).first
        if await button.count() > 0:
            try:
                await button.click(force=True, timeout=2_000)
                break
            except Exception:
                pass

    await page.evaluate(
        """([rootSelector, overlaySelector]) => {
            const removeKnownNodes = () => {
                document.querySelectorAll(rootSelector).forEach((node) => node.remove());
                document.querySelectorAll(overlaySelector).forEach((node) => node.remove());
            };
            removeKnownNodes();
            if (!window.__sabreConsentObserverInstalled) {
                const observer = new MutationObserver(() => removeKnownNodes());
                observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true,
                });
                window.__sabreConsentObserverInstalled = true;
            }
        }""",
        [CONSENT_ROOT_SELECTOR, CONSENT_OVERLAY_SELECTOR],
    )
    await page.wait_for_timeout(200)
'''

    def render_performance_test_source(self, suite_name: str) -> str:
        """Return the Sabre-specific performance test module."""
        return f'''"""Performance tests for this website suite."""

import time

import httpx
import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.performance_helpers import (
    measure_time_series,
    metric_medians,
    performance_sample_plan,
    read_navigation_metrics,
)
from tests.websites.{suite_name}.helpers import dismiss_sabre_consent
from tests.websites.{suite_name}.suite_config import (
    BASE_URL,
    PERFORMANCE_MAX_LOAD_MS,
    PERFORMANCE_MAX_RESPONSE_MS,
    PERFORMANCE_MAX_TTFB_MS,
    PERFORMANCE_SAMPLE_COUNT,
    PERFORMANCE_WARMUP_RUNS,
)
from utils.test_diagnostics import httpx_event_hooks


HOME_READY_SELECTOR = "a.search"


async def _open_ready_homepage(page) -> None:
    response = await page.goto("/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    await dismiss_sabre_consent(page)
    await expect(page.locator(HOME_READY_SELECTOR).first).to_be_visible(timeout=5_000)


@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_target_response_time(
    settings,
    test_diagnostics,
):
    maximum_ms = PERFORMANCE_MAX_RESPONSE_MS
    warmup_runs, sample_count = performance_sample_plan(
        warmup_runs=PERFORMANCE_WARMUP_RUNS,
        sample_count=PERFORMANCE_SAMPLE_COUNT,
    )

    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        follow_redirects=True,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as client:
        async def measure_once() -> float:
            started = time.perf_counter()
            response = await client.get(BASE_URL)
            assert response.status_code < 500
            return (time.perf_counter() - started) * 1000

        series = await measure_time_series(
            measure_once,
            warmup_runs=warmup_runs,
            sample_count=sample_count,
        )

    test_diagnostics.record(
        "performance_response_time",
        target_url=BASE_URL,
        warmup_ms=list(series.warmup_ms),
        sample_ms=list(series.sample_ms),
        median_ms=series.median_ms,
    )
    assert series.median_ms <= maximum_ms


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
    test_diagnostics,
):
    max_ttfb_ms = PERFORMANCE_MAX_TTFB_MS
    max_load_ms = PERFORMANCE_MAX_LOAD_MS
    warmup_runs, sample_count = performance_sample_plan(
        warmup_runs=PERFORMANCE_WARMUP_RUNS,
        sample_count=PERFORMANCE_SAMPLE_COUNT,
    )

    async def measure_once() -> dict[str, float]:
        async with page_factory(BASE_URL) as page:
            await _open_ready_homepage(page)
            await page.wait_for_load_state("load")
            return await read_navigation_metrics(page)

    warmup_metrics = [await measure_once() for _ in range(warmup_runs)]
    metric_samples = [await measure_once() for _ in range(sample_count)]
    metrics = metric_medians(metric_samples)
    test_diagnostics.record(
        "performance_metrics",
        route="/",
        warmup=warmup_metrics,
        samples=metric_samples,
        medians=metrics,
    )
    assert metrics["time_to_first_byte_ms"] < max_ttfb_ms
    assert metrics["load_event_complete_ms"] < max_load_ms


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
    test_diagnostics,
):
    test_diagnostics.record(
        "performance_mobile_throttling_skipped",
        route="/",
        reason=(
            "Sabre presents an anti-bot interruption page under throttled mobile "
            "automation, so this measurement is not a valid page-performance signal."
        ),
    )
    pytest.skip(
        "Sabre mobile throttling is disabled because the site serves an anti-bot interruption page."
    )
'''
