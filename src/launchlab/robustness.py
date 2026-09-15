from __future__ import annotations

from dataclasses import dataclass, replace

from .economics import EconomicsConfig
from .evaluation import BenchmarkScenario, PolicyAggregate, run_monte_carlo_benchmark


@dataclass(frozen=True)
class MisspecificationPoint:
    assumed_value_multiplier: float
    assumed_cost_multiplier: float
    policy: str
    correct_decision_rate: float
    harmful_launch_rate: float
    missed_opportunity_rate: float
    inconclusive_rate: float
    mean_regret: float


def run_economic_misspecification_grid(
    scenario: BenchmarkScenario,
    *,
    value_multipliers: list[float],
    cost_multipliers: list[float],
    runs: int,
) -> list[MisspecificationPoint]:
    if runs <= 0:
        raise ValueError("runs must be positive.")
    if not value_multipliers:
        raise ValueError("value_multipliers must not be empty.")
    if not cost_multipliers:
        raise ValueError("cost_multipliers must not be empty.")

    true_economics = scenario.economics
    rows: list[MisspecificationPoint] = []

    for value_mult in value_multipliers:
        if value_mult <= 0:
            raise ValueError("value multipliers must be positive.")
        for cost_mult in cost_multipliers:
            if cost_mult < 0:
                raise ValueError("cost multipliers must be non-negative.")

            assumed = replace(
                true_economics,
                value_per_conversion=true_economics.value_per_conversion * value_mult,
                candidate_cost_per_request=(
                    true_economics.incumbent_cost_per_request
                    + (
                        true_economics.candidate_cost_per_request
                        - true_economics.incumbent_cost_per_request
                    )
                    * cost_mult
                ),
            )

            perturbed = replace(scenario, policy_economics=assumed)
            aggregates = run_monte_carlo_benchmark(
                [perturbed],
                seeds_per_scenario=runs,
            )

            for agg in aggregates:
                rows.append(
                    MisspecificationPoint(
                        assumed_value_multiplier=value_mult,
                        assumed_cost_multiplier=cost_mult,
                        policy=agg.policy,
                        correct_decision_rate=agg.correct_decision_rate,
                        harmful_launch_rate=agg.harmful_launch_rate,
                        missed_opportunity_rate=agg.missed_opportunity_rate,
                        inconclusive_rate=agg.inconclusive_rate,
                        mean_regret=agg.mean_regret,
                    )
                )

    return rows
