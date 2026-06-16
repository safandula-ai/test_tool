"""Website-specific suite configuration."""

BASE_URL = "https://www.saucedemo.com"
SUITE_NAME = "saucedemo_com"
SMOKE_HEALTH_PATH = "/"
SMOKE_HEALTH_STATUS = 200
SMOKE_ROOT_PATH = "/"
SMOKE_ROOT_SELECTOR = "[data-test='login-container']"
SMOKE_REQUEST_TIMEOUT_MS = 5_000
SMOKE_RENDER_TIMEOUT_MS = 8_000
PERF_HOME_PATH = "/"
PERF_HOME_READY_SELECTOR = "[data-test='login-container']"
PERF_MOBILE_PATH = "/"
PERF_MOBILE_READY_SELECTOR = "[data-test='login-container']"
SECURITY_SEARCH_PATH = "/"
SECURITY_SEARCH_INPUT_SELECTOR = "#user-name"
SECURITY_SEARCH_SUBMIT_SELECTOR = "#login-button"
SECURITY_CONSENT_ROOT_SELECTOR = ".fc-consent-root"
SECURITY_CONSENT_ACCEPT_SELECTOR = ".fc-cta-consent, button:has-text('Consent'), button:has-text('Accept')"
SECURITY_CONSENT_OVERLAY_SELECTOR = ".fc-dialog-overlay"
