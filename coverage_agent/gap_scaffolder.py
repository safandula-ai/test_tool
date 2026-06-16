"""Generate executable pytest coverage from machine-readable gap reports."""

from __future__ import annotations

import json
from pathlib import Path

from coverage_agent.gap_scaffolder_api import (
    automationexercise_helper_imports,
    render_api_test_function,
    render_automationexercise_helper_lines,
    render_data_loader_lines,
    render_reqres_helper_lines,
    reqres_helper_imports,
)
from coverage_agent.gap_scaffolder_common import (
    GapCase,
    SUPPORTED_UI_TEMPLATES,
    build_case_data_payload,
    data_file_name,
    format_generated_python,
    helper_module_name,
    identifier,
    is_automationexercise,
    is_reqres,
    load_gap_cases,
    render_covers_decorator,
    reqres_placeholder_target,
    website_suite_name_for_output,
)
from coverage_agent.gap_scaffolder_ui import (
    is_mobile_ui_case,
    omit_ui_case,
    render_generated_target_fixture,
    render_ui_helper_lines,
    render_ui_module_support,
    render_ui_test_function,
    ui_helper_imports,
)


def _render_helper_module(
    *,
    include_ui_helpers: bool,
    include_automationexercise_helpers: bool,
    include_reqres_helpers: bool,
    include_data_loader: bool,
) -> str:
    """Build the helper module source for the selected UI/API generated suite."""
    if (
        not include_ui_helpers
        and not include_automationexercise_helpers
        and not include_reqres_helpers
        and not include_data_loader
    ):
        return ""

    lines = [
        '"""Helper functions for generated coverage tests."""',
        "",
        "from __future__ import annotations",
        "",
    ]

    if include_data_loader or include_reqres_helpers:
        lines.extend(
            [
                "import json",
                "from pathlib import Path",
                "",
            ]
        )

    if include_automationexercise_helpers:
        lines.extend(
            [
                "import httpx",
                "from uuid import uuid4",
                "",
                "from api_clients.automation_exercise_client import build_account_payload",
                "",
            ]
        )
    elif include_reqres_helpers:
        lines.extend(
            [
                "from urllib.parse import parse_qsl, urlsplit",
                "",
            ]
        )

    if include_ui_helpers:
        lines.extend(
            [
                "import pytest",
                "",
                "from playwright.async_api import expect",
                "",
            ]
        )
        lines.extend(render_ui_helper_lines())

    if include_automationexercise_helpers:
        lines.extend(render_automationexercise_helper_lines())

    if include_reqres_helpers:
        lines.extend(render_reqres_helper_lines())

    if include_data_loader:
        lines.extend(render_data_loader_lines())

    return "\n".join(lines)


def render_gap_tests(
    page: str,
    cases: list[GapCase],
    *,
    base_url: str | None = None,
    website_suite_name: str | None = None,
    base_url_setting: str = "base_url",
    feature: str = "feature:generated-gap-coverage",
    helper_module_stem: str | None = None,
    data_file_name: str | None = None,
) -> str:
    """Render a deterministic generated pytest module."""
    del base_url_setting

    has_api_cases = any(case.coverage_type == "api" for case in cases)
    automationexercise = is_automationexercise(base_url) and has_api_cases
    reqres = is_reqres(base_url) and has_api_cases
    include_ui_helpers = any(case.coverage_type == "ui" for case in cases)
    generic_api = any(
        case.coverage_type == "api"
        and not automationexercise
        and not reqres
        for case in cases
    )
    needs_json_import = reqres or generic_api

    helper_imports: list[str] = []
    if include_ui_helpers:
        helper_imports.extend(ui_helper_imports(cases))
    if automationexercise:
        helper_imports.extend(automationexercise_helper_imports())
    if reqres:
        helper_imports.extend(reqres_helper_imports())
    elif data_file_name and helper_module_stem:
        helper_imports.append("load_generated_case_data")

    header_lines = [
        '"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""',
        "",
        "from __future__ import annotations",
        "",
    ]
    if needs_json_import:
        header_lines.append("import json")
    if automationexercise:
        header_lines.append("import httpx")
    header_lines.append("import pytest")
    header_lines.append("")
    if reqres and has_api_cases:
        header_lines.extend(
            [
                "from config.settings import get_settings",
                "",
            ]
        )
    if automationexercise:
        header_lines.extend(
            [
                "from utils.test_diagnostics import httpx_event_hooks",
                "",
            ]
        )
    if website_suite_name:
        suite_config_imports = ["BASE_URL"]
        if any(case.coverage_type == "ui" and is_mobile_ui_case(case) for case in cases):
            suite_config_imports.extend(["MOBILE_USER_AGENT", "MOBILE_VIEWPORT"])
        header_lines.extend(
            [
                "from tests.websites.helpers import require_live_target, resolve_target_url",
                (
                    f"from tests.websites.{website_suite_name}.suite_config import "
                    + ", ".join(suite_config_imports)
                ),
                "",
            ]
        )
    if helper_imports and helper_module_stem:
        header_lines.extend(
            [
                f"from .{helper_module_stem} import (",
                *[f"    {name}," for name in helper_imports],
                ")",
                "",
            ]
        )
    header_lines.extend(
        [
            "from coverage_agent.decorators import covers",
            "",
        ]
    )
    if not website_suite_name:
        header_lines.extend(
            [
                f"DEFAULT_BASE_URL = {base_url!r}",
                "",
            ]
        )
    if reqres and has_api_cases:
        header_lines.extend(
            [
                "_SETTINGS = get_settings()",
                "",
            ]
        )
    if data_file_name:
        header_lines.extend(
            [
                f"CASE_DATA = load_generated_case_data(__file__, {data_file_name!r})",
                "",
            ]
        )
    if include_ui_helpers:
        header_lines.extend(
            render_ui_module_support(
                website_suite_name=website_suite_name,
                data_file_name=data_file_name,
            )
        )
    if include_ui_helpers and not website_suite_name:
        header_lines.extend(render_generated_target_fixture(base_url))

    header_lines.extend(
        [
            "pytestmark = [",
            "    pytest.mark.asyncio,",
        ]
    )
    if include_ui_helpers:
        header_lines.append("    pytest.mark.ui,")
    if has_api_cases:
        header_lines.append("    pytest.mark.api,")
    if reqres and has_api_cases:
        header_lines.extend(
            [
                "    pytest.mark.skipif(",
                "        not _SETTINGS.reqres_api_key,",
                '        reason="Set REQRES_API_KEY for ReqRes generated API coverage",',
                "    ),",
            ]
        )
    header_lines.append("]")
    header = "\n".join(header_lines)

    functions: list[str] = []
    for case in sorted(cases, key=lambda item: (item.coverage_type, item.target)):
        if case.coverage_type == "ui" and omit_ui_case(case):
            continue

        rendered_target = reqres_placeholder_target(case.target) if reqres else case.target
        decorator = render_covers_decorator(
            coverage_type=case.coverage_type,
            target=rendered_target,
            template=case.template,
            page=page,
            feature=feature,
            presence=case.presence,
        )

        if case.coverage_type == "ui" and case.template in SUPPORTED_UI_TEMPLATES:
            functions.append(
                render_ui_test_function(
                    case=case,
                    decorator=decorator,
                    page=page,
                    rendered_target=rendered_target,
                    website_suite_name=website_suite_name,
                )
            )
        elif case.coverage_type == "api":
            functions.append(
                render_api_test_function(
                    case=case,
                    decorator=decorator,
                    base_url=base_url,
                    website_suite_name=website_suite_name,
                    reqres=reqres,
                    automationexercise=automationexercise,
                )
            )
        else:
            name = f"{case.coverage_type}_{identifier(case.target)}"
            functions.append(
                f'''\n# TODO: Implement domain-specific coverage before adding this decorator:
# {decorator}
async def todo_generated_{name}():
    raise NotImplementedError("Add status, schema, and business outcome assertions")
'''
            )

    return header + "\n\n".join(functions) + "\n"


def scaffold_gap_tests(
    report_path: str | Path,
    output_path: str | Path,
    *,
    base_url_setting: str = "base_url",
    feature: str = "feature:generated-gap-coverage",
) -> int:
    """Generate pytest modules and return the number of scaffolded gaps."""
    page, base_url, cases = load_gap_cases(report_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    website_suite_name = website_suite_name_for_output(destination)

    ui_cases = [
        case
        for case in cases
        if case.coverage_type == "ui" and not omit_ui_case(case)
    ]
    api_cases = [case for case in cases if case.coverage_type == "api"]
    output_stem = destination.stem.removesuffix("_ui").removesuffix("_api")
    base_destination = destination.with_name(f"{output_stem}.py")
    output_specs = [
        ("ui", ui_cases, destination.with_name(f"{output_stem}_ui.py")),
        ("api", api_cases, destination.with_name(f"{output_stem}_api.py")),
    ]

    for coverage_type, selected_cases, module_destination in output_specs:
        if not selected_cases:
            continue
        helper_filename = helper_module_name(module_destination)
        data_filename = data_file_name(module_destination)
        helper_stem = Path(helper_filename).stem
        data_payload = build_case_data_payload(coverage_type, selected_cases)

        helper_source = _render_helper_module(
            include_ui_helpers=coverage_type == "ui",
            include_automationexercise_helpers=(
                coverage_type == "api" and is_automationexercise(base_url)
            ),
            include_reqres_helpers=coverage_type == "api" and is_reqres(base_url),
            include_data_loader=bool(data_payload),
        )
        rendered_source = render_gap_tests(
            page,
            selected_cases,
            base_url=base_url,
            website_suite_name=website_suite_name,
            base_url_setting=base_url_setting,
            feature=feature,
            helper_module_stem=helper_stem if helper_source else None,
            data_file_name=data_filename if data_payload and helper_source else None,
        )
        module_destination.write_text(
            format_generated_python(rendered_source),
            encoding="utf-8",
        )
        if helper_source:
            (module_destination.parent / helper_filename).write_text(
                format_generated_python(helper_source),
                encoding="utf-8",
            )
        if data_payload:
            (module_destination.parent / data_filename).write_text(
                json.dumps(data_payload, indent=2) + "\n",
                encoding="utf-8",
            )

    stale_artifacts = [
        base_destination,
        base_destination.parent / helper_module_name(base_destination),
        base_destination.parent / data_file_name(base_destination),
    ]
    for artifact in stale_artifacts:
        if artifact.exists():
            artifact.unlink()
    return len(ui_cases) + len(api_cases)
