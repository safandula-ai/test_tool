"""Reusable test blueprint catalog and pattern matching rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Awaitable, Callable


TemplateRunner = Callable[[Any, "TemplateInvocation"], Awaitable[None]]


class Blueprint(StrEnum):
    API_CONTRACT = "APIContractTemplate"
    APPLIED_COUPON_API = "AppliedCouponAPITemplate"
    AUTH_GATEWAY = "AuthGatewayTemplate"
    COMPONENT_VISIBILITY = "ComponentVisibilityTemplate"
    CRUD_ITEM = "CRUDItemTemplate"
    FORM_VALIDATION = "FormValidationTemplate"
    INPUT_VALIDATION = "InputValidationTemplate"
    INTERACTION = "InteractionTemplate"
    SUBMISSION = "SubmissionTemplate"


@dataclass(frozen=True)
class TemplateDefinition:
    """Definition of a reusable test pattern."""

    name: str
    coverage_type: str
    description: str
    required_parameters: tuple[str, ...] = ()
    runner: TemplateRunner | None = None


@dataclass(frozen=True)
class TemplateInvocation:
    """A template bound to a concrete page target and parameters."""

    template: str
    target: str
    page: str
    feature: str | None
    coverage_type: str
    parameters: dict[str, Any]


async def _component_visibility_runner(page: Any, invocation: TemplateInvocation) -> None:
    locator = page.get_by_test_id(invocation.target)
    await locator.wait_for(state="visible")


async def _interaction_runner(page: Any, invocation: TemplateInvocation) -> None:
    locator = page.get_by_test_id(invocation.target)
    await locator.wait_for(state="visible")
    if not await locator.is_enabled():
        raise AssertionError(f"Target is not actionable: {invocation.target}")


async def _form_validation_runner(page: Any, invocation: TemplateInvocation) -> None:
    locator = page.get_by_test_id(invocation.target)
    await locator.wait_for(state="visible")
    if await locator.get_attribute("required") is not None:
        valid = await locator.evaluate("element => element.checkValidity()")
        if valid:
            raise AssertionError(f"Required field unexpectedly accepts an empty value: {invocation.target}")


DEFAULT_TEMPLATE_CATALOG: dict[str, TemplateDefinition] = {
    Blueprint.API_CONTRACT: TemplateDefinition(
        Blueprint.API_CONTRACT, "api", "Validate status, schema, and required response fields."
    ),
    Blueprint.APPLIED_COUPON_API: TemplateDefinition(
        Blueprint.APPLIED_COUPON_API,
        "api",
        "Validate coupon application, rejection, and calculated totals.",
        ("endpoint",),
    ),
    Blueprint.AUTH_GATEWAY: TemplateDefinition(
        Blueprint.AUTH_GATEWAY,
        "ui",
        "Validate accepted and rejected authentication paths.",
        ("username_target", "password_target", "submit_target"),
    ),
    Blueprint.COMPONENT_VISIBILITY: TemplateDefinition(
        Blueprint.COMPONENT_VISIBILITY,
        "ui",
        "Validate that a component is visible and reachable.",
        runner=_component_visibility_runner,
    ),
    Blueprint.CRUD_ITEM: TemplateDefinition(
        Blueprint.CRUD_ITEM,
        "api",
        "Validate create, read, update, and delete lifecycle behavior.",
        ("create_endpoint", "read_endpoint", "update_endpoint", "delete_endpoint"),
    ),
    Blueprint.FORM_VALIDATION: TemplateDefinition(
        Blueprint.FORM_VALIDATION,
        "ui",
        "Validate required-field and browser constraint behavior.",
        runner=_form_validation_runner,
    ),
    Blueprint.INPUT_VALIDATION: TemplateDefinition(
        Blueprint.INPUT_VALIDATION,
        "ui",
        "Validate boundary, malformed, and empty input values.",
        ("invalid_values",),
    ),
    Blueprint.INTERACTION: TemplateDefinition(
        Blueprint.INTERACTION,
        "ui",
        "Validate that a control is visible and actionable.",
        runner=_interaction_runner,
    ),
    Blueprint.SUBMISSION: TemplateDefinition(
        Blueprint.SUBMISSION,
        "ui",
        "Validate successful submission and observable completion state.",
        ("submit_target", "success_target"),
    ),
}


def recommend_blueprints(target: str, coverage_type: str) -> list[str]:
    """Recommend one or more complementary templates for a target."""
    if coverage_type == "api":
        if any(token in target.lower() for token in ("coupon", "discount", "promo")):
            return [Blueprint.APPLIED_COUPON_API, Blueprint.API_CONTRACT]
        return [Blueprint.API_CONTRACT]

    normalized = target.lower()
    if any(token in normalized for token in ("form", "subscription", "address")):
        return [Blueprint.FORM_VALIDATION, Blueprint.SUBMISSION]
    if any(token in normalized for token in ("discount", "coupon", "promo")):
        return [Blueprint.INPUT_VALIDATION, Blueprint.APPLIED_COUPON_API]
    if any(token in normalized for token in ("input", "field", "email", "password", "code")):
        return [Blueprint.INPUT_VALIDATION, Blueprint.FORM_VALIDATION]
    if any(token in normalized for token in ("btn", "button", "submit", "click")):
        return [Blueprint.INTERACTION]
    return [Blueprint.COMPONENT_VISIBILITY]


def recommend_blueprint(target: str, coverage_type: str) -> str:
    """Return the primary recommendation for backward compatibility."""
    return recommend_blueprints(target, coverage_type)[0]
