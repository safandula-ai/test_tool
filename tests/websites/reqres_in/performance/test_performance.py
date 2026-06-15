"""Generic response-time check for this website suite."""

import os
import time

import httpx
import pytest

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
