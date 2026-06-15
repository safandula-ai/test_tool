"""Shared helpers for website-specific smoke, performance, and security tests."""

from __future__ import annotations

import pytest


def resolve_target_url(
    pytestconfig,
    settings,
    *,
    default_base_url: str,
    settings_base_url_attr: str | None = None,
) -> str:
    """Resolve the live target URL, preferring terminal overrides."""
    override = pytestconfig.getoption("--target-url")
    if override:
        return override.rstrip("/")
    if settings_base_url_attr:
        configured = getattr(settings, settings_base_url_attr, None)
        if configured:
            return str(configured).rstrip("/")
    return default_base_url.rstrip("/")


def require_live_target(pytestconfig, settings) -> None:
    """Skip suite tests unless live execution is explicitly enabled."""
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")


async def dismiss_consent_if_present(
    page,
    *,
    root_selector: str,
    accept_selector: str,
    overlay_selector: str = ".fc-dialog-overlay",
) -> None:
    """Remove a consent dialog that blocks interactions, when one exists."""
    root = page.locator(root_selector).first
    if await root.count() == 0:
        return
    accept_button = page.locator(accept_selector).first
    if await accept_button.is_visible():
        await accept_button.click(force=True)
    if await root.is_visible():
        await page.evaluate(
            """([rootSelector, overlaySelector]) => {
                const root = document.querySelector(rootSelector);
                if (root) {
                    root.remove();
                }
                const overlay = document.querySelector(overlaySelector);
                if (overlay) {
                    overlay.remove();
                }
                document.body.style.overflow = 'auto';
            }""",
            [root_selector, overlay_selector],
        )
