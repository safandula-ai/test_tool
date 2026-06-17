"""Reusable one-shot security tests for a live website target.

Copy this file into a dedicated website suite and replace the route/selector constants below.
By default the target comes from `BASE_URL`; pass `--target-url` to override it.
"""

from __future__ import annotations

import pytest

from coverage_agent.decorators import covers
from tests.one_shot.helpers import require_live_target, target_url
from tests.one_shot.suite_config import (
    BASE_URL,
    SECURITY_CONSENT_ACCEPT_SELECTOR,
    SECURITY_CONSENT_ROOT_SELECTOR,
    SECURITY_SEARCH_INPUT_SELECTOR,
    SECURITY_SEARCH_PATH,
    SECURITY_SEARCH_SUBMIT_SELECTOR,
    SUITE_NAME,
)


async def _dismiss_consent_if_present(page, test_diagnostics) -> None:
    root = page.locator(SECURITY_CONSENT_ROOT_SELECTOR).first
    if await root.count() == 0:
        test_diagnostics.record(
            "security_consent",
            action="consent_not_present",
            payload={"root_selector": SECURITY_CONSENT_ROOT_SELECTOR},
        )
        return
    accept_button = page.locator(SECURITY_CONSENT_ACCEPT_SELECTOR).first
    if await accept_button.is_visible():
        test_diagnostics.record(
            "security_consent",
            action="click_accept",
            payload={
                "root_selector": SECURITY_CONSENT_ROOT_SELECTOR,
                "accept_selector": SECURITY_CONSENT_ACCEPT_SELECTOR,
            },
        )
        await accept_button.click(force=True)
    if await root.is_visible():
        test_diagnostics.record(
            "security_consent",
            action="remove_overlay",
            payload={"root_selector": SECURITY_CONSENT_ROOT_SELECTOR},
        )
        await page.evaluate(
            """(rootSelector) => {
                const root = document.querySelector(rootSelector);
                if (root) {
                    root.remove();
                }
                const overlay = document.querySelector('.fc-dialog-overlay');
                if (overlay) {
                    overlay.remove();
                }
                document.body.style.overflow = 'auto';
            }""",
            SECURITY_CONSENT_ROOT_SELECTOR,
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
    test_diagnostics,
):
    require_live_target(pytestconfig, default_base_url=BASE_URL)
    base_url = target_url(pytestconfig, default_base_url=BASE_URL)
    xss_payload = '<script id="malicious-xss">window.__xss_executed = true;</script>'
    test_diagnostics.record(
        "test_surface",
        mode="live_page",
        url=base_url,
        payload={
            "suite": SUITE_NAME,
            "route": SECURITY_SEARCH_PATH,
            "search_input_selector": SECURITY_SEARCH_INPUT_SELECTOR,
            "search_submit_selector": SECURITY_SEARCH_SUBMIT_SELECTOR,
        },
    )

    async with page_factory(base_url) as page:
        test_diagnostics.record(
            "journey_step",
            step="open_search_surface",
            payload={"route": SECURITY_SEARCH_PATH},
        )
        await page.goto(SECURITY_SEARCH_PATH, wait_until="domcontentloaded")
        await _dismiss_consent_if_present(page, test_diagnostics)
        await page.wait_for_load_state("networkidle")
        search_input = page.locator(SECURITY_SEARCH_INPUT_SELECTOR).first
        search_submit = page.locator(SECURITY_SEARCH_SUBMIT_SELECTOR).first
        search_input_count = await search_input.count()
        search_submit_count = await search_submit.count()
        test_diagnostics.record(
            "security_search_controls",
            payload={
                "search_input_selector": SECURITY_SEARCH_INPUT_SELECTOR,
                "search_input_count": search_input_count,
                "search_submit_selector": SECURITY_SEARCH_SUBMIT_SELECTOR,
                "search_submit_count": search_submit_count,
            },
        )
        if search_input_count == 0 or search_submit_count == 0:
            pytest.skip("Search controls are not available on the target page")
        test_diagnostics.record(
            "journey_step",
            step="submit_xss_probe",
            payload={"probe_payload": xss_payload},
        )
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
    assert not script_executed, "Executable script injection reached the browser context"
    assert script_node_count == 0, "Injected script tag was inserted into the DOM"
    assert '<script id="malicious-xss">' not in rendered_markup, (
        "Injected script tag was inserted into rendered markup"
    )
    assert reflected_input_value == xss_payload, (
        "Input value was unexpectedly transformed; review whether the target sanitizes or mutates input"
    )


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
    test_diagnostics,
):
    require_live_target(pytestconfig, default_base_url=BASE_URL)
    base_url = target_url(pytestconfig, default_base_url=BASE_URL)
    required_headers = {
        "strict-transport-security": "HSTS protocol enforcement",
        "x-frame-options": "clickjacking mitigation",
        "content-security-policy": "content security policy",
    }
    test_diagnostics.record(
        "test_surface",
        mode="live_page",
        url=base_url,
        payload={
            "suite": SUITE_NAME,
            "route": "/",
            "required_headers": required_headers,
        },
    )

    async with page_factory(base_url) as page:
        test_diagnostics.record(
            "journey_step",
            step="open_headers_audit_route",
            payload={"route": "/"},
        )
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
        payload={"required_headers": required_headers},
        missing_headers=missing_headers,
        present_headers=sorted(
            header_name for header_name in required_headers if header_name in headers
        ),
    )
    assert not missing_headers, f"Missing defense headers: {missing_headers}"
