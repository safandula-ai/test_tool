from __future__ import annotations

from urllib.parse import urlsplit
from .base import ApiScraper
from .automationexercise import AutomationExerciseScraper
from .reqres import ReqResScraper


def get_scraper(base_url: str) -> ApiScraper | None:
    """Returns the appropriate scraper plugin based on the base URL."""
    netloc = urlsplit(base_url).netloc
    if "automationexercise.com" in netloc:
        return AutomationExerciseScraper()
    if "reqres.in" in netloc:
        return ReqResScraper()
    return None
