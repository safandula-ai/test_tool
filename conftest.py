from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import httpx
import pytest
import pytest_asyncio
from faker import Faker
from playwright.async_api import Page, async_playwright

from config.settings import Settings, get_settings
from utils.api_mocks import build_transport
from utils.logging import get_logger


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose shared runtime settings to tests."""
    return get_settings()


@pytest.fixture(scope="session")
def fake() -> Faker:
    """Expose a reusable Faker instance."""
    return Faker()


@pytest.fixture(scope="session")
def logger(settings: Settings):
    """Expose the configured project logger."""
    return get_logger(settings.log_level)


@pytest_asyncio.fixture
async def api_client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async HTTP client bound to the API base URL."""
    transport = build_transport()
    client = httpx.AsyncClient(
        base_url=settings.api_base_url,
        transport=transport,
        timeout=settings.http_timeout,
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def reqres_http_client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
    """Provide an authenticated client for opt-in live ReqRes tests."""
    headers = {"x-api-key": settings.reqres_api_key} if settings.reqres_api_key else {}
    client = httpx.AsyncClient(
        base_url=settings.reqres_base_url,
        headers=headers,
        timeout=settings.http_timeout,
    )
    yield client
    await client.aclose()


@pytest.fixture
def page_factory(
    request: pytest.FixtureRequest,
    settings: Settings,
) -> Callable[[str | None], AsyncContextManager[Page]]:
    """Build isolated async Playwright pages without async pytest fixtures."""

    @asynccontextmanager
    async def create_page(base_url: str | None = None) -> AsyncIterator[Page]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=settings.headless,
                slow_mo=settings.slow_mo,
            )
            context = await browser.new_context(
                base_url=base_url or settings.base_url,
                record_video_dir=str(settings.video_dir) if settings.video_on_failure else None,
            )
            if settings.trace_on_failure:
                await context.tracing.start(screenshots=True, snapshots=True, sources=True)

            page = await context.new_page()
            try:
                yield page
            finally:
                failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
                if failed and settings.screenshot_on_failure:
                    await page.screenshot(path=str(settings.screenshot_dir / f"{request.node.name}.png"), full_page=True)
                if settings.trace_on_failure:
                    if failed:
                        await context.tracing.stop(path=str(settings.artifact_dir / f"{request.node.name}.zip"))
                    else:
                        await context.tracing.stop()
                await context.close()
                await browser.close()

    return create_page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach test phase results to the item for fixture cleanup hooks."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
