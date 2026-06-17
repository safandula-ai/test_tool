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
    reject_selector: str | None = None,
) -> None:
    """Remove a consent dialog that blocks interactions, when one exists."""
    root = page.locator(root_selector).first
    if await root.count() == 0:
        return
    for selector in (accept_selector, reject_selector):
        if not selector:
            continue
        button = page.locator(selector).first
        if await button.count() == 0:
            continue
        if await button.is_visible():
            await button.click(force=True)
            try:
                await root.wait_for(state="hidden", timeout=2_000)
                return
            except Exception:
                continue
    if await root.count() > 0:
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
