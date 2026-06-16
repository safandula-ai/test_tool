"""Shared scaffolding data structures and formatting helpers."""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import autopep8


SUPPORTED_UI_TEMPLATES = {
    "ComponentVisibilityTemplate",
    "FormValidationTemplate",
    "InputValidationTemplate",
    "InteractionTemplate",
}

TEXT_ASSERTION_TAGS = {
    "a",
    "button",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "label",
    "p",
    "span",
}

TEXT_ASSERTION_MAX_LENGTH = 160

STRUCTURAL_ASSERTION_TAGS = {
    "blockquote",
    "div",
    "footer",
    "nav",
    "ol",
    "picture",
    "section",
    "ul",
}


@dataclass(frozen=True)
class GapCase:
    """Normalized UI or API gap entry loaded from a gap report."""

    target: str
    coverage_type: str
    template: str
    presence: str = "deterministic"
    api_details: dict[str, Any] | None = None
    ui_details: dict[str, Any] | None = None


def identifier(value: str) -> str:
    """Convert a human target string into a stable Python/test identifier."""
    sanitized = re.sub(
        r"\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "record_id",
        value.lower(),
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", sanitized).strip("_")
    return normalized or "target"


def helper_module_name(output_path: str | Path) -> str:
    """Return the generated helper module name for an output test file."""
    destination = Path(output_path)
    return f"_{destination.stem}_helpers.py"


def data_file_name(output_path: str | Path) -> str:
    """Return the generated JSON sidecar name for scaffolded case data."""
    destination = Path(output_path)
    return f"_{destination.stem}_data.json"


def website_suite_name_for_output(output_path: str | Path) -> str | None:
    """Infer the website suite slug from a generated tests output path."""
    destination = Path(output_path)
    parts = destination.parts
    try:
        website_index = parts.index("websites")
    except ValueError:
        return None
    if len(parts) <= website_index + 2:
        return None
    if parts[website_index + 2] != "generated":
        return None
    return parts[website_index + 1]


def format_generated_python(source: str) -> str:
    """Auto-format generated Python and guarantee a trailing newline."""
    formatted = autopep8.fix_code(
        source,
        options={"max_line_length": 120, "aggressive": 2},
    )
    return formatted.rstrip() + "\n"


def wrapped_string_literal(
    value: str,
    *,
    indent: str = "        ",
    width: int = 88,
) -> str:
    """Wrap long string literals so generated code stays readable."""
    literal = repr(value)
    if len(indent) + len(literal) <= width:
        return literal

    chunk_size = max(20, width - len(indent) - 4)
    chunks = [
        repr(value[index:index + chunk_size])
        for index in range(0, len(value), chunk_size)
    ]
    joined = "\n".join(f"{indent}{chunk}" for chunk in chunks)
    return f"(\n{joined}\n{indent[:-4]})"


def comment_lines(label: str, value: str, *, width: int = 88) -> list[str]:
    """Format a long scenario detail as wrapped Python comment lines."""
    prefix = f"# {label}: "
    return textwrap.wrap(
        value,
        width=width,
        initial_indent=prefix,
        subsequent_indent="#   ",
        break_long_words=False,
        break_on_hyphens=False,
    )


def load_gap_cases(report_path: str | Path) -> tuple[str, str | None, list[GapCase]]:
    """Load UI and API gap cases from a gap report."""
    with Path(report_path).open(encoding="utf-8") as file:
        report = json.load(file)
    page = report.get("page", "unknown")

    cases: list[GapCase] = []
    for item in report.get("untested_ui_elements", []):
        if isinstance(item, dict):
            cases.append(
                GapCase(
                    str(item.get("target", "")),
                    "ui",
                    "ComponentVisibilityTemplate",
                    presence=str(item.get("presence", "deterministic")),
                    ui_details=item,
                )
            )
            continue
        cases.append(
            GapCase(
                str(item),
                "ui",
                "ComponentVisibilityTemplate",
            )
        )
    cases.extend(
        GapCase(
            item["target"] if isinstance(item, dict) else item,
            "api",
            "ApiServiceTemplate",
            api_details=item if isinstance(item, dict) else None,
        )
        for item in report.get("untested_api_endpoints", [])
    )
    return page, report.get("base_url"), cases


def is_automationexercise(base_url: str | None) -> bool:
    """Return whether the current scaffold target is Automation Exercise."""
    return bool(base_url and "automationexercise.com" in base_url.lower())


def is_reqres(base_url: str | None) -> bool:
    """Return whether the current scaffold target is ReqRes."""
    return bool(base_url and "reqres.in" in base_url.lower())


def render_covers_decorator(
    *,
    coverage_type: str,
    target: str,
    template: str,
    page: str,
    feature: str,
    presence: str,
) -> str:
    """Render the ``@covers`` decorator block for one generated test."""
    return "\n".join(
        [
            "@covers(",
            f'    type="{coverage_type}",',
            f"    target={wrapped_string_literal(target, indent=' ' * 12)},",
            '    priority="high",',
            f'    template="{template}",',
            f"    page={page!r},",
            f"    feature={feature!r},",
            f'    presence="{presence}",',
            ")",
        ]
    )


def reqres_placeholder_path(path: str) -> str:
    """Replace example ReqRes record ids with a runtime-filled placeholder."""
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        path,
    )


def reqres_placeholder_url(url: str) -> str:
    """Replace example ReqRes record ids inside full URLs with a placeholder."""
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        url,
    )


def reqres_placeholder_target(target: str) -> str:
    """Replace example ReqRes record ids inside coverage target labels."""
    return re.sub(
        r"/api/collections/products/records/[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b",
        "/api/collections/products/records/{record_id_filled_during_test}",
        target,
    )


def build_case_data_payload(
    coverage_type: str,
    cases: list[GapCase],
) -> dict[str, dict[str, object]]:
    """Collect per-case UI snapshots or API payload fixtures into JSON data."""
    data_payload: dict[str, dict[str, object]] = {}
    for case in cases:
        case_name = f"{case.coverage_type}_{identifier(case.target)}"
        data_entry: dict[str, object] = {}
        if coverage_type == "ui":
            observed = (
                case.ui_details.get("observed")
                if case.ui_details and isinstance(case.ui_details.get("observed"), dict)
                else None
            )
            if observed:
                data_entry["ui_snapshot"] = observed
        elif case.api_details:
            for key in ("request_body", "response_payload"):
                value = case.api_details.get(key)
                if value:
                    data_entry[key] = str(value)
        if data_entry:
            data_payload[case_name] = data_entry
    return data_payload
