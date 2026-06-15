"""ReqRes website-suite fixtures."""

from collections.abc import AsyncIterator

import httpx
import pytest_asyncio

from config.settings import Settings
from tests.websites.reqres_in.suite_config import BASE_URL
from utils.test_diagnostics import TestDiagnosticRecorder, httpx_event_hooks


@pytest_asyncio.fixture
async def reqres_http_client(
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> AsyncIterator[httpx.AsyncClient]:
    headers = {"x-api-key": settings.reqres_api_key} if settings.reqres_api_key else {}
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers=headers,
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    ) as client:
        yield client
