from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import Settings, get_settings
from tests.websites.saucedemo_com.suite_config import BASE_URL
from utils.smoke_diagnostics import sanitize_headers
from utils.test_diagnostics import TestDiagnosticRecorder


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose shared runtime settings to SauceDemo BDD scenarios."""
    return get_settings()


@pytest.fixture
def sync_browser(settings: Settings) -> Iterator[Browser]:
    """Start a synchronous browser for one live SauceDemo scenario."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=settings.headless, slow_mo=settings.slow_mo)
        yield browser
        browser.close()


@pytest.fixture
def sync_context(
    sync_browser: Browser,
    test_diagnostics: TestDiagnosticRecorder,
) -> Iterator[BrowserContext]:
    """Create an isolated browser context for a live SauceDemo scenario."""
    context = sync_browser.new_context(base_url=BASE_URL)
    test_diagnostics.record(
        "browser_context_configured",
        configured_base_url=BASE_URL,
        suite="saucedemo_com",
        execution_mode="sync_playwright",
    )
    yield context
    context.close()


@pytest.fixture
def sync_page(
    sync_context: BrowserContext,
    test_diagnostics: TestDiagnosticRecorder,
) -> Iterator[Page]:
    """Create a fresh page for a live SauceDemo BDD scenario."""
    page = sync_context.new_page()
    test_diagnostics.record(
        "browser_page_opened",
        initial_url=page.url,
        execution_mode="sync_playwright",
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
