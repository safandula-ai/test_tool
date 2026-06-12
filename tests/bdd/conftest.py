from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import Settings, get_settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose shared runtime settings to BDD scenarios."""
    return get_settings()


@pytest.fixture
def sync_browser(settings: Settings) -> Iterator[Browser]:
    """Start an isolated synchronous browser for a BDD scenario."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=settings.headless, slow_mo=settings.slow_mo)
        yield browser
        browser.close()


@pytest.fixture
def sync_context(sync_browser: Browser, settings: Settings) -> Iterator[BrowserContext]:
    """Create a browser context for each BDD scenario."""
    context = sync_browser.new_context(base_url=settings.base_url)
    yield context
    context.close()


@pytest.fixture
def sync_page(sync_context: BrowserContext) -> Iterator[Page]:
    """Create a fresh page for a BDD scenario."""
    page = sync_context.new_page()
    yield page
    page.close()
