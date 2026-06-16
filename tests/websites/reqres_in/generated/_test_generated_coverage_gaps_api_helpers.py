"""Helper functions for generated coverage tests."""

from __future__ import annotations

import json
from pathlib import Path

from urllib.parse import parse_qsl, urlsplit


def reqres_default_record_payload(test_name: str) -> dict[str, object]:
    return {
        "data": {
            "name": f"Generated {test_name}",
            "price": 59.99,
            "category": "Electronics",
            "in_stock": True,
        }
    }


def reqres_query_params(full_url: str | None) -> dict[str, str]:
    if not full_url:
        return {}
    parsed = urlsplit(full_url)
    return dict(parse_qsl(parsed.query, keep_blank_values=True))


def reqres_request_payload(
    request_body: str | None,
    *,
    expected_response_payload: str | None = None,
    test_name: str,
) -> dict[str, object]:
    if request_body:
        return json.loads(request_body)
    if expected_response_payload:
        try:
            expected = json.loads(expected_response_payload)
        except json.JSONDecodeError:
            expected = None
        if isinstance(expected, dict):
            data = expected.get("data")
            if isinstance(data, dict):
                nested = data.get("data")
                if isinstance(nested, dict):
                    return {"data": nested}
            elif isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    nested = item.get("data")
                    if isinstance(nested, dict):
                        return {"data": nested}
    return reqres_default_record_payload(test_name)


def reqres_expected_payload_fragment(expected_response_payload: str | None) -> str:
    if not expected_response_payload:
        return ""
    try:
        payload = json.loads(expected_response_payload)
    except json.JSONDecodeError:
        return expected_response_payload
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict):
            nested = data.get("data")
            if isinstance(nested, dict):
                return json.dumps(nested, sort_keys=True)
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                nested = item.get("data")
                if isinstance(nested, dict):
                    return json.dumps(nested, sort_keys=True)
    return json.dumps(payload, sort_keys=True)


def reqres_extract_record_id(payload: object) -> str | None:
    if isinstance(payload, dict):
        value = payload.get("id")
        if value is not None:
            return str(value)
        for nested in payload.values():
            extracted = reqres_extract_record_id(nested)
            if extracted is not None:
                return extracted
    elif isinstance(payload, list):
        for nested in payload:
            extracted = reqres_extract_record_id(nested)
            if extracted is not None:
                return extracted
    return None


async def reqres_request_kwargs(
    client,
    *,
    test_name: str,
    path: str,
    method: str,
    full_url: str | None,
    request_body: str | None,
    expected_response_payload: str | None,
) -> tuple[str, dict[str, object], dict[str, object] | None]:
    params = reqres_query_params(full_url)
    request_kwargs: dict[str, object] = {}
    if params:
        request_kwargs["params"] = params
    payload = reqres_request_payload(
        request_body,
        expected_response_payload=expected_response_payload,
        test_name=test_name,
    )
    cleanup: dict[str, object] | None = None
    resolved_path = path

    if "/api/collections/products/records/" in path and method in {"GET", "PUT", "DELETE"}:
        # The documentation uses example record ids. For live tests, create
        # a disposable record first and replace the example id with the real one.
        create_response = await client.post(
            "/api/collections/products/records",
            params=params or None,
            json=payload,
        )
        assert create_response.status_code in {200, 201}
        record_id = reqres_extract_record_id(create_response.json())
        assert record_id, "ReqRes create record response did not include an id"
        resolved_path = f"/api/collections/products/records/{record_id}"
        cleanup = {"path": resolved_path, "params": params or None}
        if method == "PUT":
            request_kwargs["json"] = payload
        return resolved_path, request_kwargs, cleanup

    if method in {"POST", "PUT", "PATCH"}:
        request_kwargs["json"] = payload
        if path == "/api/collections/products/records":
            cleanup = {"path": None, "params": None}
    return resolved_path, request_kwargs, cleanup


async def cleanup_reqres_record(client, cleanup: dict[str, object] | None) -> None:
    if not cleanup:
        return
    path = cleanup.get("path")
    if not path:
        return
    try:
        await client.delete(path, params=cleanup.get("params"))
    except Exception:
        return


def load_generated_case_data(
    module_file: str,
    file_name: str,
) -> dict[str, dict[str, object]]:
    data_path = Path(module_file).with_name(file_name)
    if not data_path.is_file():
        return {}
    return json.loads(data_path.read_text(encoding='utf-8'))
