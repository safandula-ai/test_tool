from __future__ import annotations

import os
import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from typing import AsyncContextManager

import httpx
import pytest
import pytest_asyncio
from faker import Faker
from playwright.async_api import Page, async_playwright

from config.settings import Settings, get_settings
from utils.api_mocks import build_transport
from utils.allure_report import generate_allure_report
from utils.logging import get_logger, start_test_log_capture, stop_test_log_capture
from utils.smoke_diagnostics import sanitize_headers
from utils.test_diagnostics import (
    TestDiagnosticRecorder,
    append_report_diagnostics,
    emit_test_diagnostics,
    httpx_event_hooks,
    render_test_diagnostics,
)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register runtime target overrides for generic website suites."""
    parser.addoption(
        "--target-url",
        action="store",
        default=None,
        help="Override BASE_URL for smoke, performance, and generated website tests",
    )
    parser.addoption(
        "--no-allure-report",
        action="store_true",
        help="Collect Allure results but skip automatic HTML report generation",
    )
    parser.addoption(
        "--allure-report-dir",
        dest="generated_allure_report_dir",
        default="allure-report",
        help="Archive directory for timestamped Allure HTML reports and history",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose shared runtime settings to tests."""
    return get_settings()


@pytest.fixture(scope="session")
def target_url(pytestconfig: pytest.Config, settings: Settings) -> str:
    """Resolve a terminal URL override, falling back to BASE_URL."""
    value = pytestconfig.getoption("--target-url") or settings.base_url
    return value.rstrip("/")


@pytest.fixture(scope="session")
def live_target_enabled(pytestconfig: pytest.Config, settings: Settings) -> bool:
    """Allow explicit terminal targets even when global live tests are disabled."""
    return settings.run_live_tests or bool(pytestconfig.getoption("--target-url"))


@pytest.fixture
def require_live_target_enabled(live_target_enabled: bool) -> None:
    """Skip tests that require a live target unless one is explicitly enabled."""
    if not live_target_enabled:
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")


@pytest.fixture(autouse=True)
def test_diagnostics(request: pytest.FixtureRequest) -> Iterator[TestDiagnosticRecorder]:
    """Create a recorder for every test, including unit and skipped tests."""
    recorder = TestDiagnosticRecorder(request.node.nodeid)
    setattr(request.node, "diagnostic_recorder", recorder)
    log_buffer, log_token = start_test_log_capture()
    setattr(request.node, "diagnostic_log_buffer", log_buffer)
    try:
        yield recorder
    finally:
        recorder.log_lines.extend(log_buffer)
        stop_test_log_capture(log_token)
    emit_test_diagnostics(request.config, request.node, recorder)


@pytest.fixture(scope="session")
def fake() -> Faker:
    """Expose a reusable Faker instance."""
    return Faker()


@pytest.fixture(scope="session", autouse=True)
def logger(settings: Settings):
    """Expose the configured project logger."""
    return get_logger(settings.log_level)


@pytest_asyncio.fixture
async def api_client(
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async HTTP client bound to the API base URL."""
    transport = build_transport()
    client = httpx.AsyncClient(
        base_url=settings.api_base_url,
        transport=transport,
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def reqres_http_client(
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> AsyncIterator[httpx.AsyncClient]:
    """Provide an authenticated client for opt-in live ReqRes tests."""
    headers = {"x-api-key": settings.reqres_api_key} if settings.reqres_api_key else {}
    client = httpx.AsyncClient(
        base_url=settings.reqres_base_url,
        headers=headers,
        timeout=settings.http_timeout,
        event_hooks=httpx_event_hooks(test_diagnostics),
    )
    yield client
    await client.aclose()


@pytest.fixture
def page_factory(
    request: pytest.FixtureRequest,
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> Callable[[str | None], AsyncContextManager[Page]]:
    """Build isolated async Playwright pages without async pytest fixtures."""

    @asynccontextmanager
    async def create_page(base_url: str | None = None) -> AsyncIterator[Page]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=settings.headless,
                slow_mo=settings.slow_mo,
            )
            context = await browser.new_context(
                base_url=base_url or settings.base_url,
                record_video_dir=str(settings.video_dir) if settings.video_on_failure else None,
            )
            if settings.trace_on_failure:
                await context.tracing.start(screenshots=True, snapshots=True, sources=True)

            page = await context.new_page()
            test_diagnostics.record(
                "browser_page_opened",
                base_url=base_url or settings.base_url,
                initial_url=page.url,
            )
            pending_diagnostics: set[asyncio.Task[None]] = set()

            async def record_response(response) -> None:
                if response.request.resource_type not in {"document", "xhr", "fetch"}:
                    return
                test_diagnostics.record(
                    "browser_response",
                    resource_type=response.request.resource_type,
                    method=response.request.method,
                    url=response.url,
                    status=response.status,
                    response_headers=sanitize_headers(await response.all_headers()),
                )

            def schedule_response(response) -> None:
                task = asyncio.create_task(record_response(response))
                pending_diagnostics.add(task)
                task.add_done_callback(pending_diagnostics.discard)

            page.on("response", schedule_response)
            page.on(
                "requestfailed",
                lambda failed_request: test_diagnostics.record(
                    "browser_request_failed",
                    method=failed_request.method,
                    url=failed_request.url,
                    failure=failed_request.failure,
                ),
            )
            page.on(
                "console",
                lambda message: test_diagnostics.record(
                    "browser_console",
                    level=message.type,
                    text=message.text,
                )
                if message.type in {"error", "warning"}
                else None,
            )
            page.on(
                "pageerror",
                lambda error: test_diagnostics.record(
                    "browser_page_error",
                    message=str(error),
                ),
            )
            try:
                yield page
            finally:
                if pending_diagnostics:
                    await asyncio.gather(*pending_diagnostics, return_exceptions=True)
                try:
                    final_title = await page.title()
                except Exception:
                    final_title = "<unavailable>"
                test_diagnostics.record(
                    "browser_page_final_state",
                    url=page.url,
                    title=final_title,
                )
                failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
                if failed and settings.screenshot_on_failure:
                    await page.screenshot(path=str(settings.screenshot_dir / f"{request.node.name}.png"), full_page=True)
                if settings.trace_on_failure:
                    if failed:
                        await context.tracing.stop(path=str(settings.artifact_dir / f"{request.node.name}.zip"))
                    else:
                        await context.tracing.stop()
                await context.close()
                await browser.close()

    return create_page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach test phase results to the item for fixture cleanup hooks."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    recorder = getattr(item, "diagnostic_recorder", None)
    if recorder is None:
        return
    log_buffer = getattr(item, "diagnostic_log_buffer", [])
    if report.when == "call":
        rendered = render_test_diagnostics(item, recorder)
        append_report_diagnostics(report, rendered, list(log_buffer))
    elif report.when == "setup" and report.failed:
        rendered = render_test_diagnostics(item, recorder)
        append_report_diagnostics(report, rendered, list(log_buffer))


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate the persistent Allure report after result writers finish."""
    if session.config.getoption("--no-allure-report"):
        return

    results_dir = session.config.getoption("allure_report_dir") or "allure-results"
    report_dir = session.config.getoption("generated_allure_report_dir")
    result = generate_allure_report(results_dir, report_dir)
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        prefix = "ALLURE" if result.succeeded else "ALLURE WARNING"
        terminal.write_line(f"{prefix}: {result.message}")

    required = os.getenv("ALLURE_REPORT_REQUIRED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if required and not result.succeeded and exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
