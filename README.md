# Test Framework Scaffold

Modular UI and API test framework built around `pytest`, `pytest-html`, async `Playwright`, `httpx`, `jsonschema`, `python-dotenv`, and `loguru`.

The example integrations target SauceDemo for browser E2E coverage, ReqRes for paginated API contract testing, and Automation Exercise for same-system API/UI hybrid testing.

## Quick Start

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
playwright install chromium
```

### Linux

Debian or Ubuntu prerequisites:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip
```

Project setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
playwright install --with-deps chromium
```

Adjust target URLs and credentials in `.env` after copying the example file.

## Environment Setup

The framework reads configuration from environment variables and `.env` files.

- `ENV`: `local`, `staging`, or `prod`
- `BASE_URL`: default UI target base URL, used by the reusable `tests/one_shot` templates unless `--target-url` is passed
- `PERFORMANCE_MAX_RESPONSE_MS`: generic performance threshold, default `5000`
- `PERFORMANCE_MAX_TTFB_MS`: homepage time-to-first-byte threshold for browser performance checks, default `800`
- `PERFORMANCE_MAX_LOAD_MS`: homepage full-load threshold for browser performance checks, default `3000`
- `PERFORMANCE_MAX_MOBILE_INTERACTIVE_MS`: throttled mobile interactive threshold, default `10000`
- `PERFORMANCE_WARMUP_RUNS`: warmup iterations discarded before website performance assertions, default `1`
- `PERFORMANCE_SAMPLE_COUNT`: measured website performance samples aggregated by median, default `3`
- `PERFORMANCE_MOBILE_LATENCY_MS`: synthetic mobile latency in milliseconds, default `300`
- `PERFORMANCE_MOBILE_DOWNLOAD_KBPS`: synthetic mobile download rate in kilobits per second, default `400`
- `PERFORMANCE_MOBILE_UPLOAD_KBPS`: synthetic mobile upload rate in kilobits per second, default `150`
- `PERFORMANCE_MOBILE_CPU_THROTTLE_RATE`: synthetic mobile CPU slowdown multiplier, default `4`
- `PERFORMANCE_MOBILE_PROFILE_NAME`: label recorded in diagnostics for the mobile throttle profile, default `slow_3g_like`
- `API_BASE_URL`: API target base URL
- `HEADLESS`: run browser headless when `true`
- `HTML_REPORT_REQUIRED`: fail an otherwise successful run when pytest-html output is unavailable
- `TERMINAL_DIAGNOSTICS`: print custom `TEST DIAGNOSTICS` blocks to the terminal, default `true`
- `TRACE_ON_FAILURE`: enable trace capture for failed UI tests
- `REQRES_API_KEY`: required by ReqRes for live API requests
- `UPDATE_VISUAL_BASELINES`: create or replace visual regression baselines
- `ONE_SHOT_SMOKE_*`, `ONE_SHOT_PERF_*`, `ONE_SHOT_SECURITY_*`: optional path and selector overrides for the reusable one-shot templates
- `API_DOC_URL_KEYWORDS`: API doc labels treated as endpoint URLs
- `API_DOC_METHOD_KEYWORDS`: API doc labels treated as request methods
- `API_DOC_REQUEST_PARAMETER_KEYWORDS`: API doc labels treated as request-parameter fields
- `API_DOC_RESPONSE_CODE_KEYWORDS`: API doc labels treated as response-code fields
- `API_DOC_RESPONSE_PAYLOAD_KEYWORDS`: API doc labels treated as response-message or payload fields

## Running Tests

Run all tests:

```bash
pytest
```

## Style Checks

The repository includes a checked-in style configuration in `setup.cfg` for
`pycodestyle` and `flake8`.

Run the baseline repo style check with:

```bash
python -m flake8 .
```

Current policy:

- uses `max-line-length = 120`
- excludes virtualenv, cache, and report directories
- excludes generated website coverage tests from the baseline style pass

## HTML Reporting

`pytest-html` is installed through `requirements.txt` and writes a
self-contained HTML report during each pytest run. No separate CLI or Java
runtime is required.

By default, each run creates a timestamped report under
`reports/pytest-html/`, for example
`reports/pytest-html/20260616-160000-clear-river.html`. The newest report path
is also written to `reports/pytest-html/latest.txt`.

Run the suite and generate the report:

```bash
pytest
```

Open the newest report on Windows PowerShell:

```powershell
$latest = Get-Content .\reports\pytest-html\latest.txt
Start-Process $latest
```

Open the newest report on Linux:

```bash
xdg-open "$(cat ./reports/pytest-html/latest.txt)"
```

Set `HTML_REPORT_REQUIRED=true` in CI to fail an otherwise successful run when
the `pytest-html` plugin is missing or report generation is disabled. Disable
automatic HTML generation with `pytest --no-html-report`.

Windows PowerShell:

```powershell
$env:HTML_REPORT_REQUIRED = "true"
pytest
```

Linux:

```bash
HTML_REPORT_REQUIRED=true pytest
```

Override the output archive directory or the report name prefix when needed:

```bash
pytest --html-report-dir reports/custom-html --html-report-name release-2026-06
```

## Coverage Gap Agent

Tests declare the UI element or API endpoint they cover with `@covers`:

```python
@covers(
    type="ui",
    target="login-email",
    priority="high",
    presence="deterministic",
    template="InputValidationTemplate",
    page="/login",
    feature="feature:authentication",
)
```

### End-to-End Workflow

1. Generate the static coverage map from test decorators:

```bash
python -m coverage_agent analyze --tests tests --output reports/coverage_map.json
```

2. Discover the live page surface. The scraper progressively scrolls through
   the route, continuously captures `data-testid`, `data-test`, and `data-qa`
   attributes, records same-site `/api/` traffic, and applies
   `playwright-stealth` before creating browser pages:

```bash
python -m coverage_agent discover --base-url https://automationexercise.com --path /login
```

For documentation-backed APIs, use `--file` instead of `--path`. The file name
is resolved under `coverage_agent/plugins/documentation_sources/` and parsed by
the plugin selected from `--base-url`:

```bash
python -m coverage_agent discover --base-url https://reqres.in --file reqres_in.html
```

When `--base-url` is omitted, discovery uses `BASE_URL` from `.env`. Discovery
creates or reuses `tests/websites/<hostname>/` with `suite_config.py` and the
standard `api/`, `ui/`, `smoke/`, `performance/`, `security/`, and `generated/`
packages.

Use `--auth-state` to load a Playwright storage-state file and `--save-state`
to save the resulting session. Tune dynamic-page scanning with
`--scan-distance`, `--step-delay-ms`, `--sniff-interval-ms`, and
`--max-scan-steps`. Security interstitials are detected before scanning and
wait up to 15 seconds by default; override that bound with
`--challenge-timeout-ms`.

The application map records challenge handling as `not_detected`, `cleared`,
or `unresolved`. An unresolved challenge prevents surface harvesting, writes
`scan_status: blocked_by_security_challenge`, and makes `discover` return exit
code `2` instead of publishing a misleading empty scan.

Targets still attached at the final scan are classified as `deterministic`.
Targets harvested during the scan but absent from the final DOM are classified
as `ephemeral`, which covers temporary banners, recycled virtual-DOM rows, and
animation-driven widgets. The application map stores this in
`ui_element_presence` while retaining the existing target lists.

### API Discovery Plugins

The `coverage_agent` uses a plugin-based architecture for API discovery. Website-specific scrapers are located in the `coverage_agent/plugins` directory and are selected based on the `--base-url`. This allows for customized scraping logic for different websites.

The `automationexercise.com` plugin, for example, is designed to parse the API documentation on the `/api_list` page, including scenario titles, request parameters, response codes, and response messages. Distinct scenarios for the same method and path, such as valid and invalid `POST /api/verifyLogin` flows, are preserved as separate discovered API entries.

The `reqres.in` plugin supports both live page discovery and documentation-file
discovery from `coverage_agent/plugins/documentation_sources/reqres_in.html`.
Its parser extracts endpoint cards from the documentation markup, including
request bodies, explicit response status codes, response JSON payloads, and
curl samples when present.

3. Compare discovered targets with decorated tests:

```bash
python -m coverage_agent gaps
```

The report is written to `reports/gap_report.json`.
API gaps are emitted with their full scenario metadata when available, so multiple documented outcomes for the same endpoint remain distinct in the report instead of collapsing to one `METHOD /path` entry.

4. Scaffold executable checks for supported UI and API gaps:

```bash
python -m coverage_agent scaffold-gaps
```

The gap report's `base_url` selects the website suite automatically. For
example, Automation Exercise output is written to
`tests/websites/automationexercise_com/generated/test_generated_coverage_gaps_ui.py`
or `tests/websites/reqres_in/generated/test_generated_coverage_gaps_api.py`.
Use `--output` only when a custom location is required. Supported UI templates
and all API gaps generate executable tests with literal `@covers` decorators.
Generated API tests keep the discovered scenario title and request parameters as
comments, which is useful when one endpoint has multiple documented behaviors.
Generated UI tests now persist the discovered element snapshot and assert that
the observed element metadata still matches at runtime, not just that the
locator is visible.

Generated UI scaffolding also drops stale discovery artifacts when the live
target no longer exposes a stable element to test. In practice this applies to
cases such as hidden mobile-only containers that were captured during
discovery, but later cannot be located again by `data-testid`, role,
`aria-label`, id, href, or simple text/tag fallback. Those entries are omitted
from regenerated output instead of producing permanent skipped tests.

Generated test modules keep only imports, constants, decorators, and test
functions. Helper logic is written into sibling modules such as
`_test_generated_coverage_gaps_ui_helpers.py` and
`_test_generated_coverage_gaps_api_helpers.py`. Large request and response
payload snapshots, and saved UI element snapshots, are written into sibling
JSON data files such as `_test_generated_coverage_gaps_api_data.json` or
`_test_generated_coverage_gaps_ui_data.json` instead of being inlined into the
Python test modules.

For ReqRes record-by-id cases, generated decorators and request metadata use a
placeholder such as `{record_id_filled_during_test}` instead of the example id
from the documentation. The live test creates a disposable record first and
replaces that placeholder with the real id before issuing the documented
`GET`, `PUT`, or `DELETE` request.

5. Review and execute the generated tests against the live target:

Windows PowerShell:

```powershell
pytest tests/websites/automationexercise_com/generated
```

Linux:

```bash
pytest tests/websites/automationexercise_com/generated
```

6. Regenerate metadata and confirm the result:

```bash
python -m coverage_agent analyze
python -m coverage_agent gaps
```

Do not treat generated assertions as permanent coverage until they have passed
against the intended environment and their behavior matches the product
contract.

### Current Login Map

The current `reports/application_map.json` describes `/login` with six UI
targets and no observed API requests:

```json
{
  "page": "/login",
  "discovered_ui_elements": [
    "login-button",
    "login-email",
    "login-password",
    "signup-button",
    "signup-email",
    "signup-name"
  ],
  "discovered_api_endpoints": []
}
```

After covering `login-email` and `login-password` with
`test_login_fields_enforce_input_constraints`, the current result is:

```text
UI: 100.0% (6/6)
API: 100.0% (0/0)
```

### Templates and Selection

Page manifests in `config/test_manifests.json` bind discovered targets to
reusable templates and `feature:*` groups. Assemble and select suites with:

```bash
python -m coverage_agent assemble --application reports/application_map.json
python -m coverage_agent indexes
python -m coverage_agent select --template FormValidationTemplate
python -m coverage_agent select --page /login --feature feature:authentication
```

Unbound targets receive complementary template recommendations. For example,
`subscription-form` maps to form validation and submission templates, while
`discount-code` maps to input validation and coupon API templates.

### Website Suites

Provider tests are grouped by hostname:

```text
tests/websites/
  automationexercise_com/
  reqres_in/
  saucedemo_com/
  toptal_com/
```

Every website package has `suite_config.py` and consistent `api/`, `ui/`,
`smoke/`, `performance/`, `security/`, and `generated/` directories.
Generated suites use the `BASE_URL` defined in their own `suite_config.py`.
That keeps each suite bound to one target instead of allowing ad hoc runtime
overrides. Shared generic consent helpers live in `tests/websites/helpers.py`,
and site-specific helper modules may be added when a provider needs custom
behavior, as with Sabre's OneTrust handling.

Each website suite also includes:

- performance tests for:
  - transport response time
  - browser navigation timing metrics
  - throttled mobile render timing
- security tests for:
  - reflected XSS execution resistance
  - HTTP security response headers

Each smoke suite contains two critical checks:

- `test_backend_gateway_health` uses Playwright's request context and does not
  launch a browser. It requires the configured status within 5 seconds.
- `test_homepage_shell_renders` requires navigation within 8 seconds and the
  configured application-shell selector to become visible within 5 seconds.

Successful smoke checks print a `SMOKE DIAGNOSTICS` JSON block even with
pytest output capture enabled. It includes the request method, final URL, HTTP
status, elapsed milliseconds, response headers, and selector/status
expectations. Credential-bearing
headers such as `authorization`, `cookie`, API keys, and tokens are redacted.

All repository tests also publish a final `TEST DIAGNOSTICS` JSON block. It is
written to the pytest terminal stream and added to the individual test's report
sections, so IDE test runners such as IntelliJ/PyCharm can show it when that
test is selected. A separate `test-log` section contains
per-test `loguru` output. The diagnostics payload contains the test node ID,
outcome, duration, markers, and any captured HTTP or browser events. Shared
HTTPX clients record request URLs, sanitized request and response headers,
statuses, and elapsed time. Request and response payloads are also captured for
improved debugging. Tests without network or browser activity still report
their duration, markers, and result.

For quieter full-repository runs, suppress only terminal diagnostics while
keeping HTML and report-section diagnostics intact:

```bash
pytest --quiet-diagnostics
```

or:

```bash
TERMINAL_DIAGNOSTICS=false pytest
```

When both are present, `--quiet-diagnostics` wins.

Configure these safeguards in each website's `suite_config.py`. Most generated
suites use these defaults directly, but site-specific plugins may replace some
tests with custom code and stop relying on every setting listed below.

Common settings:

- smoke:
  - `SMOKE_HEALTH_PATH`
  - `SMOKE_HEALTH_STATUS`
  - `SMOKE_ROOT_PATH`
  - `SMOKE_ROOT_SELECTOR`
- performance:
  - `PERFORMANCE_MAX_RESPONSE_MS`
  - `PERFORMANCE_MAX_TTFB_MS`
  - `PERFORMANCE_MAX_LOAD_MS`
  - `PERFORMANCE_WARMUP_RUNS`
  - `PERFORMANCE_SAMPLE_COUNT`

Generic suites additionally use:

- performance routes and selectors:
  - `PERF_HOME_PATH`
  - `PERF_HOME_READY_SELECTOR`
  - `PERF_MOBILE_PATH`
  - `PERF_MOBILE_READY_SELECTOR`
- security routes and selectors:
  - `SECURITY_SEARCH_PATH`
  - `SECURITY_SEARCH_INPUT_SELECTOR`
  - `SECURITY_SEARCH_SUBMIT_SELECTOR`
  - `SECURITY_CONSENT_*`

The defaults probe `/`; replace `SMOKE_HEALTH_PATH` with a dedicated endpoint
such as `/api/v1/health` when the application provides one.

### One-Shot Templates

Reusable live-target templates are available under `tests/one_shot/`:

- `test_smoke.py`
- `test_performance.py`
- `test_security.py`

These are intended to be copied into a dedicated website suite and adjusted for
that site's selectors and routes. They use `BASE_URL` from `.env` by default,
or `--target-url` when you want to probe a one-off environment without editing
the suite. Optional `ONE_SHOT_*` environment variables allow quick
experimentation without editing the files.

Run only API tests:

```bash
pytest -m api
```

Run only UI tests:

```bash
pytest -m ui
```

Run human-readable BDD scenarios:

```bash
pytest -m bdd
```

Run deterministic API contract tests without external network access:

```bash
pytest -m "api and not integration"
```

Run live SauceDemo and ReqRes tests after setting `REQRES_API_KEY`:

```bash
pytest -m "e2e or integration"
```

On PowerShell:

```powershell
$env:REQRES_API_KEY = "your-key"
pytest -m "e2e or integration"
```

Run the Automation Exercise API-to-UI negative path:

```bash
pytest -m hybrid
```

Create the initial Automation Exercise visual baseline:

```bash
UPDATE_VISUAL_BASELINES=true pytest -m visual
```

Subsequent visual runs compare changed pixels against a 1% tolerance:

```bash
pytest -m visual
```

## Structure

```text
api_clients/                 Async API clients and endpoint wrappers
config/
  settings.py                Environment and runtime settings
  test_manifests.json        Page, feature, target, and template bindings
coverage_agent/
  analyzer.py                Static @covers extraction and reverse indexes
  blueprints.py              Reusable test templates and recommendations
  decorators.py              Runtime @covers metadata
  discovery.py               Playwright UI/API discovery and challenge handling
  gap_analysis.py            Coverage correlation, errors, and warnings
  gap_scaffolder.py          Executable generated gap tests
  manifests.py               Test-manifest loading and validation
  plugins/                   Website-specific API discovery plugins
    __init__.py
    base.py
    automationexercise.py
    reqres.py
    documentation_sources/   Static documentation snapshots for file-backed discovery
  suite_layout.py            Website package and smoke/performance/security scaffolding
  template_engine.py         Dynamic suite assembly and test selection
  __main__.py                coverage_agent command-line entry point
data/                        Test data and visual baselines
pages/                       Generic async and synchronous Playwright page objects
schemas/                     JSON Schema API contracts
tests/
  api/                       Provider-neutral mocked API contracts
  features/
    authentication/          Feature configuration, UI, and BDD login tests
  unit/                      Deterministic framework and agent tests
  one_shot/                  Copyable smoke, performance, and security templates
  websites/
    helpers.py               Shared generic helpers for website suites
    automationexercise_com/  API, UI, smoke, performance, security, generated tests
      helpers.py             Automation Exercise page objects and selector helpers
    reqres_in/               API, smoke, performance, security, generated tests
    saucedemo_com/           UI, BDD, smoke, performance, security, generated tests
      helpers.py             SauceDemo page objects and selector helpers
    sabre_com/               Smoke, performance, security, generated tests
      helpers.py             Sabre consent-handling helpers
    toptal_com/              Smoke, performance, security, generated tests
utils/                       Reporting, logging, mocks, schema, and visual helpers
```

Generated runtime output:

- `reports/pytest-html/<timestamp>-<random-name>.html`: immutable HTML report runs
- `reports/pytest-html/latest.txt`: absolute path of the newest generated report
- `reports/`: coverage maps, gap reports, traces, screenshots, and videos
- `logs/`: framework execution logs

Root configuration:

- `conftest.py`: shared fixtures, URL overrides, artifacts, and pytest-html configuration
- `pytest.ini`: test discovery, markers, and asyncio settings
- `.env` / `.env.example`: local runtime configuration and documented defaults

## Integration Boundary

SauceDemo does not provide a documented public API for creating orders or obtaining authenticated browser sessions. ReqRes and SauceDemo are unrelated systems, so the framework deliberately does not pretend that ReqRes data can prepare SauceDemo state. Automation Exercise exposes both a supported account API and UI, so it is used for the real hybrid flow: create a unique account through the API, verify duplicate-email handling in the UI, and delete the account during cleanup.
