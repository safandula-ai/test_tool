from __future__ import annotations

from .base import SuitePlugin


class SabreSuitePlugin(SuitePlugin):
    """Suite-layout overrides for sabre.com."""

    def suite_config_overrides(self) -> dict[str, object]:
        return {
            "SECURITY_SEARCH_TRIGGER_SELECTOR": "a.search",
            "SECURITY_SEARCH_TRIGGER_ACTIVE_SELECTOR": "a.search.is-active",
            "SECURITY_SEARCH_PANEL_SELECTOR": ".site-header__main--search-panel",
            "SECURITY_SEARCH_PANEL_ACTIVE_SELECTOR": ".site-header__main--search-panel.is-active",
        }
