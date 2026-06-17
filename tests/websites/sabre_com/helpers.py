"""Sabre-specific website helpers."""

from __future__ import annotations

from playwright.async_api import Page


CONSENT_ROOT_SELECTOR = "#onetrust-consent-sdk"
CONSENT_OVERLAY_SELECTOR = ".onetrust-pc-dark-filter"
CONSENT_ACCEPT_SELECTOR = "#onetrust-accept-btn-handler"
CONSENT_REJECT_SELECTOR = "#onetrust-reject-all-handler"


async def dismiss_sabre_consent(page: Page) -> None:
    """Dismiss and suppress the Sabre OneTrust consent layer."""
    await page.wait_for_timeout(500)

    for selector in (CONSENT_ACCEPT_SELECTOR, CONSENT_REJECT_SELECTOR):
        button = page.locator(selector).first
        if await button.count() > 0:
            try:
                await button.click(force=True, timeout=2_000)
                break
            except Exception:
                pass

    await page.evaluate(
        """([rootSelector, overlaySelector]) => {
            const removeKnownNodes = () => {
                document.querySelectorAll(rootSelector).forEach((node) => node.remove());
                document.querySelectorAll(overlaySelector).forEach((node) => node.remove());
            };
            removeKnownNodes();
            if (!window.__sabreConsentObserverInstalled) {
                const observer = new MutationObserver(() => removeKnownNodes());
                observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true,
                });
                window.__sabreConsentObserverInstalled = true;
            }
        }""",
        [CONSENT_ROOT_SELECTOR, CONSENT_OVERLAY_SELECTOR],
    )
    await page.wait_for_timeout(200)
