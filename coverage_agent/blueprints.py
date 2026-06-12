"""Blueprint names and recommendation rules for uncovered targets."""

from __future__ import annotations

from enum import StrEnum


class Blueprint(StrEnum):
    API_CONTRACT = "APIContractTemplate"
    COMPONENT_VISIBILITY = "ComponentVisibilityTemplate"
    FORM_VALIDATION = "FormValidationTemplate"
    INTERACTION = "InteractionTemplate"


def recommend_blueprint(target: str, coverage_type: str) -> str:
    """Return the most appropriate test blueprint for a target signature."""
    if coverage_type == "api":
        return Blueprint.API_CONTRACT

    normalized = target.lower()
    if any(token in normalized for token in ("btn", "button", "submit", "click")):
        return Blueprint.INTERACTION
    if any(token in normalized for token in ("input", "form", "field", "email", "password")):
        return Blueprint.FORM_VALIDATION
    return Blueprint.COMPONENT_VISIBILITY
