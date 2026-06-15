"""Critical availability smoke tests for this website suite."""

from urllib.parse import urljoin
from time import perf_counter

import pytest
from playwright.async_api import async_playwright, expect

from coverage_agent.decorators import covers
from tests.websites.helpers import require_live_target, resolve_target_url
from tests.websites.automationexercise_com.suite_config import (
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
    target="website://automationexercise_com/backend-gateway-health",
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
    target="website://automationexercise_com/homepage-root",
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
            details={
                "root_path": SMOKE_ROOT_PATH,
                "root_selector": SMOKE_ROOT_SELECTOR,
            },
        )
        assert response.ok, f"Homepage returned HTTP {response.status}"
        await expect(page.locator(SMOKE_ROOT_SELECTOR).first).to_be_visible(timeout=5_000)
