"""Dynamic suite assembly and reverse test selection by grouping metadata."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from coverage_agent.blueprints import (
    DEFAULT_TEMPLATE_CATALOG,
    TemplateDefinition,
    TemplateInvocation,
    recommend_blueprints,
)
from coverage_agent.manifests import PageManifest


class TemplateValidationError(ValueError):
    """Raised when a template binding cannot be assembled."""


class TemplateRegistry:
    """Registry of known reusable test blueprints."""

    def __init__(self, definitions: Iterable[TemplateDefinition] = DEFAULT_TEMPLATE_CATALOG.values()):
        self._definitions = {definition.name: definition for definition in definitions}

    def get(self, name: str) -> TemplateDefinition:
        try:
            return self._definitions[name]
        except KeyError:
            raise TemplateValidationError(f"Unknown template: {name}") from None

    def validate(self, invocation: TemplateInvocation) -> None:
        definition = self.get(invocation.template)
        missing = [key for key in definition.required_parameters if key not in invocation.parameters]
        if missing:
            raise TemplateValidationError(
                f"{invocation.template} for {invocation.target} is missing parameters: {', '.join(missing)}"
            )


class DynamicSuiteAssembler:
    """Associate discovered targets with configured or suggested templates."""

    def __init__(self, registry: TemplateRegistry | None = None):
        self.registry = registry or TemplateRegistry()

    def assemble(self, application_map: dict[str, Any], manifests: list[PageManifest]) -> dict[str, Any]:
        page = application_map.get("page", "unknown")
        manifest = next((item for item in manifests if item.page == page), None)
        bindings = {item.target: item for item in manifest.targets} if manifest else {}
        discovered = [
            (target, "ui") for target in application_map.get("discovered_ui_elements", [])
        ] + [
            (target, "api") for target in application_map.get("discovered_api_endpoints", [])
        ]

        invocations: list[TemplateInvocation] = []
        suggestions: list[dict[str, Any]] = []
        for target, coverage_type in discovered:
            binding = bindings.get(target)
            if binding:
                for template in binding.templates:
                    invocation = TemplateInvocation(
                        template=template,
                        target=target,
                        page=page,
                        feature=binding.feature,
                        coverage_type=binding.type,
                        parameters=binding.parameters,
                    )
                    self.registry.validate(invocation)
                    invocations.append(invocation)
            else:
                suggestions.append(
                    {
                        "target": target,
                        "type": coverage_type,
                        "recommended_templates": recommend_blueprints(target, coverage_type),
                    }
                )
        return {
            "page": page,
            "page_name": manifest.name if manifest else None,
            "features": list(manifest.features) if manifest else [],
            "suite": [asdict(invocation) for invocation in invocations],
            "suggestions": suggestions,
        }

    @staticmethod
    def select_tests(
        coverage_map: dict[str, list[dict[str, Any]]],
        *,
        page: str | None = None,
        feature: str | None = None,
        template: str | None = None,
    ) -> list[str]:
        """Return pytest node IDs matching page, feature, and template filters."""
        selected: set[str] = set()
        for entries in coverage_map.values():
            for entry in entries:
                if page is not None and entry.get("page") != page:
                    continue
                if feature is not None and entry.get("feature") != feature:
                    continue
                if template is not None and entry.get("template") != template:
                    continue
                selected.add(f"{entry['file_path']}::{entry['test_function']}")
        return sorted(selected)
