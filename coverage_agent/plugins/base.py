from __future__ import annotations

from abc import ABC, abstractmethod
from playwright.async_api import Page

class ApiScraper(ABC):
    """Abstract base class for website-specific API documentation scrapers."""

    @abstractmethod
    async def scrape(self, page: Page) -> list[dict[str, str]]:
        """Scrape the page for API endpoints."""
        pass