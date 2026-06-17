"""Performance tests for this website suite."""

import time
from time import perf_counter

import httpx
import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.performance_helpers import (
    MobileThrottleProfile,
    apply_mobile_throttle,
    measure_time_series,
    metric_medians,
    performance_sample_plan,
    read_navigation_metrics,
)
from tests.websites.sabre_com.suite_config import (
    BASE_URL,
    PERF_HOME_PATH,
    PERF_HOME_READY_SELECTOR,
    PERF_MOBILE_PATH,
    PERF_MOBILE_READY_SELECTOR,
    PERFORMANCE_MAX_RESPONSE_MS,
    PERFORMANCE_MAX_LOAD_MS,
    PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS,
    PERFORMANCE_MAX_TTFB_MS,
    PERFORMANCE_MOBILE_CPU_THROTTLE_RATE,
    PERFORMANCE_MOBILE_DOWNLOAD_KBPS,
    PERFORMANCE_MOBILE_LATENCY_MS,
    PERFORMANCE_MOBILE_PROFILE_NAME,
    PERFORMANCE_MOBILE_UPLOAD_KBPS,
    PERFORMANCE_SAMPLE_COUNT,
    PERFORMANCE_WARMUP_RUNS,
)
from utils.test_diagnostics import httpx_event_hooks


@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_target_response_time(
    settings,
    test_diagnostics,
):
    target_url = BASE_URL
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
            response = await client.get(target_url)
            assert response.status_code < 500
            return (time.perf_counter() - started) * 1000

        series = await measure_time_series(
            measure_once,
            warmup_runs=warmup_runs,
            sample_count=sample_count,
        )

    test_diagnostics.record(
        "performance_response_time",
        target_url=target_url,
        warmup_ms=list(series.warmup_ms),
        sample_ms=list(series.sample_ms),
        median_ms=series.median_ms,
    )
    assert series.median_ms <= maximum_ms, (
        f"Median response time {series.median_ms:.1f} ms exceeds "
        f"{maximum_ms:.1f} ms across {sample_count} sample(s)"
    )


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
    base_url = BASE_URL
    max_ttfb_ms = PERFORMANCE_MAX_TTFB_MS
    max_load_ms = PERFORMANCE_MAX_LOAD_MS
    warmup_runs, sample_count = performance_sample_plan(
        warmup_runs=PERFORMANCE_WARMUP_RUNS,
        sample_count=PERFORMANCE_SAMPLE_COUNT,
    )

    async def measure_once() -> dict[str, float]:
        async with page_factory(base_url) as page:
            response = await page.goto(PERF_HOME_PATH, wait_until="load")
            assert response is not None and response.ok
            await expect(page.locator(PERF_HOME_READY_SELECTOR).first).to_be_visible(timeout=5000)
            await page.wait_for_load_state("networkidle")
            return await read_navigation_metrics(page)

    warmup_metrics = [await measure_once() for _ in range(warmup_runs)]
    metric_samples = [await measure_once() for _ in range(sample_count)]
    metrics = metric_medians(metric_samples)
    test_diagnostics.record(
        "performance_metrics",
        route=PERF_HOME_PATH,
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
    page_factory,
    test_diagnostics,
):
    base_url = BASE_URL
    max_interactive_ms = PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS
    warmup_runs, sample_count = performance_sample_plan(
        warmup_runs=PERFORMANCE_WARMUP_RUNS,
        sample_count=PERFORMANCE_SAMPLE_COUNT,
    )
    mobile_profile = MobileThrottleProfile(
        latency_ms=PERFORMANCE_MOBILE_LATENCY_MS,
        download_kbps=PERFORMANCE_MOBILE_DOWNLOAD_KBPS,
        upload_kbps=PERFORMANCE_MOBILE_UPLOAD_KBPS,
        cpu_throttle_rate=PERFORMANCE_MOBILE_CPU_THROTTLE_RATE,
        profile_name=PERFORMANCE_MOBILE_PROFILE_NAME,
    )

    async def measure_once() -> float:
        async with page_factory(base_url) as page:
            await apply_mobile_throttle(page, mobile_profile)
            started = perf_counter()
            response = await page.goto(PERF_MOBILE_PATH, wait_until="domcontentloaded")
            assert response is not None and response.ok
            await expect(page.locator(PERF_MOBILE_READY_SELECTOR).first).to_be_visible(
                timeout=max_interactive_ms
            )
            return (perf_counter() - started) * 1000

    series = await measure_time_series(
        measure_once,
        warmup_runs=warmup_runs,
        sample_count=sample_count,
    )
    test_diagnostics.record(
        "performance_mobile_throttling",
        route=PERF_MOBILE_PATH,
        warmup_ms=list(series.warmup_ms),
        sample_ms=list(series.sample_ms),
        median_ms=series.median_ms,
        cpu_throttle_rate=mobile_profile.cpu_throttle_rate,
        network_profile=mobile_profile.profile_name,
    )
    assert series.median_ms <= max_interactive_ms, (
        f"Median interactive time {series.median_ms:.1f} ms exceeds "
        f"{max_interactive_ms:.1f} ms across {sample_count} sample(s)"
    )
