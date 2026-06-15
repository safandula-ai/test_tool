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


def _identifier(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "target"


def load_gap_cases(report_path: str | Path) -> tuple[str, str | None, list[GapCase]]:
    """Load UI and API gap cases from a gap report."""
    with Path(report_path).open(encoding="utf-8") as file:
        report = json.load(file)
    page = report.get("page", "unknown")
    gaps = report.get("gaps", {})
    cases = [
        GapCase(
            item["testid"],
            "ui",
            item["suggested_blueprint"],
            item.get("presence", "deterministic"),
        )
        for item in gaps.get("missing_ui_testids", [])
    ]
    cases.extend(
        GapCase(
            item["endpoint"],
            "api",
            item["suggested_blueprint"],
            item.get("presence", "deterministic"),
        )
        for item in gaps.get("missing_api_endpoints", [])
    )
    return page, report.get("base_url"), cases


def _ui_assertion(template: str) -> str:
    if template in {"InputValidationTemplate", "FormValidationTemplate"}:
        return "await _assert_input_validation(target)"
    if template == "InteractionTemplate":
        return "await _assert_interaction(target)"
    return "await expect(target).to_be_visible()"


def render_gap_tests(
    page: str,
    cases: list[GapCase],
    *,
    base_url: str | None = None,
    base_url_setting: str = "base_url",
    feature: str = "feature:generated-gap-coverage",
) -> str:
    """Render a deterministic generated pytest module."""
    header = f'''"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers


DEFAULT_BASE_URL = {base_url!r}

pytestmark = [
    pytest.mark.ui,
    pytest.mark.asyncio,
]


def _target(page, name: str):
    escaped = name.replace('"', '\\"')
    return page.locator(
        f'[data-testid="{{escaped}}"], [data-test="{{escaped}}"], [data-qa="{{escaped}}"]'
    ).first


async def _assert_input_validation(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_editable()
    input_type = (await target.get_attribute("type") or "text").lower()
    await target.fill("not-a-valid-value")
    if input_type in {{"email", "url", "number"}}:
        assert not await target.evaluate("element => element.checkValidity()")
    else:
        assert await target.input_value() == "not-a-valid-value"


async def _assert_interaction(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_enabled()
'''
    functions: list[str] = []
    for case in sorted(cases, key=lambda item: (item.coverage_type, item.target)):
        name = f"{case.coverage_type}_{_identifier(case.target)}"
        target_literal = json.dumps(case.target)
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
        target = _target(browser_page, {target_literal})
        {_ui_assertion(case.template)}
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
    destination.write_text(
        render_gap_tests(
            page,
            cases,
            base_url=base_url,
            base_url_setting=base_url_setting,
            feature=feature,
        ),
        encoding="utf-8",
    )
    return len(cases)
