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
    sanitized = re.sub(
        r"\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "record_id",
        value.lower(),
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", sanitized).strip("_")
    return normalized or "target"


def _helper_module_name(output_path: str | Path) -> str:
    destination = Path(output_path)
    return f"_{destination.stem}_helpers.py"


def _data_file_name(output_path: str | Path) -> str:
    destination = Path(output_path)
    return f"_{destination.stem}_data.json"


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
        response_payload = str(case.api_details.get("response_payload", "")).strip()
        if response_payload:
            if len(response_payload) <= 120 and "\n" not in response_payload:
                comment_lines.append(
                    f"# Expected Response Message: {case.api_details['response_payload']}"
                )
            else:
                comment_lines.append("# Expected Response Payload: see generated case data")
        return method, path, comment_lines

    method, path = case.target.split(" ", 1)
    return method, path, []


def _is_automationexercise(base_url: str | None) -> bool:
    return bool(base_url and "automationexercise.com" in base_url.lower())


def _is_reqres(base_url: str | None) -> bool:
    return bool(base_url and "reqres.in" in base_url.lower())


def _reqres_placeholder_path(path: str) -> str:
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        path,
    )


def _reqres_placeholder_url(url: str) -> str:
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        url,
    )


def _reqres_placeholder_target(target: str) -> str:
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        target,
    )


def _render_helper_module(
    *,
    include_ui_helpers: bool,
    include_automationexercise_helpers: bool,
    include_reqres_helpers: bool,
) -> str:
    if not include_ui_helpers and not include_automationexercise_helpers and not include_reqres_helpers:
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
    elif include_reqres_helpers:
        lines.extend(
            [
                "import json",
                "from pathlib import Path",
                "from uuid import uuid4",
                "from urllib.parse import parse_qsl, urlsplit",
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

    if include_reqres_helpers:
        lines.extend(
            [
                "",
                "def reqres_default_record_payload(test_name: str) -> dict[str, object]:",
                "    return {",
                '        "data": {',
                '            "name": f"Generated {test_name}",',
                '            "price": 59.99,',
                '            "category": "Electronics",',
                '            "in_stock": True,',
                "        }",
                "    }",
                "",
                "",
                "def reqres_query_params(full_url: str | None) -> dict[str, str]:",
                "    if not full_url:",
                "        return {}",
                "    parsed = urlsplit(full_url)",
                "    return dict(parse_qsl(parsed.query, keep_blank_values=True))",
                "",
                "",
                "def reqres_request_payload(",
                "    request_body: str | None,",
                "    *,",
                "    expected_response_payload: str | None = None,",
                "    test_name: str,",
                ") -> dict[str, object]:",
                "    if request_body:",
                "        return json.loads(request_body)",
                "    if expected_response_payload:",
                "        try:",
                "            expected = json.loads(expected_response_payload)",
                "        except json.JSONDecodeError:",
                "            expected = None",
                "        if isinstance(expected, dict):",
                '            data = expected.get("data")',
                "            if isinstance(data, dict):",
                '                nested = data.get("data")',
                "                if isinstance(nested, dict):",
                '                    return {"data": nested}',
                "            elif isinstance(data, list):",
                "                for item in data:",
                "                    if not isinstance(item, dict):",
                "                        continue",
                '                    nested = item.get("data")',
                "                    if isinstance(nested, dict):",
                '                        return {"data": nested}',
                "    return reqres_default_record_payload(test_name)",
                "",
                "",
                "def reqres_expected_payload_fragment(expected_response_payload: str | None) -> str:",
                "    if not expected_response_payload:",
                '        return ""',
                "    try:",
                "        payload = json.loads(expected_response_payload)",
                "    except json.JSONDecodeError:",
                "        return expected_response_payload",
                "    if isinstance(payload, dict):",
                '        data = payload.get("data")',
                "        if isinstance(data, dict):",
                '            nested = data.get("data")',
                "            if isinstance(nested, dict):",
                "                return json.dumps(nested, sort_keys=True)",
                "        elif isinstance(data, list):",
                "            for item in data:",
                "                if not isinstance(item, dict):",
                "                    continue",
                '                nested = item.get("data")',
                "                if isinstance(nested, dict):",
                "                    return json.dumps(nested, sort_keys=True)",
                "    return json.dumps(payload, sort_keys=True)",
                "",
                "",
                "def reqres_extract_record_id(payload: object) -> str | None:",
                "    if isinstance(payload, dict):",
                '        value = payload.get("id")',
                "        if value is not None:",
                "            return str(value)",
                "        for nested in payload.values():",
                "            extracted = reqres_extract_record_id(nested)",
                "            if extracted is not None:",
                "                return extracted",
                "    elif isinstance(payload, list):",
                "        for nested in payload:",
                "            extracted = reqres_extract_record_id(nested)",
                "            if extracted is not None:",
                "                return extracted",
                "    return None",
                "",
                "",
                "async def reqres_request_kwargs(",
                "    client,",
                "    *,",
                "    test_name: str,",
                "    path: str,",
                "    method: str,",
                "    full_url: str | None,",
                "    request_body: str | None,",
                "    expected_response_payload: str | None,",
                ") -> tuple[str, dict[str, object], dict[str, object] | None]:",
                "    params = reqres_query_params(full_url)",
                "    request_kwargs: dict[str, object] = {}",
                "    if params:",
                '        request_kwargs["params"] = params',
                "    payload = reqres_request_payload(",
                "        request_body,",
                "        expected_response_payload=expected_response_payload,",
                "        test_name=test_name,",
                "    )",
                "    cleanup: dict[str, object] | None = None",
                "    resolved_path = path",
                "",
                '    if "/api/collections/products/records/" in path and method in {"GET", "PUT", "DELETE"}:',
                "        # The documentation uses example record ids. For live tests, create",
                "        # a disposable record first and replace the example id with the real one.",
                "        create_response = await client.post(",
                '            "/api/collections/products/records",',
                "            params=params or None,",
                "            json=payload,",
                "        )",
                "        assert create_response.status_code in {200, 201}",
                "        record_id = reqres_extract_record_id(create_response.json())",
                '        assert record_id, "ReqRes create record response did not include an id"',
                '        resolved_path = f"/api/collections/products/records/{record_id}"',
                '        cleanup = {"path": resolved_path, "params": params or None}',
                '        if method == "PUT":',
                '            request_kwargs["json"] = payload',
                "        return resolved_path, request_kwargs, cleanup",
                "",
                '    if method in {"POST", "PUT", "PATCH"}:',
                '        request_kwargs["json"] = payload',
                '        if path == "/api/collections/products/records":',
                '            cleanup = {"path": None, "params": None}',
                "    return resolved_path, request_kwargs, cleanup",
                "",
                "",
                "async def cleanup_reqres_record(client, cleanup: dict[str, object] | None) -> None:",
                "    if not cleanup:",
                "        return",
                '    path = cleanup.get("path")',
                "    if not path:",
                "        return",
                "    try:",
                '        await client.delete(path, params=cleanup.get("params"))',
                "    except Exception:",
                "        return",
                "",
                "",
                "def load_generated_case_data(module_file: str, file_name: str) -> dict[str, dict[str, str]]:",
                "    data_path = Path(module_file).with_name(file_name)",
                "    if not data_path.is_file():",
                "        return {}",
                "    return json.loads(data_path.read_text(encoding='utf-8'))",
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
    data_file_name: str | None = None,
) -> str:
    """Render a deterministic generated pytest module."""
    automationexercise = _is_automationexercise(base_url)
    reqres = _is_reqres(base_url)
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
    if reqres:
        helper_imports.extend(
            [
                "cleanup_reqres_record",
                "load_generated_case_data",
                "reqres_expected_payload_fragment",
                "reqres_request_kwargs",
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
    if data_file_name:
        header_lines.extend(
            [
                f"CASE_DATA = load_generated_case_data(__file__, {data_file_name!r})",
                "",
            ]
        )
    if reqres:
        header_lines.extend(
            [
                "from config.settings import get_settings",
                "",
                "_SETTINGS = get_settings()",
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
        ]
    )
    if reqres:
        header_lines.extend(
            [
                "    pytest.mark.skipif(",
                "        not _SETTINGS.run_live_tests or not _SETTINGS.reqres_api_key,",
                '        reason="Set RUN_LIVE_TESTS=true and REQRES_API_KEY for ReqRes generated API coverage",',
                "    ),",
            ]
        )
    header_lines.append("]")
    header = "\n".join(header_lines)

    functions: list[str] = []
    for case in sorted(cases, key=lambda item: (item.coverage_type, item.target)):
        name = f"{case.coverage_type}_{_identifier(case.target)}"
        rendered_target = _reqres_placeholder_target(case.target) if reqres else case.target
        target_literal = json.dumps(rendered_target)
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
            response_status_assertion = (
                f"assert response.status_code == int({repr(str(case.api_details.get('response_code', '')).strip())})"
                if case.api_details and str(case.api_details.get("response_code", "")).strip()
                else "assert response.status_code != 500"
            )
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
            has_expected_payload = bool(
                case.api_details and str(case.api_details.get("response_payload", "")).strip()
            )
            scenario_name = (
                repr(str(case.api_details.get("name", "")).strip())
                if case.api_details
                else "''"
            )
            case_data_ref = f"CASE_DATA.get({name!r}, {{}})"
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
            response_payload_kind_value = (
                str(case.api_details.get("response_payload_kind", "message")).strip()
                if case.api_details
                else "message"
            )
            full_url = (
                repr(str(case.api_details.get("full_url", "")).strip())
                if case.api_details and case.api_details.get("full_url")
                else "None"
            )
            rendered_path = _reqres_placeholder_path(path) if reqres else path
            rendered_full_url = (
                repr(_reqres_placeholder_url(str(case.api_details.get("full_url", "")).strip()))
                if reqres and case.api_details and case.api_details.get("full_url")
                else full_url
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
            elif reqres:
                if response_payload_kind_value == "json":
                    response_assertion = """payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload""" if has_expected_payload else """payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))"""
                    reqres_case_locals = f"""    case_data = {case_data_ref}
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")"""
                elif response_payload_kind_value == "none":
                    response_assertion = ""
                    reqres_case_locals = f"""    case_data = {case_data_ref}
    raw_expected_response_payload = None
    request_body = case_data.get("request_body")"""
                else:
                    response_assertion = """payload = response.json() if response.content else None
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload""" if has_expected_payload else """payload = response.json() if response.content else None"""
                    reqres_case_locals = f"""    case_data = {case_data_ref}
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")"""
                body = f'''{comment_block}{reqres_case_locals}
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name={name!r},
        path={rendered_path!r},
        method={method!r},
        full_url={rendered_full_url},
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("{method}", resolved_path, **request_kwargs)
        {response_status_assertion}
        {response_assertion}
    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)
'''
            else:
                if response_payload_kind_value == "json":
                    response_assertion = """payload = response.json()
    assert isinstance(payload, (dict, list))
    rendered_payload = json.dumps(payload, sort_keys=True)
    assert expected_message in rendered_payload""" if has_expected_payload else """payload = response.json()
    assert isinstance(payload, (dict, list))"""
                elif response_payload_kind_value == "none":
                    response_assertion = ""
                else:
                    response_assertion = f'''payload = response.json()
    rendered_payload = json.dumps(payload, sort_keys=True)
    assert {expected_message} in rendered_payload''' if has_expected_payload else "payload = response.json()"
                body = f'''{comment_block}    url = f"{{DEFAULT_BASE_URL}}{rendered_path}"
    response = await api_client.request("{method}", url)
    {response_status_assertion}
    {response_assertion}
'''
            functions.append(
                f'''\n\n{decorator}
async def test_generated_{name}({"settings, test_diagnostics" if automationexercise else "settings, reqres_http_client" if reqres else "api_client"}):
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
    data_filename = _data_file_name(destination)
    helper_stem = Path(helper_filename).stem
    data_payload: dict[str, dict[str, str]] = {}
    for case in cases:
        if case.coverage_type != "api" or not case.api_details:
            continue
        data_entry: dict[str, str] = {}
        for key in ("request_body", "response_payload"):
            value = case.api_details.get(key)
            if value:
                data_entry[key] = str(value)
        if data_entry:
            name = f"{case.coverage_type}_{_identifier(case.target)}"
            data_payload[name] = data_entry
    helper_source = _render_helper_module(
        include_ui_helpers=any(case.coverage_type == "ui" for case in cases),
        include_automationexercise_helpers=_is_automationexercise(base_url),
        include_reqres_helpers=_is_reqres(base_url),
    )

    destination.write_text(
        render_gap_tests(
            page,
            cases,
            base_url=base_url,
            base_url_setting=base_url_setting,
            feature=feature,
            helper_module_stem=helper_stem if helper_source else None,
            data_file_name=data_filename if data_payload and helper_source else None,
        ),
        encoding="utf-8",
    )
    if helper_source:
        (destination.parent / helper_filename).write_text(
            helper_source,
            encoding="utf-8",
        )
    if data_payload:
        (destination.parent / data_filename).write_text(
            json.dumps(data_payload, indent=2) + "\n",
            encoding="utf-8",
        )
    return len(cases)
