"""Filesystem layout for website-specific pytest suites."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


SUITE_DIRECTORIES = ("api", "ui", "smoke", "performance", "generated")

def render_smoke_test_source(suite_name: str) -> str:
    """Render the standard fast-failure smoke checks for a website suite."""
    return f'''"""Critical availability smoke tests for this website suite."""

from urllib.parse import urljoin
from time import perf_counter

import pytest
from playwright.async_api import async_playwright, expect

from coverage_agent.decorators import covers
from utils.smoke_diagnostics import emit_smoke_diagnostics
from tests.websites.{suite_name}.suite_config import (
    BASE_URL,
    SMOKE_HEALTH_PATH,
    SMOKE_HEALTH_STATUS,
    SMOKE_RENDER_TIMEOUT_MS,
    SMOKE_REQUEST_TIMEOUT_MS,
    SMOKE_ROOT_PATH,
    SMOKE_ROOT_SELECTOR,
)


def _target_url(pytestconfig):
    return (pytestconfig.getoption("--target-url") or BASE_URL).rstrip("/")


def _require_live_target(pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")


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
    _require_live_target(pytestconfig, settings)
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
    _require_live_target(pytestconfig, settings)
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
            details={{
                "root_path": SMOKE_ROOT_PATH,
                "root_selector": SMOKE_ROOT_SELECTOR,
            }},
        )
        assert response.ok, f"Homepage returned HTTP {{response.status}}"
        await expect(page.locator(SMOKE_ROOT_SELECTOR).first).to_be_visible(timeout=5_000)
'''

PERFORMANCE_TEST_SOURCE = '''"""Generic response-time check for this website suite."""

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
            f"SUITE_NAME = {json.dumps(name)}\n"
            'SMOKE_HEALTH_PATH = "/"\n'
            "SMOKE_HEALTH_STATUS = 200\n"
            'SMOKE_ROOT_PATH = "/"\n'
            'SMOKE_ROOT_SELECTOR = "body"\n'
            "SMOKE_REQUEST_TIMEOUT_MS = 5_000\n"
            "SMOKE_RENDER_TIMEOUT_MS = 8_000\n",
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
    performance_source = (
        performance_file.read_text(encoding="utf-8") if performance_file.exists() else ""
    )
    if not performance_file.exists() or "Generic response-time check" in performance_source:
        performance_file.write_text(PERFORMANCE_TEST_SOURCE, encoding="utf-8")
    return WebsiteSuite(name=name, base_url=normalized_url, root=root)
