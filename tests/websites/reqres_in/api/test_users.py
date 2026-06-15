"""ReqRes user API contract tests."""

import pytest

from api_clients.reqres_client import ReqResClient
from config.settings import get_settings
from coverage_agent.decorators import covers


@pytest.mark.api
@pytest.mark.asyncio
@covers(type="api", target="GET /api/users", priority="high", template="APIContractTemplate")
async def test_reqres_client_collects_and_validates_all_user_pages(api_client):
    users = await ReqResClient(api_client).get_all_users()
    assert [user["id"] for user in users] == [1, 2]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not (get_settings().run_live_tests and get_settings().reqres_api_key),
    reason="Set RUN_LIVE_TESTS=true and REQRES_API_KEY to call ReqRes",
)
@covers(type="api", target="GET /api/users", priority="high", template="APIContractTemplate")
async def test_live_reqres_users_follow_pagination(reqres_http_client):
    users = await ReqResClient(reqres_http_client).get_all_users()
    assert users
    assert len({user["id"] for user in users}) == len(users)
