"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import json
import pytest

from config.settings import get_settings

from ._test_generated_coverage_gaps_api_helpers import (
    cleanup_reqres_record,
    load_generated_case_data,
    reqres_expected_payload_fragment,
    reqres_request_kwargs,
)

from coverage_agent.decorators import covers

DEFAULT_BASE_URL = 'https://reqres.in'

_SETTINGS = get_settings()

CASE_DATA = load_generated_case_data(__file__, '_test_generated_coverage_gaps_api_data.json')

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.api,
    pytest.mark.skipif(
        not _SETTINGS.reqres_api_key,
        reason="Set REQRES_API_KEY for ReqRes generated API coverage",
    ),
]


@covers(
    type="api",
    target=(
        'DELETE /api/collections/products/records/{record_id_filled_during_test} '
        ':: Soft-delete a record | status 204'
    ),
    priority="high",
    template="ApiServiceTemplate",
    page='/documentation_sources/reqres_in.html',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_delete_api_collections_products_records_record_id_soft_delete_a_record_status_204(
    settings, reqres_http_client
):
    # Scenario: Soft-delete a record
    # Request Parameters: project_id
    # Expected Response Code: 204
    case_data = CASE_DATA.get(
        'api_delete_api_collections_products_records_record_id_soft_delete_a_record_status_204', {})
    raw_expected_response_payload = None
    request_body = case_data.get("request_body")
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name=(
            'api_delete_api_collections_products_records_record_id_soft_delete_a_reco'
            'rd_status_204'
        ),
        path='/api/collections/products/records/{record_id_filled_during_test}',
        method='DELETE',
        full_url=(
            'https://reqres.in/api/collections/products/records/{record_id_filled_dur'
            'ing_test}?project_id=29539'
        ),
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("DELETE", resolved_path, **request_kwargs)
        assert response.status_code == int('204')

    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)


@covers(
    type="api",
    target=(
        'GET /api/collections/products/records :: Fetch all records from Products'
        ' | status 200'
    ),
    priority="high",
    template="ApiServiceTemplate",
    page='/documentation_sources/reqres_in.html',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_get_api_collections_products_records_fetch_all_records_from_products_status_200(
    settings, reqres_http_client
):
    # Scenario: Fetch all records from Products
    # Request Parameters: project_id
    # Expected Response Code: 200
    # Expected Response Payload: see generated case data
    case_data = CASE_DATA.get('api_get_api_collections_products_records_fetch_all_records_from_products_status_200', {})
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name=(
            'api_get_api_collections_products_records_fetch_all_records_from_products'
            '_status_200'
        ),
        path='/api/collections/products/records',
        method='GET',
        full_url='https://reqres.in/api/collections/products/records?project_id=29539',
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("GET", resolved_path, **request_kwargs)
        assert response.status_code == int('200')
        payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload
    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)


@covers(
    type="api",
    target=(
        'GET /api/collections/products/records/{record_id_filled_during_test} :: '
        'Fetch a single record by ID | status 200'
    ),
    priority="high",
    template="ApiServiceTemplate",
    page='/documentation_sources/reqres_in.html',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_get_api_collections_products_records_record_id_fetch_a_single_record_by_id_status_200(
    settings, reqres_http_client
):
    # Scenario: Fetch a single record by ID
    # Request Parameters: project_id
    # Expected Response Code: 200
    # Expected Response Payload: see generated case data
    case_data = CASE_DATA.get(
        'api_get_api_collections_products_records_record_id_fetch_a_single_record_by_id_status_200', {})
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name=(
            'api_get_api_collections_products_records_record_id_fetch_a_single_record'
            '_by_id_status_200'
        ),
        path='/api/collections/products/records/{record_id_filled_during_test}',
        method='GET',
        full_url=(
            'https://reqres.in/api/collections/products/records/{record_id_filled_dur'
            'ing_test}?project_id=29539'
        ),
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("GET", resolved_path, **request_kwargs)
        assert response.status_code == int('200')
        payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload
    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)


@covers(
    type="api",
    target=(
        'POST /api/collections/products/records :: Add a new record to Products |'
        ' status 201'
    ),
    priority="high",
    template="ApiServiceTemplate",
    page='/documentation_sources/reqres_in.html',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_post_api_collections_products_records_add_a_new_record_to_products_status_201(
    settings, reqres_http_client
):
    # Scenario: Add a new record to Products
    # Request Parameters: project_id, data
    # Expected Response Code: 201
    # Expected Response Payload: see generated case data
    case_data = CASE_DATA.get('api_post_api_collections_products_records_add_a_new_record_to_products_status_201', {})
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name=(
            'api_post_api_collections_products_records_add_a_new_record_to_products_s'
            'tatus_201'
        ),
        path='/api/collections/products/records',
        method='POST',
        full_url='https://reqres.in/api/collections/products/records?project_id=29539',
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("POST", resolved_path, **request_kwargs)
        assert response.status_code == int('201')
        payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload
    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)


@covers(
    type="api",
    target=(
        'PUT /api/collections/products/records/{record_id_filled_during_test} :: '
        'Update an existing record | status 200'
    ),
    priority="high",
    template="ApiServiceTemplate",
    page='/documentation_sources/reqres_in.html',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_api_put_api_collections_products_records_record_id_update_an_existing_record_status_200(
    settings, reqres_http_client
):
    # Scenario: Update an existing record
    # Request Parameters: project_id, data
    # Expected Response Code: 200
    # Expected Response Payload: see generated case data
    case_data = CASE_DATA.get(
        'api_put_api_collections_products_records_record_id_update_an_existing_record_status_200', {})
    raw_expected_response_payload = case_data.get("response_payload", "")
    expected_response_payload = reqres_expected_payload_fragment(raw_expected_response_payload)
    request_body = case_data.get("request_body")
    resolved_path, request_kwargs, cleanup = await reqres_request_kwargs(
        reqres_http_client,
        test_name=(
            'api_put_api_collections_products_records_record_id_update_an_existing_re'
            'cord_status_200'
        ),
        path='/api/collections/products/records/{record_id_filled_during_test}',
        method='PUT',
        full_url=(
            'https://reqres.in/api/collections/products/records/{record_id_filled_dur'
            'ing_test}?project_id=29539'
        ),
        request_body=request_body,
        expected_response_payload=raw_expected_response_payload,
    )
    try:
        response = await reqres_http_client.request("PUT", resolved_path, **request_kwargs)
        assert response.status_code == int('200')
        payload = response.json() if response.content else None
        assert isinstance(payload, (dict, list))
        rendered_payload = json.dumps(payload, sort_keys=True)
        assert expected_response_payload in rendered_payload
    finally:
        await cleanup_reqres_record(reqres_http_client, cleanup)
