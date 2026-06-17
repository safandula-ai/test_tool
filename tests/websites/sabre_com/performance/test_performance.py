"""Performance tests for this website suite."""

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
from tests.websites.sabre_com.helpers import dismiss_sabre_consent
from tests.websites.sabre_com.suite_config import (
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
    target="website://sabre_com/homepage-loading",
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
    target="website://sabre_com/mobile-throttled-interactive",
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
