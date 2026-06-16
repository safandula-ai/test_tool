from __future__ import annotations

import os
import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncContextManager

import httpx
import pytest
import pytest_asyncio
from faker import Faker
from playwright.async_api import Page, async_playwright
from playwright_stealth import Stealth

from config.settings import Settings, get_settings
from utils.api_mocks import build_transport
from utils.logging import get_logger, start_test_log_capture, stop_test_log_capture
from utils.pytest_html_report import (
    PytestHtmlReportResult,
    prepare_pytest_html_report,
)
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
        "--no-html-report",
        action="store_true",
        help="Skip automatic pytest-html report generation",
    )
    parser.addoption(
        "--html-report-dir",
        dest="generated_html_report_dir",
        default="reports/pytest-html",
        help="Archive directory for timestamped pytest-html reports",
    )
    parser.addoption(
        "--html-report-name",
        dest="generated_html_report_name",
        default=None,
        help="Optional file name prefix for the generated pytest-html report",
    )


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose shared runtime settings to tests."""
    return get_settings()


def _html_report_required() -> bool:
    """Return whether missing pytest-html output should fail the session."""
    return os.getenv("HTML_REPORT_REQUIRED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def pytest_configure(config: pytest.Config) -> None:
    """Configure a timestamped self-contained pytest-html report when available."""
    if config.getoption("--no-html-report"):
        result = PytestHtmlReportResult(
            "disabled",
            "pytest-html report generation disabled by --no-html-report.",
        )
    elif not config.pluginmanager.hasplugin("html"):
        result = PytestHtmlReportResult(
            "plugin_missing",
            "pytest-html plugin is not installed; HTML report was not generated.",
        )
    else:
        htmlpath = getattr(config.option, "htmlpath", None)
        if htmlpath:
            result = PytestHtmlReportResult(
                "configured",
                f"pytest-html report will be written to {htmlpath}.",
                report_path=Path(htmlpath).resolve(),
            )
        else:
            result = prepare_pytest_html_report(
                config.getoption("generated_html_report_dir"),
                report_name=config.getoption("generated_html_report_name"),
            )
            config.option.htmlpath = str(result.report_path)
        config.option.self_contained_html = True
    setattr(config, "_pytest_html_report_result", result)


@pytest.fixture(scope="session")
def target_url(pytestconfig: pytest.Config, settings: Settings) -> str:
    """Resolve a terminal URL override, falling back to BASE_URL."""
    value = pytestconfig.getoption("--target-url") or settings.base_url
    return value.rstrip("/")


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


@pytest.fixture
def http_client_factory(
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> Callable[..., AsyncContextManager[httpx.AsyncClient]]:
    """Build instrumented async HTTP clients with per-test diagnostics."""

    @asynccontextmanager
    async def create_client(
        *,
        base_url: str,
        headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        follow_redirects: bool = False,
    ) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            transport=transport,
            timeout=settings.http_timeout,
            follow_redirects=follow_redirects,
            event_hooks=httpx_event_hooks(test_diagnostics),
        ) as client:
            yield client

    return create_client


@pytest_asyncio.fixture
async def api_client(
    settings: Settings,
    http_client_factory: Callable[..., AsyncContextManager[httpx.AsyncClient]],
) -> AsyncIterator[httpx.AsyncClient]:
    """Provide an async HTTP client bound to the API base URL."""
    async with http_client_factory(
        base_url=settings.api_base_url,
        transport=build_transport(),
    ) as client:
        yield client


@pytest.fixture
def page_factory(
    request: pytest.FixtureRequest,
    settings: Settings,
    test_diagnostics: TestDiagnosticRecorder,
) -> Callable[..., AsyncContextManager[Page]]:
    """Build isolated async Playwright pages without async pytest fixtures."""

    @asynccontextmanager
    async def create_page(
        base_url: str | None = None,
        *,
        viewport: dict[str, int] | None = None,
        is_mobile: bool | None = None,
        has_touch: bool | None = None,
        user_agent: str | None = None,
    ) -> AsyncIterator[Page]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=settings.headless,
                slow_mo=settings.slow_mo,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context_options: dict[str, object] = {
                "base_url": base_url or settings.base_url,
                "locale": "en-US",
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                ),
                "viewport": {"width": 1280, "height": 720},
                "color_scheme": "light",
                "extra_http_headers": {"Accept-Language": "en-US,en;q=0.9"},
                "record_video_dir": str(settings.video_dir) if settings.video_on_failure else None,
            }
            if viewport is not None:
                context_options["viewport"] = viewport
            if is_mobile is not None:
                context_options["is_mobile"] = is_mobile
            if has_touch is not None:
                context_options["has_touch"] = has_touch
            if user_agent is not None:
                context_options["user_agent"] = user_agent
            context = await browser.new_context(**context_options)
            await Stealth().apply_stealth_async(context)
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
                    await page.screenshot(
                        path=str(
                            settings.screenshot_dir / f"{request.node.name}.png"
                        ),
                        full_page=True,
                    )
                if settings.trace_on_failure:
                    if failed:
                        await context.tracing.stop(
                            path=str(
                                settings.artifact_dir / f"{request.node.name}.zip"
                            )
                        )
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
    """Report the configured pytest-html output and optionally require it."""
    result = getattr(
        session.config,
        "_pytest_html_report_result",
        PytestHtmlReportResult("unknown", "pytest-html report status is unavailable."),
    )
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        prefix = "HTML" if result.succeeded else "HTML WARNING"
        terminal.write_line(f"{prefix}: {result.message}")

    required = _html_report_required()
    if required and not result.succeeded and exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
