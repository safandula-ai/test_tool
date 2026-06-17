from __future__ import annotations

from urllib.parse import urlsplit
from .base import ApiScraper, SuitePlugin
from .automationexercise import AutomationExerciseScraper
from .reqres import ReqResScraper
from .sabre import SabreSuitePlugin
from .toptal import ToptalScraper, ToptalSuitePlugin


def get_scraper(base_url: str) -> ApiScraper | None:
    """Returns the appropriate scraper plugin based on the base URL."""
    netloc = urlsplit(base_url).netloc
    if "automationexercise.com" in netloc:
        return AutomationExerciseScraper()
    if "reqres.in" in netloc:
        return ReqResScraper()
    if "toptal.com" in netloc:
        return ToptalScraper()
    return None


def get_suite_plugin(base_url: str) -> SuitePlugin | None:
    """Return the optional suite-layout plugin for one base URL."""
    netloc = urlsplit(base_url).netloc
    if "sabre.com" in netloc:
        return SabreSuitePlugin()
    if "toptal.com" in netloc:
        return ToptalSuitePlugin()
    return None
