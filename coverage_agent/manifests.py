"""Configuration model for page and feature template associations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ManifestValidationError(ValueError):
    """Raised when a template manifest is structurally invalid."""


@dataclass(frozen=True)
class TargetBinding:
    target: str
    type: str
    templates: tuple[str, ...]
    feature: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PageManifest:
    page: str
    name: str
    features: tuple[str, ...]
    targets: tuple[TargetBinding, ...]


def load_manifests(path: str | Path) -> list[PageManifest]:
    """Load and validate page manifests from JSON."""
    with Path(path).open(encoding="utf-8") as file:
        payload = json.load(file)
    pages = payload.get("pages") if isinstance(payload, dict) else None
    if not isinstance(pages, list):
        raise ManifestValidationError("Manifest must contain a 'pages' list")

    manifests: list[PageManifest] = []
    for page_data in pages:
        if not page_data.get("page") or not page_data.get("name"):
            raise ManifestValidationError("Every page requires 'page' and 'name'")
        bindings: list[TargetBinding] = []
        for target in page_data.get("targets", []):
            templates = target.get("templates", [])
            if not target.get("target") or target.get("type") not in {"ui", "api", "visual"}:
                raise ManifestValidationError(f"Invalid target binding on {page_data['page']}")
            if not templates:
                raise ManifestValidationError(f"Target {target['target']} requires at least one template")
            bindings.append(
                TargetBinding(
                    target=target["target"],
                    type=target["type"],
                    templates=tuple(templates),
                    feature=target.get("feature"),
                    parameters=target.get("parameters", {}),
                )
            )
        manifests.append(
            PageManifest(
                page=page_data["page"],
                name=page_data["name"],
                features=tuple(page_data.get("features", [])),
                targets=tuple(bindings),
            )
        )
    return manifests
