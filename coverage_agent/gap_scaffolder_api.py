"""API-specific gap scaffolding helpers."""

from __future__ import annotations

from coverage_agent.gap_scaffolder_common import (
    GapCase,
    comment_lines,
    identifier,
    reqres_placeholder_path,
    reqres_placeholder_url,
    wrapped_string_literal,
)


def api_case_metadata(case: GapCase) -> tuple[str, str, list[str]]:
    """Extract rendered method, path, and comment lines for one API gap case."""
    if case.api_details:
        method = str(case.api_details.get("method", "")).upper()
        path = str(case.api_details.get("path", ""))
        rendered_comment_lines = []
        if case.api_details.get("name"):
            rendered_comment_lines.extend(
                comment_lines("Scenario", str(case.api_details["name"]))
            )
        if case.api_details.get("request_parameters"):
            rendered_comment_lines.extend(
                comment_lines(
                    "Request Parameters",
                    str(case.api_details["request_parameters"]),
                )
            )
        if case.api_details.get("response_code"):
            rendered_comment_lines.append(
                f"# Expected Response Code: {case.api_details['response_code']}"
            )
        response_payload = str(case.api_details.get("response_payload", "")).strip()
        if response_payload:
            if len(response_payload) <= 120 and "\n" not in response_payload:
                rendered_comment_lines.extend(
                    comment_lines(
                        "Expected Response Message",
                        str(case.api_details["response_payload"]),
                    )
                )
            else:
                rendered_comment_lines.append("# Expected Response Payload: see generated case data")
        return method, path, rendered_comment_lines

    method, path = case.target.split(" ", 1)
    return method, path, []


def automationexercise_helper_imports() -> list[str]:
    """Return helper imports required by Automation Exercise generated API tests."""
    return [
        "automationexercise_request_kwargs",
        "cleanup_generated_account",
    ]


def reqres_helper_imports() -> list[str]:
    """Return helper imports required by ReqRes generated API tests."""
    return [
        "cleanup_reqres_record",
        "load_generated_case_data",
        "reqres_expected_payload_fragment",
        "reqres_request_kwargs",
    ]


def render_automationexercise_helper_lines() -> list[str]:
    """Emit generated helper source lines for live Automation Exercise API cases."""
    return [
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
        "def generated_account_payload(",
        '    test_name: str, *, password: str = "secret-password"',
        ") -> dict[str, str]:",
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


def render_reqres_helper_lines() -> list[str]:
    """Emit generated helper source lines for live ReqRes API cases."""
    return [
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
    ]


def render_data_loader_lines() -> list[str]:
    """Emit the shared JSON sidecar loader used by generated test modules."""
    return [
        "",
        "def load_generated_case_data(",
        "    module_file: str,",
        "    file_name: str,",
        ") -> dict[str, dict[str, object]]:",
        "    data_path = Path(module_file).with_name(file_name)",
        "    if not data_path.is_file():",
        "        return {}",
        "    return json.loads(data_path.read_text(encoding='utf-8'))",
        "",
    ]


def render_api_test_function(
    *,
    case: GapCase,
    decorator: str,
    base_url: str | None,
    website_suite_name: str | None,
    reqres: bool,
    automationexercise: bool,
) -> str:
    """Render one generated async API test for the selected target domain."""
    method, path, comment_lines_value = api_case_metadata(case)
    comment_block = "".join(f"    {line}\n" for line in comment_lines_value)
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
        wrapped_string_literal(
            str(case.api_details.get("name", "")).strip(),
            indent=" " * 12,
        )
        if case.api_details
        else "''"
    )
    name = f"{case.coverage_type}_{identifier(case.target)}"
    case_data_ref = f"CASE_DATA.get({name!r}, {{}})"
    request_parameters = (
        wrapped_string_literal(
            str(case.api_details.get("request_parameters", "")).strip(),
            indent=" " * 12,
        )
        if case.api_details and case.api_details.get("request_parameters")
        else "None"
    )
    response_payload_kind_value = (
        str(case.api_details.get("response_payload_kind", "message")).strip()
        if case.api_details
        else "message"
    )
    full_url = (
        wrapped_string_literal(
            str(case.api_details.get("full_url", "")).strip(),
            indent=" " * 12,
        )
        if case.api_details and case.api_details.get("full_url")
        else "None"
    )
    rendered_path = reqres_placeholder_path(path) if reqres else path
    rendered_full_url = (
        wrapped_string_literal(
            reqres_placeholder_url(
                str(case.api_details.get("full_url", "")).strip()
            ),
            indent=" " * 12,
        )
        if reqres and case.api_details and case.api_details.get("full_url")
        else full_url
    )

    if automationexercise:
        automationexercise_base_url = "BASE_URL" if website_suite_name else "DEFAULT_BASE_URL"
        if response_payload_kind_value == "json":
            response_assertion = """response_payload = response.json()
            assert isinstance(response_payload, (dict, list))"""
        else:
            response_assertion = f"""response_payload = response.json()
            assert response_payload["responseCode"] == int({expected_code})
            assert response_payload["message"] == {expected_message}"""
        body = f'''{comment_block}    url = f"{{{automationexercise_base_url}}}{path}"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url={automationexercise_base_url},
            test_name={wrapped_string_literal(name, indent=" " * 12)},
            path={wrapped_string_literal(path, indent=" " * 12)},
            method={wrapped_string_literal(method, indent=" " * 12)},
            scenario={scenario_name},
            request_parameters={request_parameters},
        )
        try:
            response = await live_client.request("{method}", url, **request_kwargs)
            assert response.status_code == 200
            {response_assertion}
        finally:
            await cleanup_generated_account(live_client, {automationexercise_base_url}, cleanup_payload)
'''
    elif reqres:
        if response_payload_kind_value == "json":
            response_assertion = (
                """payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload"""
                if has_expected_payload
                else """payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))"""
            )
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
            response_assertion = (
                """payload = response.json() if response.content else None
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload"""
                if has_expected_payload
                else """payload = response.json() if response.content else None"""
            )
            reqres_case_locals = f"""    case_data = {case_data_ref}
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")"""
        body = f'''{comment_block}{reqres_case_locals}
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name={wrapped_string_literal(name, indent=" " * 12)},
        path={wrapped_string_literal(rendered_path, indent=" " * 12)},
        method={wrapped_string_literal(method, indent=" " * 12)},
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
        generic_api_base_url = "BASE_URL" if website_suite_name else "DEFAULT_BASE_URL"
        if response_payload_kind_value == "json":
            response_assertion = (
                """payload = response.json()
    assert isinstance(payload, (dict, list))
    rendered_payload = json.dumps(payload, sort_keys=True)
    assert expected_message in rendered_payload"""
                if has_expected_payload
                else """payload = response.json()
    assert isinstance(payload, (dict, list))"""
            )
        elif response_payload_kind_value == "none":
            response_assertion = ""
        else:
            response_assertion = (
                f"""payload = response.json()
    rendered_payload = json.dumps(payload, sort_keys=True)
    assert {expected_message} in rendered_payload"""
                if has_expected_payload
                else "payload = response.json()"
            )
        body = f'''{comment_block}    url = f"{{{generic_api_base_url}}}{rendered_path}"
    response = await api_client.request("{method}", url)
    {response_status_assertion}
    {response_assertion}
'''

    signature = (
        "settings, test_diagnostics"
        if automationexercise
        else "settings, reqres_http_client"
        if reqres
        else "api_client"
    )
    return f'''\n{decorator}
async def test_generated_{name}(
    {signature}
):
{body}
'''
