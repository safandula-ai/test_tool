"""Performance tests for this website suite."""

import os
import time
from time import perf_counter

import httpx
import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.helpers import require_live_target, resolve_target_url
from tests.websites.reqres_in.suite_config import (
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
    assert elapsed_ms <= maximum_ms, f"Response took {elapsed_ms:.1f} ms; limit is {maximum_ms:.1f} ms"


@pytest.mark.performance
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="visual",
    target="website://reqres_in/homepage-loading",
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
            """() => {
                const nav = performance.getEntriesByType("navigation")[0];
                if (nav) {
                    return {
                        time_to_first_byte_ms: nav.responseStart,
                        dom_content_loaded_ms: nav.domContentLoadedEventEnd,
                        load_event_complete_ms: nav.loadEventEnd,
                    };
                }
                const timing = performance.timing;
                const navigationStart = timing.navigationStart;
                return {
                    time_to_first_byte_ms: timing.responseStart - navigationStart,
                    dom_content_loaded_ms: timing.domContentLoadedEventEnd - navigationStart,
                    load_event_complete_ms: timing.loadEventEnd - navigationStart,
                };
            }"""
        )
    test_diagnostics.record("performance_metrics", route=PERF_HOME_PATH, **metrics)
    assert metrics["time_to_first_byte_ms"] < max_ttfb_ms
    assert metrics["load_event_complete_ms"] < max_load_ms


@pytest.mark.performance
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="visual",
    target="website://reqres_in/mobile-throttled-interactive",
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
            {
                "offline": False,
                "latency": 300,
                "downloadThroughput": 400 * 1024 // 8,
                "uploadThroughput": 150 * 1024 // 8,
            },
        )
        await client.send("Emulation.setCPUThrottlingRate", {"rate": 4})
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
        assert elapsed_ms <= max_interactive_ms
