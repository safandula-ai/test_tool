from __future__ import annotations

from abc import ABC, abstractmethod
from playwright.async_api import Page


class ApiScraper(ABC):
    """Abstract base class for website-specific API documentation scrapers."""

    @abstractmethod
    async def scrape(self, page: Page) -> list[dict[str, str]]:
        """Scrape the page for API endpoints."""
        raise NotImplementedError

    async def scrape_content(self, content: str) -> list[dict[str, str]]:
        """Scrape endpoints from already captured page content."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support content-backed scraping"
        )

    async def enrich_endpoints(
        self,
        page: Page,
        endpoints: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """Optionally enrich network-observed endpoints with domain metadata."""
        _ = page
        return endpoints


class SuitePlugin(ABC):
    """Optional suite-layout customizations for generated website suites."""

    def suite_config_overrides(self) -> dict[str, object]:
        """Return suite_config constants that should override generic defaults."""
        return {}
