"""Shared helpers for website-specific smoke, performance, and security tests."""

from __future__ import annotations


def resolve_target_url(
    pytestconfig,
    *,
    default_base_url: str,
) -> str:
    """Resolve the live target URL, preferring terminal overrides."""
    override = pytestconfig.getoption("--target-url")

    def normalize(value: str) -> str:
        normalized = value.strip()
        if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {"'", '"'}:
            normalized = normalized[1:-1].strip()
        return normalized.rstrip("/")

    if override:
        return normalize(override)
    return normalize(default_base_url)


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
