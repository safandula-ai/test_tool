"""Security verification tests for this website suite."""

from __future__ import annotations

import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers
from tests.websites.sabre_com.helpers import dismiss_sabre_consent
from tests.websites.sabre_com.suite_config import BASE_URL


SEARCH_TRIGGER_SELECTOR = "a.search"
SEARCH_TRIGGER_ACTIVE_SELECTOR = "a.search.is-active"
SEARCH_PANEL_ACTIVE_SELECTOR = ".site-header__main--search-panel.is-active"
SEARCH_INPUT_SELECTOR = (
    "form[action='https://www.sabre.com/'] input[name='s']"
)
SEARCH_SUBMIT_SELECTOR = "form[action='https://www.sabre.com/'] button[type='submit']"


@pytest.mark.security
@pytest.mark.ui
@pytest.mark.asyncio
@covers(
    type="ui",
    target="search-field-injection",
    priority="high",
    template="SecuritySanitizerTemplate",
    page="/",
    feature="feature:security",
)
async def test_search_rejects_reflected_xss_payload(
    page_factory,
    test_diagnostics,
):
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'

    async with page_factory(BASE_URL) as page:
        await page.goto("/", wait_until="domcontentloaded")
        await dismiss_sabre_consent(page)
        await page.locator(SEARCH_TRIGGER_SELECTOR).first.click(force=True)
        await expect(page.locator(SEARCH_TRIGGER_ACTIVE_SELECTOR).first).to_be_visible(timeout=5_000)
        await expect(page.locator(SEARCH_PANEL_ACTIVE_SELECTOR).first).to_be_visible(timeout=5_000)
        search_input = page.locator(SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SEARCH_SUBMIT_SELECTOR).first
        await expect(search_input).to_be_visible(timeout=5_000)
        await expect(search_submit).to_be_visible(timeout=5_000)
        test_diagnostics.record(
            "security_search_surface",
            trigger_selector=SEARCH_TRIGGER_SELECTOR,
            input_selector=SEARCH_INPUT_SELECTOR,
            submit_selector=SEARCH_SUBMIT_SELECTOR,
        )
        await search_input.fill(xss_payload)
        await search_submit.click(force=True)
        await page.wait_for_load_state("domcontentloaded")
        await dismiss_sabre_consent(page)
        script_node = page.locator("script#malicious-xss")
        script_executed = await page.evaluate("() => Boolean(window.__xss_executed)")
        script_node_count = await script_node.count()
        reflected_input_value = await page.locator(SEARCH_INPUT_SELECTOR).first.input_value()
        rendered_markup = await page.locator("body").inner_html()

    test_diagnostics.record(
        "security_xss_probe",
        route="/",
        payload=xss_payload,
        script_executed=script_executed,
        script_node_count=script_node_count,
        reflected_input_value=reflected_input_value,
    )
    assert not script_executed, "Executable script injection reached the browser context"
    assert script_node_count == 0, "Injected script tag was inserted into the DOM"
    assert '<script id="malicious-xss">' not in rendered_markup, (
        "Injected script tag was inserted into rendered markup"
    )
    assert reflected_input_value == xss_payload


@pytest.mark.security
@pytest.mark.api
@pytest.mark.asyncio
@covers(
    type="api",
    target="security-response-headers",
    priority="medium",
    template="APIContractTemplate",
    page="/",
    feature="feature:security",
)
async def test_http_security_defense_headers(
    page_factory,
    test_diagnostics,
):
    required_headers = {
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }

    async with page_factory(BASE_URL) as page:
        response = await page.goto("/", wait_until="domcontentloaded")
        assert response is not None, "Navigation completed without an HTTP response"
        headers = await response.all_headers()

    missing_headers = [
        f"{header_name} ({description})"
        for header_name, description in required_headers.items()
        if header_name not in headers
    ]
    test_diagnostics.record(
        "security_headers_audit",
        route="/",
        missing_headers=missing_headers,
        present_headers=sorted(
            header_name for header_name in required_headers if header_name in headers
        ),
    )
    assert not missing_headers, f"Missing defense headers: {missing_headers}"
