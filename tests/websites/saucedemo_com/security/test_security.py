"""Security verification tests for this website suite."""

from __future__ import annotations

import pytest

from coverage_agent.decorators import covers
from tests.websites.helpers import (
    dismiss_consent_if_present,
    require_live_target,
    resolve_target_url,
)
from tests.websites.saucedemo_com.suite_config import (
    BASE_URL,
    SECURITY_CONSENT_ACCEPT_SELECTOR,
    SECURITY_CONSENT_OVERLAY_SELECTOR,
    SECURITY_CONSENT_ROOT_SELECTOR,
    SECURITY_SEARCH_INPUT_SELECTOR,
    SECURITY_SEARCH_PATH,
    SECURITY_SEARCH_SUBMIT_SELECTOR,
)


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
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'

    async with page_factory(base_url) as page:
        await page.goto(SECURITY_SEARCH_PATH, wait_until="domcontentloaded")
        await dismiss_consent_if_present(
            page,
            root_selector=SECURITY_CONSENT_ROOT_SELECTOR,
            accept_selector=SECURITY_CONSENT_ACCEPT_SELECTOR,
            overlay_selector=SECURITY_CONSENT_OVERLAY_SELECTOR,
        )
        await page.wait_for_load_state("networkidle")
        search_input = page.locator(SECURITY_SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SECURITY_SEARCH_SUBMIT_SELECTOR).first
        if await search_input.count() == 0 or await search_submit.count() == 0:
            pytest.skip("Search controls are not available on the target page")
        await search_input.fill(xss_payload)
        await search_submit.click(force=True)
        await page.wait_for_load_state("networkidle")
        script_node = page.locator("script#malicious-xss")
        script_executed = await page.evaluate("() => Boolean(window.__xss_executed)")
        script_node_count = await script_node.count()
        rendered_markup = await page.locator("body").inner_html()
        reflected_input_value = await search_input.input_value()

    test_diagnostics.record(
        "security_xss_probe",
        route=SECURITY_SEARCH_PATH,
        payload=xss_payload,
        script_executed=script_executed,
        script_node_count=script_node_count,
        reflected_input_value=reflected_input_value,
    )
    assert not script_executed
    assert script_node_count == 0
    assert '<script id="malicious-xss">' not in rendered_markup
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
    pytestconfig,
    settings,
    test_diagnostics,
):
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    required_headers = {
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }

    async with page_factory(base_url) as page:
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
