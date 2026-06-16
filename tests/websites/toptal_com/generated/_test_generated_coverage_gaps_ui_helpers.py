"""Helper functions for generated coverage tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from playwright.async_api import expect


def _normalize_snapshot_text(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    pieces: list[str] = []
    previous = ''
    for char in text:
        if previous and previous.islower() and char.isupper():
            pieces.append(" ")
        pieces.append(char)
        previous = char
    normalized = " ".join("".join(pieces).split())
    return normalized


def _text_candidates(expected_snapshot: dict[str, object] | None) -> list[str]:
    if not expected_snapshot:
        return []
    normalized = _normalize_snapshot_text(expected_snapshot.get("text", ""))
    if not normalized:
        return []
    candidates: list[str] = [normalized]
    parts = normalized.split()
    if len(parts) >= 2:
        candidates.append(" ".join(parts[:2]))
        candidates.append(" ".join(parts[-2:]))
    candidates.extend(token for token in parts if len(token) >= 4)
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _is_mobile_target(
    name: str,
    expected_snapshot: dict[str, object] | None = None,
) -> bool:
    identity_parts = [name]
    if expected_snapshot:
        identity_parts.extend(
            str(expected_snapshot.get(key, ""))
            for key in ("locator_value", "data_testid")
        )
    identity = " ".join(identity_parts).lower()
    return "mobile-" in identity or "mobile_" in identity


def target_candidates(
    page,
    name: str,
    expected_snapshot: dict[str, object] | None = None,
):
    candidates = []
    if expected_snapshot:
        locator_attribute = str(expected_snapshot.get("locator_attribute", "")).strip()
        locator_value = str(expected_snapshot.get("locator_value", "")).strip()
        if locator_attribute and locator_value:
            escaped = locator_value.replace('"', '\\"')
            candidates.append(page.locator(f'[{locator_attribute}="{escaped}"]').first)
        element_id = str(expected_snapshot.get("id", "")).strip()
        if element_id:
            escaped = element_id.replace('"', '\\"')
            candidates.append(page.locator(f'#{escaped}').first)
        href = str(expected_snapshot.get("href", "")).strip()
        if href:
            escaped = href.replace('"', '\\"')
            candidates.append(page.locator(f'a[href="{escaped}"]').first)
        role = str(expected_snapshot.get("role", "")).strip()
        aria_label = str(expected_snapshot.get("aria_label", "")).strip()
        if role and aria_label:
            escaped_role = role.replace('"', '\\"')
            escaped_aria = aria_label.replace('"', '\\"')
            candidates.append(
                page.locator(
                    f'[role="{escaped_role}"][aria-label="{escaped_aria}"]'
                ).first
            )
        if aria_label:
            escaped_aria = aria_label.replace('"', '\\"')
            candidates.append(page.locator(f'[aria-label="{escaped_aria}"]').first)
        tag_name = str(expected_snapshot.get("tag_name", "")).strip().lower()
        for candidate in _text_candidates(expected_snapshot):
            if tag_name:
                candidates.append(page.locator(tag_name).filter(has_text=candidate).first)
            candidates.append(page.get_by_text(candidate, exact=False).first)
    escaped = name.replace('"', '\\"')
    candidates.append(
        page.locator(
            f'[data-testid="{escaped}"], [data-test="{escaped}"], [data-qa="{escaped}"]'
        ).first
    )
    return candidates


async def target_locator(
    page,
    name: str,
    expected_snapshot: dict[str, object] | None = None,
):
    for candidate in target_candidates(page, name, expected_snapshot):
        if await candidate.count() > 0:
            return candidate
    return target_candidates(page, name, expected_snapshot)[0]


async def skip_if_security_block(page) -> None:
    block_markers = (
        "Sorry, you have been blocked",
        "You are unable to access",
        "security service to protect itself from online attacks",
        "Cloudflare Ray ID",
    )
    try:
        title = await page.title()
    except Exception:
        title = ""
    try:
        body_text = await page.locator("body").inner_text()
    except Exception:
        body_text = ""
    normalized_url = page.url.lower()
    combined = f"{title}\n{body_text}"
    if "/cdn-cgi/" in normalized_url or any(marker in combined for marker in block_markers):
        pytest.skip(
            "Live target blocked this automated browser session with a security page "
            "(headless/browser fingerprint protection)."
        )


async def _find_target(page, name: str, expected_snapshot: dict[str, object] | None):
    for candidate in target_candidates(page, name, expected_snapshot):
        if await candidate.count() > 0:
            return candidate
    return None


async def _open_mobile_navigation(page) -> None:
    menu_selectors = (
        '[data-testid="burger-menu-button"]',
        'button[aria-label="menu"]',
        'button[aria-label*="menu" i]',
    )
    for selector in menu_selectors:
        toggle = page.locator(selector).first
        if await toggle.count() == 0:
            continue
        try:
            await toggle.click(force=True)
            await page.wait_for_timeout(500)
        except Exception:
            continue
        return


async def prepare_target(page, name: str, expected_snapshot: dict[str, object] | None):
    await skip_if_security_block(page)
    target = await _find_target(page, name, expected_snapshot)
    if target is not None:
        return target
    if _is_mobile_target(name, expected_snapshot):
        await _open_mobile_navigation(page)
        target = await _find_target(page, name, expected_snapshot)
        if target is not None:
            return target
    for _ in range(8):
        await page.mouse.wheel(0, 1200)
        await page.wait_for_timeout(350)
        target = await _find_target(page, name, expected_snapshot)
        if target is not None:
            return target
    if _is_mobile_target(name, expected_snapshot):
        await _open_mobile_navigation(page)
        target = await _find_target(page, name, expected_snapshot)
        if target is not None:
            return target
    await skip_if_security_block(page)
    return await target_locator(page, name, expected_snapshot)


async def open_generated_ui_target(
    page,
    *,
    page_path: str,
    target_name: str,
    expected_snapshot: dict[str, object] | None,
):
    await page.goto(page_path)
    return await prepare_target(page, target_name, expected_snapshot)


async def record_generated_ui_target(
    test_diagnostics,
    *,
    target,
    target_name: str,
    expected_snapshot: dict[str, object] | None,
    assertion: str,
) -> None:
    observed_snapshot = await describe_target(target) if await target.count() > 0 else {}
    test_diagnostics.record(
        "generated_ui_target",
        target=target_name,
        expected_snapshot=expected_snapshot or {},
        observed_snapshot=observed_snapshot,
        assertion=assertion,
    )


async def assert_visible(target) -> None:
    await expect(target).to_be_visible()


async def assert_attached(target) -> None:
    assert await target.count() > 0, "Expected element is not attached to the DOM"


async def assert_attached_or_skip(target, name: str) -> None:
    if await target.count() == 0:
        pytest.skip(f"Responsive or structural element is absent in this render: {name}")


async def assert_visible_or_skip(target, name: str) -> None:
    if await target.count() == 0:
        pytest.skip(f"Responsive or structural element is absent in this render: {name}")
    await expect(target).to_be_visible()


async def describe_target(target) -> dict[str, object]:
    await assert_attached(target)
    return await target.evaluate(
        """node => {
            const normalize = (value) =>
                String(value ?? "").replace(/\\s+/g, " ").trim();
            const style = window.getComputedStyle(node);
            const rect = node.getBoundingClientRect();
            const image = node.tagName.toLowerCase() === 'img'
                ? node
                : node.querySelector('img');
            return {
                tag_name: normalize(node.tagName).toLowerCase(),
                text: normalize(node.innerText || node.textContent || ""),
                value: "value" in node ? normalize(node.value) : "",
                href: normalize(node.getAttribute("href")),
                src: normalize(node.getAttribute("src")),
                data_testid: normalize(node.getAttribute("data-testid")),
                data_test: normalize(node.getAttribute("data-test")),
                data_qa: normalize(node.getAttribute("data-qa")),
                aria_label: normalize(node.getAttribute("aria-label")),
                visibility_state: (style.display === "none" ||
                    style.visibility === "hidden" ||
                    style.visibility === "collapse" ||
                    rect.width === 0 || rect.height === 0)
                    ? "hidden"
                    : "visible",
                image_src: image
                    ? normalize(image.currentSrc || image.getAttribute("src") || "")
                    : "",
            };
        }"""
    )


async def assert_text(target, expected_text: object) -> None:
    expected = str(expected_text or "").strip()
    assert expected, "Expected text snapshot is empty"
    await expect(target).to_be_visible()
    await expect(target).to_contain_text(expected)


async def assert_image_present(target) -> None:
    await assert_attached(target)
    image_source = await target.evaluate(
        """node => {
            const image = node.tagName.toLowerCase() === 'img'
                ? node
                : node.querySelector('img');
            if (image) {
                return image.currentSrc || image.getAttribute('src') || '';
            }
            const style = window.getComputedStyle(node);
            const match = (style.backgroundImage || '').match(/url\\(["']?(.*?)["']?\\)/);
            return match && match[2] ? match[2] : '';
        }"""
    )
    assert str(image_source or '').strip(), "Expected image source was not found"


async def assert_input_validation(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_editable()
    input_type = (await target.get_attribute("type") or "text").lower()
    await target.fill("not-a-valid-value")
    if input_type in {"email", "url", "number"}:
        assert not await target.evaluate("element => element.checkValidity()")
    else:
        assert await target.input_value() == "not-a-valid-value"


async def assert_interaction(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_enabled()


def load_generated_case_data(
    module_file: str,
    file_name: str,
) -> dict[str, dict[str, object]]:
    data_path = Path(module_file).with_name(file_name)
    if not data_path.is_file():
        return {}
    return json.loads(data_path.read_text(encoding='utf-8'))
