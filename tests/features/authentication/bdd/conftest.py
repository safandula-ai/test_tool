from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import Settings, get_settings
from utils.smoke_diagnostics import sanitize_headers
from utils.test_diagnostics import TestDiagnosticRecorder


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
def sync_context(
    sync_browser: Browser,
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> Iterator[BrowserContext]:
    """Create a browser context for each BDD scenario."""
    context = sync_browser.new_context(base_url=settings.base_url)
    yield context
    context.close()


@pytest.fixture
def sync_page(
    sync_context: BrowserContext,
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> Iterator[Page]:
    """Create a fresh page for a BDD scenario."""
    page = sync_context.new_page()
    test_diagnostics.record(
        "browser_page_opened",
        base_url=settings.base_url,
        initial_url=page.url,
    )
    page.on(
        "response",
        lambda response: test_diagnostics.record(
            "browser_response",
            resource_type=response.request.resource_type,
            method=response.request.method,
            url=response.url,
            status=response.status,
            response_headers=sanitize_headers(response.all_headers()),
        )
        if response.request.resource_type in {"document", "xhr", "fetch"}
        else None,
    )
    yield page
    try:
        final_title = page.title()
    except Exception:
        final_title = "<unavailable>"
    test_diagnostics.record(
        "browser_page_final_state",
        url=page.url,
        title=final_title,
    )
    page.close()
