"""Small image comparison layer for Playwright screenshots."""

from __future__ import annotations

from pathlib import Path

from playwright.async_api import Locator, Page


async def assert_visual_match(
    target: Page | Locator,
    baseline: Path,
    actual: Path,
    max_changed_pixel_ratio: float = 0.01,
    update_baseline: bool = False,
) -> None:
    """Compare a screenshot with a baseline using a pixel-change threshold."""
    from PIL import Image, ImageChops

    baseline.parent.mkdir(parents=True, exist_ok=True)
    actual.parent.mkdir(parents=True, exist_ok=True)
    await target.screenshot(path=str(actual), animations="disabled")

    if update_baseline:
        baseline.write_bytes(actual.read_bytes())
        return
    if not baseline.exists():
        raise FileNotFoundError(f"Visual baseline does not exist: {baseline}")

    with Image.open(baseline).convert("RGBA") as expected, Image.open(actual).convert("RGBA") as observed:
        if expected.size != observed.size:
            raise AssertionError(f"Screenshot size changed from {expected.size} to {observed.size}")
        difference = ImageChops.difference(expected, observed).convert("L")
        changed_pixels = sum(1 for pixel in difference.getdata() if pixel > 0)
        changed_ratio = changed_pixels / (expected.width * expected.height)
        if changed_ratio > max_changed_pixel_ratio:
            raise AssertionError(
                f"Visual difference {changed_ratio:.2%} exceeds {max_changed_pixel_ratio:.2%}"
            )
