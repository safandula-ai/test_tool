"""ReqRes website-suite fixtures."""

from collections.abc import AsyncIterator, Callable
from typing import AsyncContextManager

import httpx
import pytest_asyncio

from config.settings import Settings
from tests.websites.reqres_in.suite_config import BASE_URL, REQRES_ENV_HEADER


@pytest_asyncio.fixture
async def reqres_http_client(
    settings: Settings,
    http_client_factory: Callable[..., AsyncContextManager[httpx.AsyncClient]],
) -> AsyncIterator[httpx.AsyncClient]:
    headers: dict[str, str] = {"X-Reqres-Env": REQRES_ENV_HEADER}
    if settings.reqres_api_key:
        headers["x-api-key"] = settings.reqres_api_key
    async with http_client_factory(
        base_url=BASE_URL,
        headers=headers,
    ) as client:
        yield client
