from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from scipy.stats import norm

from .economics import (
    EconomicsConfig,
    annual_cost_savings,
    annual_incremental_serving_cost,
    effective_allowed_loss,
    required_lift_for_break_even,
)
from .inference import ProportionEffect


class LaunchDecision(str, Enum):
    SHIP = "SHIP"
    REJECT = "REJECT"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class PolicyResult:
    policy: str
    decision: LaunchDecision
    threshold: float
    estimate: float
    lower_bound: float
    upper_bound: float
    rationale: str


def _validate_confidence(confidence: float) -> None:
    if not 0.5 < confidence < 1.0:
        raise ValueError("confidence must be between 0.5 and 1.0.")


def one_sided_bounds(
    effect: ProportionEffect,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return symmetric one-sided confidence bounds using the estimate's SE."""
    _validate_confidence(confidence)
    z = norm.ppf(confidence)
    margin = z * effect.standard_error
    return effect.absolute_effect - margin, effect.absolute_effect + margin


def _threshold_policy(
    *,
    name: str,
    effect: ProportionEffect,
    threshold: float,
    confidence: float,
    rationale: str,
) -> PolicyResult:
    lower, upper = one_sided_bounds(effect, confidence)

    if lower > threshold:
        decision = LaunchDecision.SHIP
    elif upper < threshold:
        decision = LaunchDecision.REJECT
    else:
        decision = LaunchDecision.INCONCLUSIVE

    return PolicyResult(
        policy=name,
        decision=decision,
        threshold=threshold,
        estimate=effect.absolute_effect,
        lower_bound=lower,
        upper_bound=upper,
        rationale=rationale,
    )


def statistical_superiority_policy(
    effect: ProportionEffect,
    confidence: float = 0.95,
) -> PolicyResult:
    return _threshold_policy(
        name="statistical_superiority",
        effect=effect,
        threshold=0.0,
        confidence=confidence,
        rationale="Requires evidence that treatment effect is above zero.",
    )


def practical_significance_policy(
    effect: ProportionEffect,
    practical_threshold: float,
    confidence: float = 0.95,
) -> PolicyResult:
    return _threshold_policy(
        name="practical_significance",
        effect=effect,
        threshold=practical_threshold,
        confidence=confidence,
        rationale="Requires evidence that effect exceeds a predeclared practical threshold.",
    )


def economic_break_even_policy(
    effect: ProportionEffect,
    economics: EconomicsConfig,
    confidence: float = 0.95,
) -> PolicyResult:
    threshold = required_lift_for_break_even(economics)
    return _threshold_policy(
        name="economic_break_even",
        effect=effect,
        threshold=threshold,
        confidence=confidence,
        rationale="Requires evidence that conversion lift exceeds economic break-even.",
    )


def non_inferiority_savings_policy(
    effect: ProportionEffect,
    economics: EconomicsConfig,
    confidence: float = 0.95,
) -> PolicyResult:
    savings = annual_cost_savings(economics)
    if savings <= 0:
        return PolicyResult(
            policy="non_inferiority_savings",
            decision=LaunchDecision.REJECT,
            threshold=0.0,
            estimate=effect.absolute_effect,
            lower_bound=one_sided_bounds(effect, confidence)[0],
            upper_bound=one_sided_bounds(effect, confidence)[1],
            rationale="Candidate has no serving-cost savings, so savings-based non-inferiority does not apply.",
        )

    threshold = -effective_allowed_loss(economics)
    return _threshold_policy(
        name="non_inferiority_savings",
        effect=effect,
        threshold=threshold,
        confidence=confidence,
        rationale="Requires evidence that quality loss stays within the stricter economic/product margin.",
    )


def risk_adjusted_expected_value_policy(
    effect: ProportionEffect,
    economics: EconomicsConfig,
    confidence: float = 0.95,
) -> PolicyResult:
    """Convert effect uncertainty into annual-value uncertainty.

    With a linear value model, the economic zero-value boundary maps exactly to
    the break-even treatment-effect threshold. This policy reports decisions in
    value terms and is kept distinct because later milestones can attach richer
    utility/risk models without changing the interface.
    """
    _validate_confidence(confidence)
    lower_effect, upper_effect = one_sided_bounds(effect, confidence)

    scale = economics.annual_traffic * economics.value_per_conversion
    incremental_cost = annual_incremental_serving_cost(economics)

    lower_value = lower_effect * scale - incremental_cost
    upper_value = upper_effect * scale - incremental_cost
    estimate_value = effect.absolute_effect * scale - incremental_cost

    if lower_value > 0:
        decision = LaunchDecision.SHIP
    elif upper_value < 0:
        decision = LaunchDecision.REJECT
    else:
        decision = LaunchDecision.INCONCLUSIVE

    return PolicyResult(
        policy="risk_adjusted_expected_value",
        decision=decision,
        threshold=0.0,
        estimate=estimate_value,
        lower_bound=lower_value,
        upper_bound=upper_value,
        rationale="Requires the one-sided annual-value interval to lie wholly above or below zero.",
    )
