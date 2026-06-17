"""Shared measurement helpers for website performance guardrail tests."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Awaitable, Callable


@dataclass(frozen=True)
class PerformanceSeries:
    """One timed series with optional warmups and measured samples."""

    warmup_ms: tuple[float, ...]
    sample_ms: tuple[float, ...]

    @property
    def median_ms(self) -> float:
        """Return the median of the measured samples."""
        return float(median(self.sample_ms))


@dataclass(frozen=True)
class MobileThrottleProfile:
    """Named browser throttling profile used by mobile performance checks."""

    latency_ms: int
    download_kbps: int
    upload_kbps: int
    cpu_throttle_rate: int
    profile_name: str = "slow_3g_like"


def performance_sample_plan(*, warmup_runs: int, sample_count: int) -> tuple[int, int]:
    """Normalize configured warmup and sample counts for performance tests."""
    warmup_runs = max(0, int(warmup_runs))
    sample_count = max(1, int(sample_count))
    return warmup_runs, sample_count


async def measure_time_series(
    measure_once: Callable[[], Awaitable[float]],
    *,
    warmup_runs: int,
    sample_count: int,
) -> PerformanceSeries:
    """Measure one async timing function with warmups and median samples."""
    warmup_ms = [await measure_once() for _ in range(warmup_runs)]
    sample_ms = [await measure_once() for _ in range(sample_count)]
    return PerformanceSeries(
        warmup_ms=tuple(warmup_ms),
        sample_ms=tuple(sample_ms),
    )


def metric_medians(metric_samples: list[dict[str, float]]) -> dict[str, float]:
    """Collapse repeated metric dictionaries into one median-per-key dict."""
    if not metric_samples:
        return {}
    return {
        key: float(median([sample[key] for sample in metric_samples]))
        for key in metric_samples[0]
    }


async def read_navigation_metrics(page) -> dict[str, float]:
    """Read normalized browser navigation timing metrics from the active page."""
    return await page.evaluate(
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


async def apply_mobile_throttle(page, profile: MobileThrottleProfile) -> None:
    """Apply a repeatable synthetic mobile network and CPU profile to one page."""
    client = await page.context.new_cdp_session(page)
    await client.send("Network.enable")
    await client.send(
        "Network.emulateNetworkConditions",
        {
            "offline": False,
            "latency": profile.latency_ms,
            "downloadThroughput": profile.download_kbps * 1024 // 8,
            "uploadThroughput": profile.upload_kbps * 1024 // 8,
        },
    )
    await client.send(
        "Emulation.setCPUThrottlingRate",
        {"rate": profile.cpu_throttle_rate},
    )
