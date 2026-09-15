from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OptimalAction(str, Enum):
    SHIP = "SHIP"
    REJECT = "REJECT"


@dataclass(frozen=True)
class EconomicsConfig:
    annual_traffic: float
    value_per_conversion: float
    incumbent_cost_per_request: float
    candidate_cost_per_request: float
    product_allowed_loss: float = 0.0
    harmful_launch_weight: float = 1.0
    missed_opportunity_weight: float = 1.0
    inconclusive_cost: float = 0.0

    def __post_init__(self) -> None:
        if self.annual_traffic <= 0:
            raise ValueError("annual_traffic must be positive.")
        if self.value_per_conversion <= 0:
            raise ValueError("value_per_conversion must be positive.")
        if self.incumbent_cost_per_request < 0:
            raise ValueError("incumbent_cost_per_request must be non-negative.")
        if self.candidate_cost_per_request < 0:
            raise ValueError("candidate_cost_per_request must be non-negative.")
        if self.product_allowed_loss < 0:
            raise ValueError("product_allowed_loss must be non-negative.")
        if self.harmful_launch_weight <= 0:
            raise ValueError("harmful_launch_weight must be positive.")
        if self.missed_opportunity_weight <= 0:
            raise ValueError("missed_opportunity_weight must be positive.")
        if self.inconclusive_cost < 0:
            raise ValueError("inconclusive_cost must be non-negative.")


def annual_incremental_serving_cost(config: EconomicsConfig) -> float:
    return config.annual_traffic * (
        config.candidate_cost_per_request - config.incumbent_cost_per_request
    )


def annual_cost_savings(config: EconomicsConfig) -> float:
    return -annual_incremental_serving_cost(config)


def required_lift_for_break_even(config: EconomicsConfig) -> float:
    return annual_incremental_serving_cost(config) / (
        config.annual_traffic * config.value_per_conversion
    )


def economic_allowed_loss(config: EconomicsConfig) -> float:
    savings = annual_cost_savings(config)
    if savings <= 0:
        return 0.0

    return savings / (
        config.annual_traffic * config.value_per_conversion
    )


def effective_allowed_loss(config: EconomicsConfig) -> float:
    return min(
        economic_allowed_loss(config),
        config.product_allowed_loss,
    )


def annual_deployment_value(
    true_effect: float,
    config: EconomicsConfig,
) -> float:
    conversion_value = (
        config.annual_traffic
        * true_effect
        * config.value_per_conversion
    )
    return conversion_value - annual_incremental_serving_cost(config)


def violates_product_floor(
    true_effect: float,
    config: EconomicsConfig,
) -> bool:
    return true_effect < -config.product_allowed_loss


def optimal_action(
    true_effect: float,
    config: EconomicsConfig,
) -> OptimalAction:
    if violates_product_floor(true_effect, config):
        return OptimalAction.REJECT

    if annual_deployment_value(true_effect, config) > 0:
        return OptimalAction.SHIP

    return OptimalAction.REJECT


def economic_regret(
    true_effect: float,
    chosen_action: str,
    config: EconomicsConfig,
) -> float:
    """Raw economic regret for SHIP, REJECT, or INCONCLUSIVE.

    INCONCLUSIVE pays the configured delay/continuation cost in addition to the
    opportunity cost of not shipping a truly valuable candidate.
    """
    action = chosen_action.upper()
    value = annual_deployment_value(true_effect, config)
    optimal = optimal_action(true_effect, config)

    if action not in {"SHIP", "REJECT", "INCONCLUSIVE"}:
        raise ValueError("chosen_action must be SHIP, REJECT, or INCONCLUSIVE.")

    if action == optimal.value:
        return 0.0

    if action == "INCONCLUSIVE":
        opportunity_cost = max(value, 0.0) if optimal is OptimalAction.SHIP else 0.0
        return opportunity_cost + config.inconclusive_cost

    if optimal is OptimalAction.SHIP and action == "REJECT":
        return max(value, 0.0)

    if optimal is OptimalAction.REJECT and action == "SHIP":
        return max(-value, 0.0)

    raise RuntimeError("unhandled action combination")


def risk_weighted_loss(
    true_effect: float,
    chosen_action: str,
    config: EconomicsConfig,
) -> float:
    action = chosen_action.upper()
    value = annual_deployment_value(true_effect, config)
    optimal = optimal_action(true_effect, config)

    if action not in {"SHIP", "REJECT", "INCONCLUSIVE"}:
        raise ValueError("chosen_action must be SHIP, REJECT, or INCONCLUSIVE.")

    if action == optimal.value:
        return 0.0

    if action == "INCONCLUSIVE":
        opportunity_cost = max(value, 0.0) if optimal is OptimalAction.SHIP else 0.0
        return (
            config.missed_opportunity_weight * opportunity_cost
            + config.inconclusive_cost
        )

    if optimal is OptimalAction.SHIP and action == "REJECT":
        return config.missed_opportunity_weight * max(value, 0.0)

    if optimal is OptimalAction.REJECT and action == "SHIP":
        return config.harmful_launch_weight * max(-value, 0.0)

    raise RuntimeError("unhandled action combination")
