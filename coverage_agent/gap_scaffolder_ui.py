"""UI-specific gap scaffolding helpers."""

from __future__ import annotations

from coverage_agent.gap_scaffolder_common import (
    STRUCTURAL_ASSERTION_TAGS,
    TEXT_ASSERTION_MAX_LENGTH,
    TEXT_ASSERTION_TAGS,
    GapCase,
    identifier,
)


def ui_snapshot(case: GapCase) -> dict[str, object]:
    """Return the discovered UI snapshot payload stored for a gap case."""
    if not case.ui_details:
        return {}
    observed = case.ui_details.get("observed")
    return observed if isinstance(observed, dict) else {}


def omit_ui_case(case: GapCase) -> bool:
    """Skip stale responsive container artifacts that no longer map to a live target."""
    snapshot = ui_snapshot(case)
    if not snapshot:
        return False
    identity = " ".join(
        str(snapshot.get(key, ""))
        for key in ("locator_value", "data_testid", "aria_label")
    ).lower()
    if (
        "mobile-" in identity
        and str(snapshot.get("visibility_state", "")).lower() == "hidden"
        and str(snapshot.get("tag_name", "")).lower() == "div"
        and not str(snapshot.get("text", "")).strip()
        and not str(snapshot.get("href", "")).strip()
        and not str(snapshot.get("id", "")).strip()
        and not str(snapshot.get("src", "")).strip()
        and not str(snapshot.get("image_src", "")).strip()
    ):
        return True
    return False


def is_mobile_ui_case(case: GapCase) -> bool:
    """Detect whether a generated UI case should run with a mobile browser profile."""
    snapshot = ui_snapshot(case)
    identity = " ".join(
        [
            case.target,
            str(snapshot.get("locator_value", "")),
            str(snapshot.get("data_testid", "")),
        ]
    ).lower()
    return "mobile-" in identity or "mobile_" in identity


def ui_check_kind(case: GapCase) -> str:
    """Choose the simplest assertion strategy that matches the discovered element."""
    if case.template in {"InputValidationTemplate", "FormValidationTemplate"}:
        return "input_validation"
    if case.template == "InteractionTemplate":
        return "interaction"

    snapshot = ui_snapshot(case)
    tag_name = str(snapshot.get("tag_name", "")).lower()
    visibility_state = str(snapshot.get("visibility_state", "visible")).lower()
    text = str(snapshot.get("text", "")).strip()

    if visibility_state and visibility_state != "visible":
        return "optional_attached"
    if tag_name == "script":
        return "attached"
    if (
        text
        and tag_name in TEXT_ASSERTION_TAGS
        and len(text) <= TEXT_ASSERTION_MAX_LENGTH
    ):
        return "text"
    if tag_name in {"ul", "ol"} and snapshot.get("role") and not text:
        return "optional_attached"
    if tag_name == "img" or any(
        snapshot.get(key)
        for key in ("src", "image_src", "background_image_url")
    ):
        return "image"
    if tag_name in STRUCTURAL_ASSERTION_TAGS:
        return "optional_visible"
    return "visible"


def ui_check_call(case: GapCase) -> str:
    """Render the assertion call used inside a generated UI test body."""
    kind = ui_check_kind(case)
    if kind == "input_validation":
        return "await assert_input_validation(target)"
    if kind == "interaction":
        return "await assert_interaction(target)"
    if kind == "attached":
        return "await assert_attached(target)"
    if kind == "optional_attached":
        return f"await assert_attached_or_skip(target, {case.target!r})"
    if kind == "optional_visible":
        return f"await assert_visible_or_skip(target, {case.target!r})"
    if kind == "text":
        return 'await assert_text(target, expected_snapshot.get("text", ""))'
    if kind == "image":
        return "await assert_image_present(target)"
    return "await assert_visible(target)"


def ui_helper_imports(cases: list[GapCase]) -> list[str]:
    """Return only the generated UI helper imports required by the selected cases."""
    imports = {"open_generated_ui_target", "record_generated_ui_target"}
    for case in cases:
        if case.coverage_type != "ui":
            continue
        kind = ui_check_kind(case)
        if kind == "input_validation":
            imports.add("assert_input_validation")
        elif kind == "interaction":
            imports.add("assert_interaction")
        elif kind == "attached":
            imports.add("assert_attached")
        elif kind == "optional_attached":
            imports.add("assert_attached_or_skip")
        elif kind == "optional_visible":
            imports.add("assert_visible_or_skip")
        elif kind == "text":
            imports.add("assert_text")
        elif kind == "image":
            imports.add("assert_image_present")
        else:
            imports.add("assert_visible")
    return sorted(imports)


def render_ui_helper_lines() -> list[str]:
    """Emit the generated helper module source lines used by scaffolded UI tests."""
    return [
        "def _normalize_snapshot_text(value: object) -> str:",
        '    text = str(value or "").strip()',
        "    if not text:",
        '        return ""',
        "    pieces: list[str] = []",
        "    previous = ''",
        "    for char in text:",
        "        if previous and previous.islower() and char.isupper():",
        '            pieces.append(" ")',
        "        pieces.append(char)",
        "        previous = char",
        '    normalized = " ".join("".join(pieces).split())',
        "    return normalized",
        "",
        "",
        "def _text_candidates(expected_snapshot: dict[str, object] | None) -> list[str]:",
        "    if not expected_snapshot:",
        "        return []",
        '    normalized = _normalize_snapshot_text(expected_snapshot.get("text", ""))',
        "    if not normalized:",
        "        return []",
        "    candidates: list[str] = [normalized]",
        "    parts = normalized.split()",
        "    if len(parts) >= 2:",
        '        candidates.append(" ".join(parts[:2]))',
        '        candidates.append(" ".join(parts[-2:]))',
        "    candidates.extend(token for token in parts if len(token) >= 4)",
        "    unique: list[str] = []",
        "    for candidate in candidates:",
        "        if candidate and candidate not in unique:",
        "            unique.append(candidate)",
        "    return unique",
        "",
        "",
        "def _is_mobile_target(",
        "    name: str,",
        "    expected_snapshot: dict[str, object] | None = None,",
        ") -> bool:",
        "    identity_parts = [name]",
        "    if expected_snapshot:",
        "        identity_parts.extend(",
        '            str(expected_snapshot.get(key, ""))',
        '            for key in ("locator_value", "data_testid")',
        "        )",
        '    identity = " ".join(identity_parts).lower()',
        '    return "mobile-" in identity or "mobile_" in identity',
        "",
        "",
        "def target_candidates(",
        "    page,",
        "    name: str,",
        "    expected_snapshot: dict[str, object] | None = None,",
        "):",
        "    candidates = []",
        "    if expected_snapshot:",
        '        locator_attribute = str(expected_snapshot.get("locator_attribute", "")).strip()',
        '        locator_value = str(expected_snapshot.get("locator_value", "")).strip()',
        "        if locator_attribute and locator_value:",
        "            escaped = locator_value.replace('\"', '\\\\\"')",
        '            candidates.append(page.locator(f\'[{locator_attribute}=\"{escaped}\"]\').first)',
        '        element_id = str(expected_snapshot.get("id", "")).strip()',
        "        if element_id:",
        "            escaped = element_id.replace('\"', '\\\\\"')",
        "            candidates.append(page.locator(f'#{escaped}').first)",
        '        href = str(expected_snapshot.get("href", "")).strip()',
        "        if href:",
        "            escaped = href.replace('\"', '\\\\\"')",
        '            candidates.append(page.locator(f\'a[href=\"{escaped}\"]\').first)',
        '        role = str(expected_snapshot.get("role", "")).strip()',
        '        aria_label = str(expected_snapshot.get("aria_label", "")).strip()',
        "        if role and aria_label:",
        "            escaped_role = role.replace('\"', '\\\\\"')",
        "            escaped_aria = aria_label.replace('\"', '\\\\\"')",
        "            candidates.append(",
        "                page.locator(",
        '                    f\'[role=\"{escaped_role}\"][aria-label=\"{escaped_aria}\"]\'',
        "                ).first",
        "            )",
        "        if aria_label:",
        "            escaped_aria = aria_label.replace('\"', '\\\\\"')",
        '            candidates.append(page.locator(f\'[aria-label=\"{escaped_aria}\"]\').first)',
        '        tag_name = str(expected_snapshot.get("tag_name", "")).strip().lower()',
        "        for candidate in _text_candidates(expected_snapshot):",
        "            if tag_name:",
        "                candidates.append(page.locator(tag_name).filter(has_text=candidate).first)",
        "            candidates.append(page.get_by_text(candidate, exact=False).first)",
        '    escaped = name.replace(\'"\', \'\\\\"\')',
        "    candidates.append(",
        "        page.locator(",
        '            f\'[data-testid=\"{escaped}\"], [data-test=\"{escaped}\"], [data-qa=\"{escaped}\"]\'',
        "        ).first",
        "    )",
        "    return candidates",
        "",
        "",
        "async def target_locator(",
        "    page,",
        "    name: str,",
        "    expected_snapshot: dict[str, object] | None = None,",
        "):",
        "    for candidate in target_candidates(page, name, expected_snapshot):",
        "        if await candidate.count() > 0:",
        "            return candidate",
        "    return target_candidates(page, name, expected_snapshot)[0]",
        "",
        "",
        "async def skip_if_security_block(page) -> None:",
        "    block_markers = (",
        '        "Sorry, you have been blocked",',
        '        "You are unable to access",',
        '        "security service to protect itself from online attacks",',
        '        "Cloudflare Ray ID",',
        "    )",
        "    try:",
        "        title = await page.title()",
        "    except Exception:",
        '        title = ""',
        "    try:",
        '        body_text = await page.locator("body").inner_text()',
        "    except Exception:",
        '        body_text = ""',
        "    normalized_url = page.url.lower()",
        '    combined = f"{title}\\n{body_text}"',
        '    if "/cdn-cgi/" in normalized_url or any(marker in combined for marker in block_markers):',
        "        pytest.skip(",
        '            "Live target blocked this automated browser session with a security page "',
        '            "(headless/browser fingerprint protection)."',
        "        )",
        "",
        "",
        "async def _find_target(page, name: str, expected_snapshot: dict[str, object] | None):",
        "    for candidate in target_candidates(page, name, expected_snapshot):",
        "        if await candidate.count() > 0:",
        "            return candidate",
        "    return None",
        "",
        "",
        "async def _open_mobile_navigation(page) -> None:",
        "    menu_selectors = (",
        '        \'[data-testid=\"burger-menu-button\"]\',',
        '        \'button[aria-label=\"menu\"]\',',
        '        \'button[aria-label*=\"menu\" i]\',',
        "    )",
        "    for selector in menu_selectors:",
        "        toggle = page.locator(selector).first",
        "        if await toggle.count() == 0:",
        "            continue",
        "        try:",
        "            await toggle.click(force=True)",
        "            await page.wait_for_timeout(500)",
        "        except Exception:",
        "            continue",
        "        return",
        "",
        "",
        "async def prepare_target(page, name: str, expected_snapshot: dict[str, object] | None):",
        "    await skip_if_security_block(page)",
        "    target = await _find_target(page, name, expected_snapshot)",
        "    if target is not None:",
        "        return target",
        "    if _is_mobile_target(name, expected_snapshot):",
        "        await _open_mobile_navigation(page)",
        "        target = await _find_target(page, name, expected_snapshot)",
        "        if target is not None:",
        "            return target",
        "    for _ in range(8):",
        "        await page.mouse.wheel(0, 1200)",
        "        await page.wait_for_timeout(350)",
        "        target = await _find_target(page, name, expected_snapshot)",
        "        if target is not None:",
        "            return target",
        "    if _is_mobile_target(name, expected_snapshot):",
        "        await _open_mobile_navigation(page)",
        "        target = await _find_target(page, name, expected_snapshot)",
        "        if target is not None:",
        "            return target",
        "    await skip_if_security_block(page)",
        "    return await target_locator(page, name, expected_snapshot)",
        "",
        "",
        "async def open_generated_ui_target(",
        "    page,",
        "    *,",
        "    page_path: str,",
        "    target_name: str,",
        "    expected_snapshot: dict[str, object] | None,",
        "):",
        "    await page.goto(page_path)",
        "    return await prepare_target(page, target_name, expected_snapshot)",
        "",
        "",
        "async def record_generated_ui_target(",
        "    test_diagnostics,",
        "    *,",
        "    target,",
        "    target_name: str,",
        "    expected_snapshot: dict[str, object] | None,",
        "    assertion: str,",
        ") -> None:",
        "    observed_snapshot = await describe_target(target) if await target.count() > 0 else {}",
        "    test_diagnostics.record(",
        '        "generated_ui_target",',
        "        target=target_name,",
        "        expected_snapshot=expected_snapshot or {},",
        "        observed_snapshot=observed_snapshot,",
        "        assertion=assertion,",
        "    )",
        "",
        "",
        "async def assert_visible(target) -> None:",
        "    await expect(target).to_be_visible()",
        "",
        "",
        "async def assert_attached(target) -> None:",
        "    assert await target.count() > 0, \"Expected element is not attached to the DOM\"",
        "",
        "",
        "async def assert_attached_or_skip(target, name: str) -> None:",
        "    if await target.count() == 0:",
        "        pytest.skip(f\"Responsive or structural element is absent in this render: {name}\")",
        "",
        "",
        "async def assert_visible_or_skip(target, name: str) -> None:",
        "    if await target.count() == 0:",
        "        pytest.skip(f\"Responsive or structural element is absent in this render: {name}\")",
        "    await expect(target).to_be_visible()",
        "",
        "",
        "async def describe_target(target) -> dict[str, object]:",
        "    await assert_attached(target)",
        "    return await target.evaluate(",
        '        """node => {',
        "            const normalize = (value) =>",
        '                String(value ?? "").replace(/\\s+/g, " ").trim();',
        "            const style = window.getComputedStyle(node);",
        "            const rect = node.getBoundingClientRect();",
        "            const image = node.tagName.toLowerCase() === 'img'",
        "                ? node",
        "                : node.querySelector('img');",
        "            return {",
        '                tag_name: normalize(node.tagName).toLowerCase(),',
        '                text: normalize(node.innerText || node.textContent || ""),',
        '                value: "value" in node ? normalize(node.value) : "",',
        '                href: normalize(node.getAttribute("href")),',
        '                src: normalize(node.getAttribute("src")),',
        '                data_testid: normalize(node.getAttribute("data-testid")),',
        '                data_test: normalize(node.getAttribute("data-test")),',
        '                data_qa: normalize(node.getAttribute("data-qa")),',
        '                aria_label: normalize(node.getAttribute("aria-label")),',
        '                visibility_state: (style.display === "none" ||',
        '                    style.visibility === "hidden" ||',
        '                    style.visibility === "collapse" ||',
        "                    rect.width === 0 || rect.height === 0)",
        '                    ? "hidden"',
        '                    : "visible",',
        "                image_src: image",
        '                    ? normalize(image.currentSrc || image.getAttribute("src") || "")',
        '                    : "",',
        "            };",
        '        }"""',
        "    )",
        "",
        "",
        "async def assert_text(target, expected_text: object) -> None:",
        '    expected = str(expected_text or "").strip()',
        '    assert expected, "Expected text snapshot is empty"',
        "    await expect(target).to_be_visible()",
        "    await expect(target).to_contain_text(expected)",
        "",
        "",
        "async def assert_image_present(target) -> None:",
        "    await assert_attached(target)",
        "    image_source = await target.evaluate(",
        '        """node => {',
        "            const image = node.tagName.toLowerCase() === 'img'",
        "                ? node",
        "                : node.querySelector('img');",
        "            if (image) {",
        "                return image.currentSrc || image.getAttribute('src') || '';",
        "            }",
        "            const style = window.getComputedStyle(node);",
        "            const match = (style.backgroundImage || '').match(/url\\\\([\"']?(.*?)[\"']?\\\\)/);",
        "            return match && match[2] ? match[2] : '';",
        '        }"""',
        "    )",
        "    assert str(image_source or '').strip(), \"Expected image source was not found\"",
        "",
        "",
        "async def assert_input_validation(target) -> None:",
        "    await expect(target).to_be_visible()",
        "    await expect(target).to_be_editable()",
        '    input_type = (await target.get_attribute("type") or "text").lower()',
        '    await target.fill("not-a-valid-value")',
        '    if input_type in {"email", "url", "number"}:',
        '        assert not await target.evaluate("element => element.checkValidity()")',
        "    else:",
        '        assert await target.input_value() == "not-a-valid-value"',
        "",
        "",
        "async def assert_interaction(target) -> None:",
        "    await expect(target).to_be_visible()",
        "    await expect(target).to_be_enabled()",
        "",
    ]


def render_ui_module_support(
    *,
    website_suite_name: str | None,
    data_file_name: str | None,
) -> list[str]:
    """Render module-level helpers that resolve base URL and case snapshot data."""
    lines: list[str] = []
    if website_suite_name:
        lines.extend(
            [
                "def resolve_generated_ui_case(",
                "    pytestconfig,",
                "    settings,",
                "    case_name: str,",
                ") -> tuple[str, dict[str, object]]:",
                "    _ = (pytestconfig, settings)",
                "    base_url = BASE_URL",
                "    case_data = CASE_DATA.get(case_name, {})",
                '    expected_snapshot = case_data.get("ui_snapshot", {})',
                "    return base_url, expected_snapshot",
                "",
            ]
        )
    elif data_file_name:
        lines.extend(
            [
                "def resolve_generated_ui_case(",
                "    generated_target_url: str,",
                "    case_name: str,",
                ") -> tuple[str, dict[str, object]]:",
                "    case_data = CASE_DATA.get(case_name, {})",
                '    expected_snapshot = case_data.get("ui_snapshot", {})',
                "    return generated_target_url, expected_snapshot",
                "",
            ]
        )
    return lines


def render_generated_target_fixture(default_base_url: str | None) -> list[str]:
    """Render the generic URL fixture for non-website generated UI suites."""
    _ = default_base_url
    return [
        "@pytest.fixture(scope='module')",
        "def generated_target_url(pytestconfig) -> str:",
        '    target_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL',
        "    if not target_url:",
        '        pytest.skip("Set BASE_URL or pass --target-url")',
        "    return target_url.rstrip('/')",
        "",
    ]


def render_ui_test_function(
    *,
    case: GapCase,
    decorator: str,
    page: str,
    rendered_target: str,
    website_suite_name: str | None,
) -> str:
    """Render one generated async UI test function for a discovered gap case."""
    name = f"{case.coverage_type}_{identifier(case.target)}"
    ui_assertion = ui_check_call(case)
    if website_suite_name:
        function_signature = "page_factory, pytestconfig, settings, test_diagnostics"
        ui_case_locals = (
            f"    base_url, expected_snapshot = resolve_generated_ui_case(\n"
            "        pytestconfig,\n"
            "        settings,\n"
            f"        {name!r},\n"
            "    )"
        )
        page_factory_target = "base_url"
    else:
        function_signature = "page_factory, generated_target_url, test_diagnostics"
        ui_case_locals = (
            f"    base_url, expected_snapshot = resolve_generated_ui_case(\n"
            "        generated_target_url,\n"
            f"        {name!r},\n"
            "    )"
        )
        page_factory_target = "base_url"

    if is_mobile_ui_case(case):
        mobile_viewport_ref = (
            "MOBILE_VIEWPORT"
            if website_suite_name
            else '{"width": 390, "height": 844}'
        )
        mobile_user_agent_ref = (
            "MOBILE_USER_AGENT"
            if website_suite_name
            else (
                '"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 '
                'Mobile/15E148 Safari/604.1"'
            )
        )
        page_factory_invocation = f"""page_factory(
        {page_factory_target},
        viewport={mobile_viewport_ref},
        is_mobile=True,
        has_touch=True,
        user_agent={mobile_user_agent_ref},
    )"""
    else:
        page_factory_invocation = f"page_factory({page_factory_target})"
    return f'''\n{decorator}
async def test_generated_{name}({function_signature}):
{ui_case_locals}
    async with {page_factory_invocation} as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path={page!r},
            target_name={rendered_target!r},
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name={rendered_target!r},
            expected_snapshot=expected_snapshot,
            assertion={ui_assertion!r},
        )
        {ui_assertion}
'''
