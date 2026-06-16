"""Website-specific suite configuration."""

BASE_URL = "https://automationexercise.com"
SUITE_NAME = "automationexercise_com"
SMOKE_HEALTH_PATH = "/"
SMOKE_HEALTH_STATUS = 200
SMOKE_ROOT_PATH = "/"
SMOKE_ROOT_SELECTOR = "header"
SMOKE_REQUEST_TIMEOUT_MS = 5_000
SMOKE_RENDER_TIMEOUT_MS = 8_000
PERF_HOME_PATH = "/"
PERF_HOME_READY_SELECTOR = "header"
PERF_MOBILE_PATH = "/login"
PERF_MOBILE_READY_SELECTOR = "[data-qa='login-email']"
SECURITY_SEARCH_PATH = "/products"
SECURITY_SEARCH_INPUT_SELECTOR = "#search_product, input[name='search']"
SECURITY_SEARCH_SUBMIT_SELECTOR = "#submit_search, button[type='submit']"
SECURITY_CONSENT_ROOT_SELECTOR = ".fc-consent-root"
SECURITY_CONSENT_ACCEPT_SELECTOR = ".fc-cta-consent, button:has-text('Consent'), button:has-text('Accept')"
SECURITY_CONSENT_OVERLAY_SELECTOR = ".fc-dialog-overlay"
