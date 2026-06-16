"""Generated coverage tests. Regenerate with ``coverage_agent scaffold-gaps``."""

from __future__ import annotations

import pytest

from tests.websites.helpers import require_live_target, resolve_target_url
from tests.websites.toptal_com.suite_config import BASE_URL, MOBILE_USER_AGENT, MOBILE_VIEWPORT

from ._test_generated_coverage_gaps_ui_helpers import (
    assert_attached_or_skip,
    assert_image_present,
    assert_text,
    assert_visible,
    assert_visible_or_skip,
    open_generated_ui_target,
    record_generated_ui_target,
    load_generated_case_data,
)

from coverage_agent.decorators import covers

CASE_DATA = load_generated_case_data(__file__, '_test_generated_coverage_gaps_ui_data.json')


def resolve_generated_ui_case(
    pytestconfig,
    settings,
    case_name: str,
) -> tuple[str, dict[str, object]]:
    require_live_target(pytestconfig, settings)
    base_url = resolve_target_url(
        pytestconfig,
        default_base_url=BASE_URL,
    )
    case_data = CASE_DATA.get(case_name, {})
    expected_snapshot = case_data.get("ui_snapshot", {})
    return base_url, expected_snapshot


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.ui,
]


@covers(
    type="ui",
    target='author-label',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_author_label(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_author_label',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='author-label',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='author-label',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='avatar',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_avatar(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_avatar',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='avatar',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='avatar',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='benefit-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_benefit_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_benefit_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='benefit-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='benefit-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='blockquote',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_blockquote(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_blockquote',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='blockquote',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='blockquote',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='blog-card',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_blog_card(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_blog_card',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='blog-card',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='blog-card',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='blog-card-breadcrumbs',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_blog_card_breadcrumbs(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_blog_card_breadcrumbs',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='blog-card-breadcrumbs',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='blog-card-breadcrumbs',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'blog-card-breadcrumbs')",
        )
        await assert_visible_or_skip(target, 'blog-card-breadcrumbs')


@covers(
    type="ui",
    target='blog-card-link',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_blog_card_link(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_blog_card_link',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='blog-card-link',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='blog-card-link',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='blog-section-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_blog_section_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_blog_section_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='blog-section-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='blog-section-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='burger-menu-button',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_burger_menu_button(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_burger_menu_button',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='burger-menu-button',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='burger-menu-button',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'burger-menu-button')",
        )
        await assert_attached_or_skip(target, 'burger-menu-button')


@covers(
    type="ui",
    target='client-script',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_client_script(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_client_script',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='client-script',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='client-script',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'client-script')",
        )
        await assert_attached_or_skip(target, 'client-script')


@covers(
    type="ui",
    target='client-testimonials-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_client_testimonials_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_client_testimonials_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='client-testimonials-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='client-testimonials-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='clients-carousel',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_clients_carousel(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_clients_carousel',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='clients-carousel',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='clients-carousel',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'clients-carousel')",
        )
        await assert_visible_or_skip(target, 'clients-carousel')


@covers(
    type="ui",
    target='clients-grid-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_clients_grid_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_clients_grid_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='clients-grid-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='clients-grid-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='close-icon',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_close_icon(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_close_icon',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='close-icon',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='close-icon',
            expected_snapshot=expected_snapshot,
            assertion='await assert_visible(target)',
        )
        await assert_visible(target)


@covers(
    type="ui",
    target='cover-image',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_cover_image(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_cover_image',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='cover-image',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='cover-image',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='cover-image-link',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_cover_image_link(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_cover_image_link',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='cover-image-link',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='cover-image-link',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='emblem',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_emblem(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_emblem',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='emblem',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='emblem',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'emblem')",
        )
        await assert_visible_or_skip(target, 'emblem')


@covers(
    type="ui",
    target='feature-stepper-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_feature_stepper_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_feature_stepper_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='feature-stepper-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='feature-stepper-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='footer',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_footer(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_footer',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='footer',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='footer',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='footer-column-links-list',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_footer_column_links_list(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_footer_column_links_list',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='footer-column-links-list',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='footer-column-links-list',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'footer-column-links-list')",
        )
        await assert_visible_or_skip(target, 'footer-column-links-list')


@covers(
    type="ui",
    target='footer-column-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_footer_column_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_footer_column_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='footer-column-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='footer-column-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='hero-cta',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hero_cta(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hero_cta',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hero-cta',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hero-cta',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='hero-talent-name',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hero_talent_name(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hero_talent_name',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hero-talent-name',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hero-talent-name',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='hero-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hero_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hero_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hero-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hero-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='hire-cta',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hire_cta(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hire_cta',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hire-cta',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hire-cta',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'hire-cta')",
        )
        await assert_visible_or_skip(target, 'hire-cta')


@covers(
    type="ui",
    target='hire-cta-section',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hire_cta_section(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hire_cta_section',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hire-cta-section',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hire-cta-section',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'hire-cta-section')",
        )
        await assert_visible_or_skip(target, 'hire-cta-section')


@covers(
    type="ui",
    target='hire-cta-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_hire_cta_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_hire_cta_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='hire-cta-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='hire-cta-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='mobile-nav-item',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_mobile_nav_item(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_mobile_nav_item',
    )
    async with page_factory(
        base_url,
        viewport=MOBILE_VIEWPORT,
        is_mobile=True,
        has_touch=True,
        user_agent=MOBILE_USER_AGENT,
    ) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='mobile-nav-item',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='mobile-nav-item',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'mobile-nav-item')",
        )
        await assert_attached_or_skip(target, 'mobile-nav-item')


@covers(
    type="ui",
    target='nav-container',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_nav_container(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_nav_container',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='nav-container',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='nav-container',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='nav-cta',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_nav_cta(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_nav_cta',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='nav-cta',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='nav-cta',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'nav-cta')",
        )
        await assert_attached_or_skip(target, 'nav-cta')


@covers(
    type="ui",
    target='overlay-outline',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_overlay_outline(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_overlay_outline',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='overlay-outline',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='overlay-outline',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'overlay-outline')",
        )
        await assert_attached_or_skip(target, 'overlay-outline')


@covers(
    type="ui",
    target='pagination',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_pagination(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_pagination',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='pagination',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='pagination',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'pagination')",
        )
        await assert_attached_or_skip(target, 'pagination')


@covers(
    type="ui",
    target='partnership-section-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_partnership_section_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_partnership_section_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='partnership-section-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='partnership-section-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='picture',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_picture(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_picture',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='picture',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='picture',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'picture')",
        )
        await assert_attached_or_skip(target, 'picture')


@covers(
    type="ui",
    target='professional-services-section',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_professional_services_section(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_professional_services_section',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='professional-services-section',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='professional-services-section',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='promo-banners-section',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_promo_banners_section(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_promo_banners_section',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='promo-banners-section',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='promo-banners-section',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='quote-text',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_quote_text(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_quote_text',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='quote-text',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='quote-text',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='read-more-wrapper',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_read_more_wrapper(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_read_more_wrapper',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='read-more-wrapper',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='read-more-wrapper',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'read-more-wrapper')",
        )
        await assert_visible_or_skip(target, 'read-more-wrapper')


@covers(
    type="ui",
    target='section-links-container',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_section_links_container(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_section_links_container',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='section-links-container',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='section-links-container',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'section-links-container')",
        )
        await assert_visible_or_skip(target, 'section-links-container')


@covers(
    type="ui",
    target='services-tab',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_services_tab(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_services_tab',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='services-tab',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='services-tab',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='skill-categories-section',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_skill_categories_section(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_skill_categories_section',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='skill-categories-section',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='skill-categories-section',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'skill-categories-section')",
        )
        await assert_visible_or_skip(target, 'skill-categories-section')


@covers(
    type="ui",
    target='skill-categories-section-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_skill_categories_section_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_skill_categories_section_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='skill-categories-section-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='skill-categories-section-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='skill-tag',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_skill_tag(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_skill_tag',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='skill-tag',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='skill-tag',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='skip-links',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_skip_links(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_skip_links',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='skip-links',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='skip-links',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'skip-links')",
        )
        await assert_visible_or_skip(target, 'skip-links')


@covers(
    type="ui",
    target='step-description',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_step_description(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_step_description',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='step-description',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='step-description',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'step-description')",
        )
        await assert_visible_or_skip(target, 'step-description')


@covers(
    type="ui",
    target='step-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_step_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_step_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='step-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='step-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='talent-card',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talent_card(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talent_card',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talent-card',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talent-card',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='talent-network-section',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talent_network_section(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talent_network_section',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talent-network-section',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talent-network-section',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='talent-network-section-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talent_network_section_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talent_network_section_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talent-network-section-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talent-network-section-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='talent-tab',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talent_tab(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talent_tab',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talent-tab',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talent-tab',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='talent-tabs',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talent_tabs(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talent_tabs',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talent-tabs',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talent-tabs',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'talent-tabs')",
        )
        await assert_attached_or_skip(target, 'talent-tabs')


@covers(
    type="ui",
    target='talents-slide',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_talents_slide(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_talents_slide',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='talents-slide',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='talents-slide',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='testimonial',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_testimonial(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_testimonial',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='testimonial',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='testimonial',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='testimonials-text',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_testimonials_text(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_testimonials_text',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='testimonials-text',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='testimonials-text',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'testimonials-text')",
        )
        await assert_visible_or_skip(target, 'testimonials-text')


@covers(
    type="ui",
    target='tooltip-trigger',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_tooltip_trigger(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_tooltip_trigger',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='tooltip-trigger',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='tooltip-trigger',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'tooltip-trigger')",
        )
        await assert_visible_or_skip(target, 'tooltip-trigger')


@covers(
    type="ui",
    target='trustpilot-imf',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_trustpilot_imf(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_trustpilot_imf',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='trustpilot-imf',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='trustpilot-imf',
            expected_snapshot=expected_snapshot,
            assertion='await assert_image_present(target)',
        )
        await assert_image_present(target)


@covers(
    type="ui",
    target='usp-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_usp_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_usp_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='usp-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='usp-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='vertical-dropdown',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="ephemeral",
)
async def test_generated_ui_vertical_dropdown(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_vertical_dropdown',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='vertical-dropdown',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='vertical-dropdown',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'vertical-dropdown')",
        )
        await assert_visible_or_skip(target, 'vertical-dropdown')


@covers(
    type="ui",
    target='verticals-title',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_verticals_title(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_verticals_title',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='verticals-title',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='verticals-title',
            expected_snapshot=expected_snapshot,
            assertion='await assert_text(target, expected_snapshot.get("text", ""))',
        )
        await assert_text(target, expected_snapshot.get("text", ""))


@covers(
    type="ui",
    target='wordmark',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_wordmark(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_wordmark',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='wordmark',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='wordmark',
            expected_snapshot=expected_snapshot,
            assertion="await assert_visible_or_skip(target, 'wordmark')",
        )
        await assert_visible_or_skip(target, 'wordmark')


@covers(
    type="ui",
    target='wordmarkpng',
    priority="high",
    template="ComponentVisibilityTemplate",
    page='/',
    feature='feature:generated-gap-coverage',
    presence="deterministic",
)
async def test_generated_ui_wordmarkpng(page_factory, pytestconfig, settings, test_diagnostics):

    base_url, expected_snapshot = resolve_generated_ui_case(
        pytestconfig,
        settings,
        'ui_wordmarkpng',
    )
    async with page_factory(base_url) as browser_page:
        target = await open_generated_ui_target(
            browser_page,
            page_path='/',
            target_name='wordmarkpng',
            expected_snapshot=expected_snapshot,
        )
        await record_generated_ui_target(
            test_diagnostics,
            target=target,
            target_name='wordmarkpng',
            expected_snapshot=expected_snapshot,
            assertion="await assert_attached_or_skip(target, 'wordmarkpng')",
        )
        await assert_attached_or_skip(target, 'wordmarkpng')
