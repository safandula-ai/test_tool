# Test Framework Scaffold

Modular UI and API test framework built around `pytest`, async `Playwright`, `httpx`, `jsonschema`, `allure-pytest`, `python-dotenv`, and `loguru`.

The example integrations target SauceDemo for browser E2E coverage, ReqRes for paginated API contract testing, and Automation Exercise for same-system API/UI hybrid testing.

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and adjust the target URLs.
4. Install Playwright browsers with `playwright install`.

## Environment Setup

The framework reads configuration from environment variables and `.env` files.

- `ENV`: `local`, `staging`, or `prod`
- `BASE_URL`: UI target base URL
- `API_BASE_URL`: API target base URL
- `HEADLESS`: run browser headless when `true`
- `TRACE_ON_FAILURE`: enable trace capture for failed UI tests
- `REQRES_API_KEY`: required by ReqRes for live API requests
- `RUN_LIVE_TESTS`: opt in to tests that call external services
- `AUTOMATION_EXERCISE_BASE_URL`: UI and API base URL for advanced tests
- `UPDATE_VISUAL_BASELINES`: create or replace visual regression baselines

## Running Tests

Run all tests:

```bash
pytest
```

## Allure Reporting

`allure-pytest` is installed through `requirements.txt` and collects test
results. The separate Allure CLI is required to render or open the HTML report.

The Python virtual environment does not provide the `allure` executable. On
Windows, install a Java runtime and the standalone CLI. This machine has
`winget`, so Java can be installed with:

```powershell
winget install --id EclipseAdoptium.Temurin.17.JRE --exact
```

Then download the latest `allure-*.zip` from the official Allure releases,
extract it, and add its `bin` directory to the user `PATH`:

https://github.com/allure-framework/allure2/releases

For example, if extracted to `C:\Tools\allure`:

```powershell
$allureBin = "C:\Tools\allure\bin"
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";" + $allureBin,
  "User"
)
```

Close and reopen PowerShell after changing `PATH`, then verify both commands:

```powershell
java -version
allure --version
```

Do not prefix Allure commands with `python`. `allure` is a standalone command,
not a Python module.

Run tests and replace previous Allure results:

```powershell
pytest --alluredir=allure-results --clean-alluredir
```

Generate a temporary report and open it in a browser:

```powershell
allure serve allure-results
```

Generate and open a persistent report in `allure-report/`:

```powershell
allure generate allure-results --clean -o allure-report
allure open allure-report
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

```powershell
python -m coverage_agent analyze --tests tests --output reports/coverage_map.json
```

2. Discover the live page surface. The scraper progressively scrolls through
   the route, continuously captures `data-testid`, `data-test`, and `data-qa`
   attributes, records same-site `/api/` traffic, and applies
   `playwright-stealth` before creating browser pages:

```powershell
python -m coverage_agent discover --base-url https://automationexercise.com --path /login
```

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

3. Compare discovered targets with decorated tests:

```powershell
python -m coverage_agent gaps
```

The report is written to `reports/gap_report.json`. A missing entry resembles:

```text
ERROR UI login-email (deterministic) -> InputValidationTemplate
WARNING UI temporary-toast (ephemeral) -> ComponentVisibilityTemplate
```

Deterministic UI gaps and all API gaps are added to `errors`, and the command
returns exit code `1`. Ephemeral UI gaps are added to `warnings`, receive the
same blueprint recommendations, and do not fail the build.

4. Scaffold executable checks for supported UI gaps:

```powershell
python -m coverage_agent scaffold-gaps `
  --base-url-setting automation_exercise_base_url
```

This replaces only `tests/generated/test_generated_coverage_gaps.py`. Supported
UI templates generate executable Playwright assertions and literal `@covers`
decorators. API and domain-specific gaps generate `todo_generated_*` functions
without active decorators, so unfinished placeholders cannot falsely close a
gap.

5. Review and execute the generated tests against the live target:

```powershell
$env:RUN_LIVE_TESTS = "true"
pytest tests/generated/test_generated_coverage_gaps.py
```

6. Regenerate metadata and confirm the result:

```powershell
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

```powershell
python -m coverage_agent assemble --application reports/application_map.json
python -m coverage_agent indexes
python -m coverage_agent select --template FormValidationTemplate
python -m coverage_agent select --page /login --feature feature:authentication
```

Unbound targets receive complementary template recommendations. For example,
`subscription-form` maps to form validation and submission templates, while
`discount-code` maps to input validation and coupon API templates.

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
RUN_LIVE_TESTS=true pytest -m "e2e or integration"
```

On PowerShell:

```powershell
$env:RUN_LIVE_TESTS = "true"
$env:REQRES_API_KEY = "your-key"
pytest -m "e2e or integration"
```

Run the Automation Exercise API-to-UI negative path:

```bash
RUN_LIVE_TESTS=true pytest -m hybrid
```

Create the initial Automation Exercise visual baseline:

```bash
RUN_LIVE_TESTS=true UPDATE_VISUAL_BASELINES=true pytest -m visual
```

Subsequent visual runs compare changed pixels against a 1% tolerance:

```bash
RUN_LIVE_TESTS=true pytest -m visual
```

## Structure

- `api_clients/`: asynchronous HTTP clients and endpoint signatures
- `coverage_agent/`: coverage discovery, analysis, templates, and CLI
- `coverage_agent/analyzer.py`: AST extraction and coverage indexes
- `coverage_agent/blueprints.py`: reusable template definitions and matching rules
- `coverage_agent/decorators.py`: `@covers` runtime metadata
- `coverage_agent/discovery.py`: Playwright UI and API surface discovery
- `coverage_agent/gap_analysis.py`: application-to-test coverage correlation
- `coverage_agent/gap_scaffolder.py`: generated tests for supported gaps
- `coverage_agent/manifests.py`: page and feature manifest validation
- `coverage_agent/template_engine.py`: dynamic suite assembly and test selection
- `config/settings.py`: environment and runtime settings
- `config/test_manifests.json`: page, feature, target, and template associations
- `pages/`: asynchronous and synchronous Playwright page objects
- `schemas/`: JSON Schema API contracts
- `tests/api/`: API and contract tests
- `tests/ui/`: UI, accessibility, visual, hybrid, and E2E tests
- `tests/bdd/`: Gherkin scenarios and synchronous Playwright steps
- `tests/unit/`: deterministic coverage-agent tests
- `tests/generated/`: gap tests created on demand by `scaffold-gaps`
- `utils/`: logging, mocks, test data, schema, and visual helpers
- `reports/application_map.json`: latest discovered application surface
- `reports/coverage_map.json`: target-indexed `@covers` metadata
- `reports/coverage_indexes.json`: page, feature, and template reverse indexes
- `reports/gap_report.json`: latest metrics and missing coverage targets

## Integration Boundary

SauceDemo does not provide a documented public API for creating orders or obtaining authenticated browser sessions. ReqRes and SauceDemo are unrelated systems, so the framework deliberately does not pretend that ReqRes data can prepare SauceDemo state. Automation Exercise exposes both a supported account API and UI, so it is used for the real hybrid flow: create a unique account through the API, verify duplicate-email handling in the UI, and delete the account during cleanup.
