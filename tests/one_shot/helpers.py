"""Shared target-resolution helpers for one-shot live website templates."""

from __future__ import annotations

import pytest

from tests.websites.helpers import resolve_target_url


def target_url(pytestconfig, *, default_base_url: str) -> str:
    """Resolve the live target for a one-shot template run."""
    return resolve_target_url(pytestconfig, default_base_url=default_base_url)


def require_live_target(pytestconfig, *, default_base_url: str) -> None:
    """Skip the test when neither `BASE_URL` nor `--target-url` is provided."""
    if not (pytestconfig.getoption("--target-url") or default_base_url):
        pytest.skip("Set BASE_URL or pass --target-url")
