"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import pytest
from playwright.async_api import expect

from coverage_agent.decorators import covers


DEFAULT_BASE_URL = 'https://www.toptal.com'

pytestmark = [
    pytest.mark.ui,
    pytest.mark.asyncio,
]


def _target(page, name: str):
    escaped = name.replace('"', '\"')
    return page.locator(
        f'[data-testid="{escaped}"], [data-test="{escaped}"], [data-qa="{escaped}"]'
    ).first


async def _assert_input_validation(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_editable()
    input_type = (await target.get_attribute("type") or "text").lower()
    await target.fill("not-a-valid-value")
    if input_type in {"email", "url", "number"}:
        assert not await target.evaluate("element => element.checkValidity()")
    else:
        assert await target.input_value() == "not-a-valid-value"


async def _assert_interaction(target) -> None:
    await expect(target).to_be_visible()
    await expect(target).to_be_enabled()


@covers(type="ui", target="author-label", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_author_label(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "author-label")
        await expect(target).to_be_visible()


@covers(type="ui", target="avatar", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_avatar(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "avatar")
        await expect(target).to_be_visible()


@covers(type="ui", target="benefit-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_benefit_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "benefit-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="blockquote", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_blockquote(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "blockquote")
        await expect(target).to_be_visible()


@covers(type="ui", target="blog-card", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_blog_card(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "blog-card")
        await expect(target).to_be_visible()


@covers(type="ui", target="blog-card-breadcrumbs", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_blog_card_breadcrumbs(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "blog-card-breadcrumbs")
        await expect(target).to_be_visible()


@covers(type="ui", target="blog-card-link", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_blog_card_link(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "blog-card-link")
        await expect(target).to_be_visible()


@covers(type="ui", target="blog-section-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_blog_section_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "blog-section-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="burger-menu-button", priority="high", template="InteractionTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_burger_menu_button(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "burger-menu-button")
        await _assert_interaction(target)


@covers(type="ui", target="client-script", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_client_script(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "client-script")
        await expect(target).to_be_visible()


@covers(type="ui", target="client-testimonials-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_client_testimonials_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "client-testimonials-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="clients-carousel", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_clients_carousel(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "clients-carousel")
        await expect(target).to_be_visible()


@covers(type="ui", target="clients-grid-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_clients_grid_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "clients-grid-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="close-icon", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_close_icon(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "close-icon")
        await expect(target).to_be_visible()


@covers(type="ui", target="cover-image", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_cover_image(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "cover-image")
        await expect(target).to_be_visible()


@covers(type="ui", target="cover-image-link", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_cover_image_link(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "cover-image-link")
        await expect(target).to_be_visible()


@covers(type="ui", target="emblem", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_emblem(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "emblem")
        await expect(target).to_be_visible()


@covers(type="ui", target="feature-stepper-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_feature_stepper_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "feature-stepper-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="footer", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_footer(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "footer")
        await expect(target).to_be_visible()


@covers(type="ui", target="footer-column-links-list", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_footer_column_links_list(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "footer-column-links-list")
        await expect(target).to_be_visible()


@covers(type="ui", target="footer-column-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_footer_column_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "footer-column-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="hero-cta", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hero_cta(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hero-cta")
        await expect(target).to_be_visible()


@covers(type="ui", target="hero-talent-name", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hero_talent_name(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hero-talent-name")
        await expect(target).to_be_visible()


@covers(type="ui", target="hero-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hero_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hero-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="hire-cta", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hire_cta(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hire-cta")
        await expect(target).to_be_visible()


@covers(type="ui", target="hire-cta-section", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hire_cta_section(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hire-cta-section")
        await expect(target).to_be_visible()


@covers(type="ui", target="hire-cta-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_hire_cta_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "hire-cta-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="nav-container", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_nav_container(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "nav-container")
        await expect(target).to_be_visible()


@covers(type="ui", target="nav-cta", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_nav_cta(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "nav-cta")
        await expect(target).to_be_visible()


@covers(type="ui", target="overlay-outline", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_overlay_outline(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "overlay-outline")
        await expect(target).to_be_visible()


@covers(type="ui", target="pagination", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_pagination(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "pagination")
        await expect(target).to_be_visible()


@covers(type="ui", target="partnership-section-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_partnership_section_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "partnership-section-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="picture", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_picture(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "picture")
        await expect(target).to_be_visible()


@covers(type="ui",
        target="professional-services-section",
        priority="high",
        template="ComponentVisibilityTemplate",
        page='/',
        feature='feature:generated-gap-coverage',
        presence="deterministic")
async def test_generated_ui_professional_services_section(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "professional-services-section")
        await expect(target).to_be_visible()


@covers(type="ui", target="promo-banners-section", priority="high", template="InputValidationTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_promo_banners_section(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "promo-banners-section")
        await _assert_input_validation(target)


@covers(type="ui", target="quote-text", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_quote_text(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "quote-text")
        await expect(target).to_be_visible()


@covers(type="ui", target="read-more-wrapper", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_read_more_wrapper(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "read-more-wrapper")
        await expect(target).to_be_visible()


@covers(type="ui", target="section-links-container", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_section_links_container(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "section-links-container")
        await expect(target).to_be_visible()


@covers(type="ui", target="services-tab", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_services_tab(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "services-tab")
        await expect(target).to_be_visible()


@covers(type="ui", target="skill-categories-section", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_skill_categories_section(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "skill-categories-section")
        await expect(target).to_be_visible()


@covers(type="ui",
        target="skill-categories-section-title",
        priority="high",
        template="ComponentVisibilityTemplate",
        page='/',
        feature='feature:generated-gap-coverage',
        presence="deterministic")
async def test_generated_ui_skill_categories_section_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "skill-categories-section-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="skill-tag", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_skill_tag(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "skill-tag")
        await expect(target).to_be_visible()


@covers(type="ui", target="skip-links", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_skip_links(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "skip-links")
        await expect(target).to_be_visible()


@covers(type="ui", target="step-description", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_step_description(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "step-description")
        await expect(target).to_be_visible()


@covers(type="ui", target="step-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_step_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "step-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="talent-card", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_talent_card(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "talent-card")
        await expect(target).to_be_visible()


@covers(type="ui", target="talent-network-section", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_talent_network_section(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "talent-network-section")
        await expect(target).to_be_visible()


@covers(type="ui",
        target="talent-network-section-title",
        priority="high",
        template="ComponentVisibilityTemplate",
        page='/',
        feature='feature:generated-gap-coverage',
        presence="deterministic")
async def test_generated_ui_talent_network_section_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "talent-network-section-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="talent-tab", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_talent_tab(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "talent-tab")
        await expect(target).to_be_visible()


@covers(type="ui", target="talents-slide", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_talents_slide(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "talents-slide")
        await expect(target).to_be_visible()


@covers(type="ui", target="testimonial", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_testimonial(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "testimonial")
        await expect(target).to_be_visible()


@covers(type="ui", target="testimonials-text", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_testimonials_text(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "testimonials-text")
        await expect(target).to_be_visible()


@covers(type="ui", target="tooltip-trigger", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_tooltip_trigger(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "tooltip-trigger")
        await expect(target).to_be_visible()


@covers(type="ui", target="trustpilot-imf", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_trustpilot_imf(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "trustpilot-imf")
        await expect(target).to_be_visible()


@covers(type="ui", target="usp-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_usp_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "usp-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="vertical-dropdown", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_vertical_dropdown(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "vertical-dropdown")
        await expect(target).to_be_visible()


@covers(type="ui", target="verticals-title", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_verticals_title(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "verticals-title")
        await expect(target).to_be_visible()


@covers(type="ui", target="wordmark", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_wordmark(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "wordmark")
        await expect(target).to_be_visible()


@covers(type="ui", target="wordmarkpng", priority="high", template="ComponentVisibilityTemplate",
        page='/', feature='feature:generated-gap-coverage', presence="deterministic")
async def test_generated_ui_wordmarkpng(page_factory, pytestconfig, settings):
    if not settings.run_live_tests and not pytestconfig.getoption("--target-url"):
        pytest.skip("Set RUN_LIVE_TESTS=true or pass --target-url")
    base_url = pytestconfig.getoption("--target-url") or DEFAULT_BASE_URL
    if base_url is None:
        base_url = getattr(settings, 'base_url')
    async with page_factory(base_url) as browser_page:
        await browser_page.goto('/')
        target = _target(browser_page, "wordmarkpng")
        await expect(target).to_be_visible()
