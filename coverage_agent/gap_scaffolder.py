"""Generate executable pytest coverage from machine-readable gap reports."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_UI_TEMPLATES = {
    "ComponentVisibilityTemplate",
    "FormValidationTemplate",
    "InputValidationTemplate",
    "InteractionTemplate",
}


@dataclass(frozen=True)
class GapCase:
    target: str
    coverage_type: str
    template: str
    presence: str = "deterministic"
    api_details: dict[str, Any] | None = None


def _identifier(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "target"


def _helper_module_name(output_path: str | Path) -> str:
    destination = Path(output_path)
    return f"_{destination.stem}_helpers.py"


def load_gap_cases(report_path: str | Path) -> tuple[str, str | None, list[GapCase]]:
    """Load UI and API gap cases from a gap report."""
    with Path(report_path).open(encoding="utf-8") as file:
        report = json.load(file)
    page = report.get("page", "unknown")

    cases = [
        GapCase(
            item,
            "ui",
            "ComponentVisibilityTemplate",
        )
        for item in report.get("untested_ui_elements", [])
    ]
    cases.extend(
        GapCase(
            item["target"] if isinstance(item, dict) else item,
            "api",
            "ApiServiceTemplate",
            api_details=item if isinstance(item, dict) else None,
        )
        for item in report.get("untested_api_endpoints", [])
    )
    return page, report.get("base_url"), cases


def _ui_assertion(template: str) -> str:
    if template in {"InputValidationTemplate", "FormValidationTemplate"}:
        return "await assert_input_validation(target)"
    if template == "InteractionTemplate":
        return "await assert_interaction(target)"
    return "await assert_visible(target)"


def _api_case_metadata(case: GapCase) -> tuple[str, str, list[str]]:
    if case.api_details:
        method = str(case.api_details.get("method", "")).upper()
        path = str(case.api_details.get("path", ""))
        comment_lines = []
        if case.api_details.get("name"):
            comment_lines.append(f"# Scenario: {case.api_details['name']}")
        if case.api_details.get("request_parameters"):
            comment_lines.append(
                f"# Request Parameters: {case.api_details['request_parameters']}"
            )
        if case.api_details.get("response_code"):
            comment_lines.append(
                f"# Expected Response Code: {case.api_details['response_code']}"
            )
        if case.api_details.get("response_payload"):
            comment_lines.append(
                f"# Expected Response Message: {case.api_details['response_payload']}"
            )
        return method, path, comment_lines

    method, path = case.target.split(" ", 1)
    return method, path, []


def _is_automationexercise(base_url: str | None) -> bool:
    return bool(base_url and "automationexercise.com" in base_url.lower())


def _render_helper_module(
    *,
    include_ui_helpers: bool,
    include_automationexercise_helpers: bool,
) -> str:
    if not include_ui_helpers and not include_automationexercise_helpers:
        return ""

    lines = [
        '"""Helper functions for generated coverage tests."""',
        "",
        "from __future__ import annotations",
        "",
    ]

    if include_automationexercise_helpers:
        lines.extend(
            [
                "import httpx",
                "from uuid import uuid4",
                "",
                "from api_clients.automation_exercise_client import build_account_payload",
                "",
            ]
        )

    if include_ui_helpers:
        lines.extend(
            [
                "from playwright.async_api import expect",
                "",
            ]
        )

    if include_ui_helpers:
        lines.extend(
            [
                "def target_locator(page, name: str):",
                '    escaped = name.replace(\'"\', \'\\\\"\')',
                "    return page.locator(",
                '        f\'[data-testid=\"{escaped}\"], [data-test=\"{escaped}\"], [data-qa=\"{escaped}\"]\'',
                "    ).first",
                "",
                "",
                "async def assert_visible(target) -> None:",
                "    await expect(target).to_be_visible()",
                "",
                "",
                "async def assert_input_validation(target) -> None:",
                "    await expect(target).to_be_visible()",
                "    await expect(target).to_be_editable()",
                '    input_type = (await target.get_attribute("type") or "text").lower()',
                '    await target.fill("not-a-valid-value")',
                '    if input_type in {"email", "url", "number"}:',
                '        assert not await target.evaluate("element => element.checkValidity()")',
                "    else:",
                '        assert await target.input_value() == "not-a-valid-value"',
                "",
                "",
                "async def assert_interaction(target) -> None:",
                "    await expect(target).to_be_visible()",
                "    await expect(target).to_be_enabled()",
                "",
            ]
        )

    if include_automationexercise_helpers:
        lines.extend(
            [
                "",
                "def default_request_payload(request_parameters: str | None) -> dict[str, str]:",
                "    payload: dict[str, str] = {}",
                "    if not request_parameters:",
                "        return payload",
                '    for raw_parameter in request_parameters.split(","):',
                "        parameter = raw_parameter.strip()",
                "        if not parameter:",
                "            continue",
                '        name = parameter.split("(", 1)[0].strip().replace(" ", "_")',
                "        if not name:",
                "            continue",
                '        if name == "email":',
                '            payload[name] = f"generated-{uuid4().hex[:10]}@example.com"',
                '        elif name == "password":',
                '            payload[name] = "secret-password"',
                '        elif name == "search_product":',
                '            payload[name] = "top"',
                "        else:",
                '            payload[name] = "test"',
                "    return payload",
                "",
                "",
                'def generated_account_payload(test_name: str, *, password: str = "secret-password") -> dict[str, str]:',
                '    email = f"{test_name}-{uuid4().hex[:10]}@example.com"',
                '    return build_account_payload("Generated User", email, password)',
                "",
                "",
                "async def cleanup_generated_account(",
                "    client: httpx.AsyncClient,",
                "    base_url: str,",
                "    payload: dict[str, str] | None,",
                ") -> None:",
                "    if not payload:",
                "        return",
                "    try:",
                "        await client.request(",
                '            "DELETE",',
                '            f"{base_url}/api/deleteAccount",',
                '            data={"email": payload["email"], "password": payload["password"]},',
                "        )",
                "    except Exception:",
                "        return",
                "",
                "",
                "async def automationexercise_request_kwargs(",
                "    client: httpx.AsyncClient,",
                "    *,",
                "    base_url: str,",
                "    test_name: str,",
                "    path: str,",
                "    method: str,",
                "    scenario: str,",
                "    request_parameters: str | None,",
                ") -> tuple[dict[str, object], dict[str, str] | None]:",
                "    scenario_lower = scenario.lower()",
                "    request_kwargs: dict[str, object] = {}",
                "    cleanup_payload: dict[str, str] | None = None",
                "",
                '    if path == "/api/createAccount" and method == "POST":',
                "        cleanup_payload = generated_account_payload(test_name)",
                '        request_kwargs["data"] = cleanup_payload',
                "        return request_kwargs, cleanup_payload",
                "",
                '    if path == "/api/deleteAccount" and method == "DELETE":',
                "        cleanup_payload = generated_account_payload(test_name)",
                "        await client.request(",
                '            "POST",',
                '            f"{base_url}/api/createAccount",',
                "            data=cleanup_payload,",
                "        )",
                '        request_kwargs["data"] = {',
                '            "email": cleanup_payload["email"],',
                '            "password": cleanup_payload["password"],',
                "        }",
                "        return request_kwargs, None",
                "",
                '    if path == "/api/updateAccount" and method == "PUT":',
                "        original_payload = generated_account_payload(test_name)",
                "        await client.request(",
                '            "POST",',
                '            f"{base_url}/api/createAccount",',
                "            data=original_payload,",
                "        )",
                "        cleanup_payload = dict(original_payload)",
                '        cleanup_payload["password"] = "updated-secret-password"',
                '        cleanup_payload["firstname"] = "Updated"',
                '        request_kwargs["data"] = cleanup_payload',
                "        return request_kwargs, cleanup_payload",
                "",
                '    if path == "/api/getUserDetailByEmail" and method == "GET":',
                "        cleanup_payload = generated_account_payload(test_name)",
                "        await client.request(",
                '            "POST",',
                '            f"{base_url}/api/createAccount",',
                "            data=cleanup_payload,",
                "        )",
                '        request_kwargs["params"] = {"email": cleanup_payload["email"]}',
                "        return request_kwargs, cleanup_payload",
                "",
                '    if path == "/api/verifyLogin" and method == "POST":',
                '        if "valid details" in scenario_lower:',
                "            cleanup_payload = generated_account_payload(test_name)",
                "            await client.request(",
                '                "POST",',
                '                f"{base_url}/api/createAccount",',
                "                data=cleanup_payload,",
                "            )",
                '            request_kwargs["data"] = {',
                '                "email": cleanup_payload["email"],',
                '                "password": cleanup_payload["password"],',
                "            }",
                "            return request_kwargs, cleanup_payload",
                '        if "without email parameter" in scenario_lower:',
                '            request_kwargs["data"] = {"password": "secret-password"}',
                "            return request_kwargs, cleanup_payload",
                '        if "without password parameter" in scenario_lower:',
                '            request_kwargs["data"] = {"email": f"generated-{uuid4().hex[:10]}@example.com"}',
                "            return request_kwargs, cleanup_payload",
                '        if "invalid details" in scenario_lower:',
                '            request_kwargs["data"] = {',
                '                "email": f"missing-{uuid4().hex[:10]}@example.com",',
                '                "password": "wrong-password",',
                "            }",
                "            return request_kwargs, cleanup_payload",
                "",
                '    if path == "/api/searchProduct" and method == "POST":',
                '        if "without search_product parameter" in scenario_lower:',
                '            request_kwargs["data"] = {}',
                "        else:",
                '            request_kwargs["data"] = {"search_product": "top"}',
                "        return request_kwargs, cleanup_payload",
                "",
                "    payload = default_request_payload(request_parameters)",
                "    if payload:",
                '        if method == "GET":',
                '            request_kwargs["params"] = payload',
                "        else:",
                '            request_kwargs["data"] = payload',
                "    return request_kwargs, cleanup_payload",
                "",
            ]
        )

    return "\n".join(lines)


def render_gap_tests(
    page: str,
    cases: list[GapCase],
    *,
    base_url: str | None = None,
    base_url_setting: str = "base_url",
    feature: str = "feature:generated-gap-coverage",
    helper_module_stem: str | None = None,
) -> str:
    """Render a deterministic generated pytest module."""
    automationexercise = _is_automationexercise(base_url)
    include_ui_helpers = any(case.coverage_type == "ui" for case in cases)
    helper_imports: list[str] = []
    if include_ui_helpers:
        helper_imports.extend(
            [
                "assert_input_validation",
                "assert_interaction",
                "assert_visible",
                "target_locator",
            ]
        )
    if automationexercise:
        helper_imports.extend(
            [
                "automationexercise_request_kwargs",
                "cleanup_generated_account",
            ]
        )

    header_lines = [
        '"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""',
        "",
        "from __future__ import annotations",
        "",
        "import pytest",
    ]
    if automationexercise:
        header_lines.append("import httpx")
    header_lines.extend(["import json", ""])
    if automationexercise:
        header_lines.extend(
            [
                "from utils.test_diagnostics import httpx_event_hooks",
                "",
            ]
        )
    if helper_imports and helper_module_stem:
        header_lines.extend(
            [
                f"from .{helper_module_stem} import (",
                *[f"    {name}," for name in helper_imports],
                ")",
                "",
            ]
        )
    header_lines.extend(
        [
            "from coverage_agent.decorators import covers",
            "",
            "",
            f"DEFAULT_BASE_URL = {base_url!r}",
            "",
            "pytestmark = [",
            "    pytest.mark.api,",
            "    pytest.mark.asyncio,",
            "]",
        ]
    )
    header = "\n".join(header_lines)

    functions: list[str] = []
    for case in sorted(cases, key=lambda item: (item.coverage_type, item.target)):
        name = f"{case.coverage_type}_{_identifier(case.target)}"
        target_literal = json.dumps(case.target)
        decorator = (
            f'@covers(type="{case.coverage_type}", target={target_literal}, priority="high", '
            f'template="{case.template}", page={page!r}, feature={feature!r}, '
            f'presence="{case.presence}")'
        )
        if case.coverage_type == "ui" and case.template in SUPPORTED_UI_TEMPLATES:
            functions.append(
                f'''\n\n{decorator}
async def test_generated_{name}(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, {base_url_setting!r})
    async with page_factory(base_url) as browser_page:
        await browser_page.goto({page!r})
        target = target_locator(browser_page, {target_literal})
        {_ui_assertion(case.template)}
'''
            )
        elif case.coverage_type == "api":
            method, path, comment_lines = _api_case_metadata(case)
            comment_block = "".join(f"    {line}\n" for line in comment_lines)
            expected_code = (
                repr(str(case.api_details.get("response_code", "")).strip())
                if case.api_details
                else "''"
            )
            expected_message = (
                repr(str(case.api_details.get("response_payload", "")).strip())
                if case.api_details
                else "''"
            )
            scenario_name = (
                repr(str(case.api_details.get("name", "")).strip())
                if case.api_details
                else "''"
            )
            request_parameters = (
                repr(str(case.api_details.get("request_parameters", "")).strip())
                if case.api_details and case.api_details.get("request_parameters")
                else "None"
            )
            response_payload_kind = (
                repr(str(case.api_details.get("response_payload_kind", "message")).strip())
                if case.api_details
                else "'message'"
            )
            if automationexercise:
                response_assertion = f'''response_payload = response.json()
            if {response_payload_kind} == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int({expected_code})
                assert response_payload["message"] == {expected_message}'''
                body = f'''{comment_block}    url = f"{{DEFAULT_BASE_URL}}{path}"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name={name!r},
            path={path!r},
            method={method!r},
            scenario={scenario_name},
            request_parameters={request_parameters},
        )
        try:
            response = await live_client.request("{method}", url, **request_kwargs)
            assert response.status_code == 200
            {response_assertion}
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)
'''
            else:
                response_assertion = f'''payload = response.json()
    if {response_payload_kind} == "json":
        assert isinstance(payload, (dict, list))
    elif {expected_message}:
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert {expected_message} in rendered_payload'''
                body = f'''{comment_block}    url = f"{{DEFAULT_BASE_URL}}{path}"
    response = await api_client.request("{method}", url)
    assert response.status_code == int({expected_code}) if {expected_code} else response.status_code != 500
    {response_assertion}
'''
            functions.append(
                f'''\n\n{decorator}
async def test_generated_{name}({"settings, test_diagnostics" if automationexercise else "api_client"}):
{body}
'''
            )
        else:
            functions.append(
                f'''\n\n# TODO: Implement domain-specific coverage before adding this decorator:
# {decorator}
async def todo_generated_{name}():
    raise NotImplementedError("Add status, schema, and business outcome assertions")
'''
            )
    return header + "".join(functions) + "\n"


def scaffold_gap_tests(
    report_path: str | Path,
    output_path: str | Path,
    *,
    base_url_setting: str = "base_url",
    feature: str = "feature:generated-gap-coverage",
) -> int:
    """Generate a pytest module and return the number of scaffolded gaps."""
    page, base_url, cases = load_gap_cases(report_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    helper_filename = _helper_module_name(destination)
    helper_stem = Path(helper_filename).stem
    helper_source = _render_helper_module(
        include_ui_helpers=any(case.coverage_type == "ui" for case in cases),
        include_automationexercise_helpers=_is_automationexercise(base_url),
    )

    destination.write_text(
        render_gap_tests(
            page,
            cases,
            base_url=base_url,
            base_url_setting=base_url_setting,
            feature=feature,
            helper_module_stem=helper_stem if helper_source else None,
        ),
        encoding="utf-8",
    )
    if helper_source:
        (destination.parent / helper_filename).write_text(
            helper_source,
            encoding="utf-8",
        )
    return len(cases)
