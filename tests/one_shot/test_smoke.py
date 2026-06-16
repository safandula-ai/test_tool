"""Reusable one-shot smoke tests for a live website target.

Copy this file into a dedicated website suite and replace the selectors/paths below.
By default the target comes from `BASE_URL`; pass `--target-url` to override it.
"""

from __future__ import annotations

import os
from time import perf_counter
from urllib.parse import urljoin

import pytest
from playwright.async_api import async_playwright, expect

from coverage_agent.decorators import covers
from utils.smoke_diagnostics import emit_smoke_diagnostics


DEFAULT_BASE_URL = os.getenv("BASE_URL") or None
SMOKE_HEALTH_PATH = os.getenv("ONE_SHOT_SMOKE_HEALTH_PATH", "/")
SMOKE_HEALTH_STATUS = int(os.getenv("ONE_SHOT_SMOKE_HEALTH_STATUS", "200"))
SMOKE_ROOT_PATH = os.getenv("ONE_SHOT_SMOKE_ROOT_PATH", "/")
SMOKE_ROOT_SELECTOR = os.getenv("ONE_SHOT_SMOKE_ROOT_SELECTOR", "body")
SMOKE_REQUEST_TIMEOUT_MS = int(os.getenv("ONE_SHOT_SMOKE_REQUEST_TIMEOUT_MS", "5000"))
SMOKE_RENDER_TIMEOUT_MS = int(os.getenv("ONE_SHOT_SMOKE_RENDER_TIMEOUT_MS", "8000"))


def _target_url(pytestconfig):
    target_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    return target_url.rstrip("/")


def _require_live_target(pytestconfig):
    if not (pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL):
        pytest.skip("Set BASE_URL or pass --target-url")


@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
@covers(
    type="api",
    target="website://one_shot/backend-gateway-health",
    priority="critical",
    presence="deterministic",
    template="APIContractTemplate",
)
async def test_backend_gateway_health(pytestconfig):
    _require_live_target(pytestconfig)
    base_url = _target_url(pytestconfig)
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
        details={"expected_status": SMOKE_HEALTH_STATUS},
    )
    assert response_status == SMOKE_HEALTH_STATUS, (
        f"Backend gateway probe failed: {response_status} "
        f"{urljoin(base_url + '/', SMOKE_HEALTH_PATH.lstrip('/'))}"
    )


@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.asyncio
@covers(
    type="ui",
    target="website://one_shot/homepage-root",
    priority="critical",
    presence="deterministic",
    template="ComponentVisibilityTemplate",
)
async def test_homepage_shell_renders(page_factory, pytestconfig):
    _require_live_target(pytestconfig)
    base_url = _target_url(pytestconfig)
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
            details={
                "root_path": SMOKE_ROOT_PATH,
                "root_selector": SMOKE_ROOT_SELECTOR,
            },
        )
        assert response.ok, f"Homepage returned HTTP {response.status}"
        await expect(page.locator(SMOKE_ROOT_SELECTOR).first).to_be_visible(timeout=5000)
