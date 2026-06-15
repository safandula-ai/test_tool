"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import pytest
import httpx
import json

from utils.test_diagnostics import httpx_event_hooks

from ._test_generated_coverage_gaps_helpers import (
    automationexercise_request_kwargs,
    cleanup_generated_account,
)

from coverage_agent.decorators import covers


DEFAULT_BASE_URL = 'https://automationexercise.com'

pytestmark = [
    pytest.mark.api,
    pytest.mark.asyncio,
]

@covers(type="api", target="DELETE /api/deleteAccount :: DELETE METHOD To Delete User Account | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_delete_api_deleteaccount_delete_method_to_delete_user_account_status_200(settings, test_diagnostics):
    # Scenario: DELETE METHOD To Delete User Account
    # Request Parameters: email, password
    # Expected Response Code: 200
    # Expected Response Message: Account deleted!
    url = f"{DEFAULT_BASE_URL}/api/deleteAccount"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_delete_api_deleteaccount_delete_method_to_delete_user_account_status_200',
            path='/api/deleteAccount',
            method='DELETE',
            scenario='DELETE METHOD To Delete User Account',
            request_parameters='email, password',
        )
        try:
            response = await live_client.request("DELETE", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'Account deleted!'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="DELETE /api/verifyLogin :: DELETE To Verify Login | status 405", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_delete_api_verifylogin_delete_to_verify_login_status_405(settings, test_diagnostics):
    # Scenario: DELETE To Verify Login
    # Expected Response Code: 405
    # Expected Response Message: This request method is not supported.
    url = f"{DEFAULT_BASE_URL}/api/verifyLogin"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_delete_api_verifylogin_delete_to_verify_login_status_405',
            path='/api/verifyLogin',
            method='DELETE',
            scenario='DELETE To Verify Login',
            request_parameters=None,
        )
        try:
            response = await live_client.request("DELETE", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('405')
                assert response_payload["message"] == 'This request method is not supported.'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="GET /api/brandsList :: Get All Brands List | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_get_api_brandslist_get_all_brands_list_status_200(settings, test_diagnostics):
    # Scenario: Get All Brands List
    # Expected Response Code: 200
    # Expected Response Message: All brands list
    url = f"{DEFAULT_BASE_URL}/api/brandsList"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_get_api_brandslist_get_all_brands_list_status_200',
            path='/api/brandsList',
            method='GET',
            scenario='Get All Brands List',
            request_parameters=None,
        )
        try:
            response = await live_client.request("GET", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'json' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'All brands list'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="GET /api/getUserDetailByEmail :: GET user account detail by email | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_get_api_getuserdetailbyemail_get_user_account_detail_by_email_status_200(settings, test_diagnostics):
    # Scenario: GET user account detail by email
    # Request Parameters: email
    # Expected Response Code: 200
    # Expected Response Message: User Detail
    url = f"{DEFAULT_BASE_URL}/api/getUserDetailByEmail"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_get_api_getuserdetailbyemail_get_user_account_detail_by_email_status_200',
            path='/api/getUserDetailByEmail',
            method='GET',
            scenario='GET user account detail by email',
            request_parameters='email',
        )
        try:
            response = await live_client.request("GET", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'json' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'User Detail'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="GET /api/productsList :: Get All Products List | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_get_api_productslist_get_all_products_list_status_200(settings, test_diagnostics):
    # Scenario: Get All Products List
    # Expected Response Code: 200
    # Expected Response Message: All products list
    url = f"{DEFAULT_BASE_URL}/api/productsList"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_get_api_productslist_get_all_products_list_status_200',
            path='/api/productsList',
            method='GET',
            scenario='Get All Products List',
            request_parameters=None,
        )
        try:
            response = await live_client.request("GET", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'json' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'All products list'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/createAccount :: POST To Create/Register User Account | status 201", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_createaccount_post_to_create_register_user_account_status_201(settings, test_diagnostics):
    # Scenario: POST To Create/Register User Account
    # Request Parameters: name, email, password, title (for example: Mr, Mrs, Miss), birth_date, birth_month, birth_year, firstname, lastname, company, address1, address2, country, zipcode, state, city, mobile_number
    # Expected Response Code: 201
    # Expected Response Message: User created!
    url = f"{DEFAULT_BASE_URL}/api/createAccount"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_createaccount_post_to_create_register_user_account_status_201',
            path='/api/createAccount',
            method='POST',
            scenario='POST To Create/Register User Account',
            request_parameters='name, email, password, title (for example: Mr, Mrs, Miss), birth_date, birth_month, birth_year, firstname, lastname, company, address1, address2, country, zipcode, state, city, mobile_number',
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('201')
                assert response_payload["message"] == 'User created!'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/productsList :: POST To All Products List | status 405", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_productslist_post_to_all_products_list_status_405(settings, test_diagnostics):
    # Scenario: POST To All Products List
    # Expected Response Code: 405
    # Expected Response Message: This request method is not supported.
    url = f"{DEFAULT_BASE_URL}/api/productsList"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_productslist_post_to_all_products_list_status_405',
            path='/api/productsList',
            method='POST',
            scenario='POST To All Products List',
            request_parameters=None,
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('405')
                assert response_payload["message"] == 'This request method is not supported.'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/searchProduct :: POST To Search Product without search_product parameter | status 400", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_searchproduct_post_to_search_product_without_search_product_parameter_status_400(settings, test_diagnostics):
    # Scenario: POST To Search Product without search_product parameter
    # Expected Response Code: 400
    # Expected Response Message: Bad request, search_product parameter is missing in POST request.
    url = f"{DEFAULT_BASE_URL}/api/searchProduct"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_searchproduct_post_to_search_product_without_search_product_parameter_status_400',
            path='/api/searchProduct',
            method='POST',
            scenario='POST To Search Product without search_product parameter',
            request_parameters=None,
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('400')
                assert response_payload["message"] == 'Bad request, search_product parameter is missing in POST request.'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/searchProduct :: POST To Search Product | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_searchproduct_post_to_search_product_status_200(settings, test_diagnostics):
    # Scenario: POST To Search Product
    # Request Parameters: search_product (For example: top, tshirt, jean)
    # Expected Response Code: 200
    # Expected Response Message: Searched products list
    url = f"{DEFAULT_BASE_URL}/api/searchProduct"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_searchproduct_post_to_search_product_status_200',
            path='/api/searchProduct',
            method='POST',
            scenario='POST To Search Product',
            request_parameters='search_product (For example: top, tshirt, jean)',
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'json' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'Searched products list'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/verifyLogin :: POST To Verify Login with invalid details | status 404", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_verifylogin_post_to_verify_login_with_invalid_details_status_404(settings, test_diagnostics):
    # Scenario: POST To Verify Login with invalid details
    # Request Parameters: email, password (invalid values)
    # Expected Response Code: 404
    # Expected Response Message: User not found!
    url = f"{DEFAULT_BASE_URL}/api/verifyLogin"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_verifylogin_post_to_verify_login_with_invalid_details_status_404',
            path='/api/verifyLogin',
            method='POST',
            scenario='POST To Verify Login with invalid details',
            request_parameters='email, password (invalid values)',
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('404')
                assert response_payload["message"] == 'User not found!'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/verifyLogin :: POST To Verify Login with valid details | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_verifylogin_post_to_verify_login_with_valid_details_status_200(settings, test_diagnostics):
    # Scenario: POST To Verify Login with valid details
    # Request Parameters: email, password
    # Expected Response Code: 200
    # Expected Response Message: User exists!
    url = f"{DEFAULT_BASE_URL}/api/verifyLogin"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_verifylogin_post_to_verify_login_with_valid_details_status_200',
            path='/api/verifyLogin',
            method='POST',
            scenario='POST To Verify Login with valid details',
            request_parameters='email, password',
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'User exists!'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="POST /api/verifyLogin :: POST To Verify Login without email parameter | status 400", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_post_api_verifylogin_post_to_verify_login_without_email_parameter_status_400(settings, test_diagnostics):
    # Scenario: POST To Verify Login without email parameter
    # Request Parameters: password
    # Expected Response Code: 400
    # Expected Response Message: Bad request, email or password parameter is missing in POST request.
    url = f"{DEFAULT_BASE_URL}/api/verifyLogin"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_post_api_verifylogin_post_to_verify_login_without_email_parameter_status_400',
            path='/api/verifyLogin',
            method='POST',
            scenario='POST To Verify Login without email parameter',
            request_parameters='password',
        )
        try:
            response = await live_client.request("POST", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('400')
                assert response_payload["message"] == 'Bad request, email or password parameter is missing in POST request.'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="PUT /api/brandsList :: PUT To All Brands List | status 405", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_put_api_brandslist_put_to_all_brands_list_status_405(settings, test_diagnostics):
    # Scenario: PUT To All Brands List
    # Expected Response Code: 405
    # Expected Response Message: This request method is not supported.
    url = f"{DEFAULT_BASE_URL}/api/brandsList"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_put_api_brandslist_put_to_all_brands_list_status_405',
            path='/api/brandsList',
            method='PUT',
            scenario='PUT To All Brands List',
            request_parameters=None,
        )
        try:
            response = await live_client.request("PUT", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('405')
                assert response_payload["message"] == 'This request method is not supported.'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)



@covers(type="api", target="PUT /api/updateAccount :: PUT METHOD To Update User Account | status 200", priority="high", template="ApiServiceTemplate", page='/api_list', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_api_put_api_updateaccount_put_method_to_update_user_account_status_200(settings, test_diagnostics):
    # Scenario: PUT METHOD To Update User Account
    # Request Parameters: name, email, password, title (for example: Mr, Mrs, Miss), birth_date, birth_month, birth_year, firstname, lastname, company, address1, address2, country, zipcode, state, city, mobile_number
    # Expected Response Code: 200
    # Expected Response Message: User updated!
    url = f"{DEFAULT_BASE_URL}/api/updateAccount"
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as live_client:
        request_kwargs, cleanup_payload = await automationexercise_request_kwargs(
            live_client,
            base_url=DEFAULT_BASE_URL,
            test_name='api_put_api_updateaccount_put_method_to_update_user_account_status_200',
            path='/api/updateAccount',
            method='PUT',
            scenario='PUT METHOD To Update User Account',
            request_parameters='name, email, password, title (for example: Mr, Mrs, Miss), birth_date, birth_month, birth_year, firstname, lastname, company, address1, address2, country, zipcode, state, city, mobile_number',
        )
        try:
            response = await live_client.request("PUT", url, **request_kwargs)
            assert response.status_code == 200
            response_payload = response.json()
            if 'message' == "json":
                assert isinstance(response_payload, (dict, list))
            else:
                assert response_payload["responseCode"] == int('200')
                assert response_payload["message"] == 'User updated!'
        finally:
            await cleanup_generated_account(live_client, DEFAULT_BASE_URL, cleanup_payload)


