"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import json
import pytest

from coverage_agent.plugins.toptal import sanitize_toptal_response_payload

from tests.websites.toptal_com.suite_config import BASE_URL

from ._test_generated_coverage_gaps_api_helpers import (
    fetch_json_via_browser,
    load_generated_case_data,
)

from coverage_agent.decorators import covers

CASE_DATA = load_generated_case_data(__file__, '_test_generated_coverage_gaps_api_data.json')

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.api,
]


@covers(
    type="api",
    target='GET /api/cms/sessions :: status 200',
    priority="high",
    template="ApiServiceTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_get_api_cms_sessions_status_200(
    page_factory, test_diagnostics
):
    # Expected Response Code: 200
    # Expected Response Message: {"success": false, "talent_signup_data": null, "user":
    #   null}
    expected_payload = json.loads('{"success": false, "talent_signup_data": null, "user": null}')
    async with page_factory(BASE_URL) as browser_page:
        await browser_page.goto("/")
        fetch_result = await fetch_json_via_browser(
            browser_page,
            path='/api/cms/sessions',
            method="GET",
        )
    assert fetch_result["status"] == int('200')
    payload = sanitize_toptal_response_payload(json.loads(fetch_result["text"]))
    test_diagnostics.record(
        "generated_api_payload",
        endpoint='/api/cms/sessions',
        method="GET",
        status=fetch_result["status"],
        expected_payload=expected_payload,
        observed_payload=payload,
    )
    assert payload == expected_payload
