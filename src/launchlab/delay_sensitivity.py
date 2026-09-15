from __future__ import annotations

from dataclasses import dataclass, replace

from .economics import EconomicsConfig
from .risk_adjustment import run_probability_risk_benchmark


@dataclass(frozen=True)
class DelaySensitivityPoint:
    treatment_effect: float
    inconclusive_cost: float
    minimum_positive_value_probability: float
    correct_decision_rate: float
    harmful_launch_rate: float
    missed_opportunity_rate: float
    inconclusive_rate: float
    mean_regret: float


@dataclass(frozen=True)
class DelayCostOptimum:
    treatment_effect: float
    inconclusive_cost: float
    minimum_positive_value_probability: float
    mean_regret: float


def run_delay_cost_sensitivity(
    *,
    n_users: int,
    baseline_conversion: float,
    treatment_effect: float,
    economics: EconomicsConfig,
    inconclusive_costs: list[float],
    probability_thresholds: list[float],
    seeds_per_threshold: int = 100,
) -> list[DelaySensitivityPoint]:
    if not inconclusive_costs:
        raise ValueError("inconclusive_costs must not be empty.")
    if not probability_thresholds:
        raise ValueError("probability_thresholds must not be empty.")
    if any(cost < 0 for cost in inconclusive_costs):
        raise ValueError("inconclusive costs must be non-negative.")

    rows: list[DelaySensitivityPoint] = []

    for inconclusive_cost in inconclusive_costs:
        scenario_economics = replace(
            economics,
            inconclusive_cost=inconclusive_cost,
        )
        aggregates = run_probability_risk_benchmark(
            n_users=n_users,
            baseline_conversion=baseline_conversion,
            treatment_effect=treatment_effect,
            economics=scenario_economics,
            probability_thresholds=probability_thresholds,
            seeds_per_threshold=seeds_per_threshold,
        )

        for aggregate in aggregates:
            rows.append(
                DelaySensitivityPoint(
                    treatment_effect=treatment_effect,
                    inconclusive_cost=inconclusive_cost,
                    minimum_positive_value_probability=(
                        aggregate.minimum_positive_value_probability
                    ),
                    correct_decision_rate=aggregate.correct_decision_rate,
                    harmful_launch_rate=aggregate.harmful_launch_rate,
                    missed_opportunity_rate=aggregate.missed_opportunity_rate,
                    inconclusive_rate=aggregate.inconclusive_rate,
                    mean_regret=aggregate.mean_regret,
                )
            )

    return rows


def select_minimum_regret_thresholds(
    rows: list[DelaySensitivityPoint],
) -> list[DelayCostOptimum]:
    if not rows:
        raise ValueError("rows must not be empty.")

    grouped: dict[tuple[float, float], list[DelaySensitivityPoint]] = {}
    for row in rows:
        grouped.setdefault(
            (row.treatment_effect, row.inconclusive_cost),
            [],
        ).append(row)

    output: list[DelayCostOptimum] = []
    for (treatment_effect, inconclusive_cost), group in sorted(grouped.items()):
        best = min(
            group,
            key=lambda row: (
                row.mean_regret,
                row.minimum_positive_value_probability,
            ),
        )
        output.append(
            DelayCostOptimum(
                treatment_effect=treatment_effect,
                inconclusive_cost=inconclusive_cost,
                minimum_positive_value_probability=(
                    best.minimum_positive_value_probability
                ),
                mean_regret=best.mean_regret,
            )
        )

    return output
