from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .economics import EconomicsConfig
from .experiment import ExperimentConfig
from .inference import estimate_proportion_effect
from .policies import (
    PolicyResult,
    economic_break_even_policy,
    practical_significance_policy,
    risk_adjusted_expected_value_policy,
    statistical_superiority_policy,
)
from .simulation import simulate_experiment


@dataclass(frozen=True)
class SensitivityPoint:
    sample_size: int
    value_per_conversion: float
    candidate_cost_per_request: float
    practical_threshold: float
    policy: str
    decision: str
    estimate: float
    lower_bound: float
    upper_bound: float
    threshold: float


def run_sensitivity_grid(
    *,
    baseline_conversion: float,
    treatment_effect: float,
    annual_traffic: float,
    incumbent_cost_per_request: float,
    sample_sizes: list[int],
    values_per_conversion: list[float],
    candidate_costs: list[float],
    practical_thresholds: list[float],
    seed: int = 0,
) -> list[SensitivityPoint]:
    if not sample_sizes:
        raise ValueError("sample_sizes must not be empty.")
    if not values_per_conversion:
        raise ValueError("values_per_conversion must not be empty.")
    if not candidate_costs:
        raise ValueError("candidate_costs must not be empty.")
    if not practical_thresholds:
        raise ValueError("practical_thresholds must not be empty.")

    rows: list[SensitivityPoint] = []

    for n_users in sample_sizes:
        if n_users <= 0:
            raise ValueError("sample sizes must be positive.")

        experiment = simulate_experiment(
            ExperimentConfig(
                n_users=n_users,
                baseline_conversion=baseline_conversion,
                treatment_effect=treatment_effect,
                seed=seed,
            )
        )
        c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
        effect = estimate_proportion_effect(c_success, c_n, t_success, t_n)

        for value, cost, practical in product(
            values_per_conversion,
            candidate_costs,
            practical_thresholds,
        ):
            if value <= 0:
                raise ValueError("value_per_conversion must be positive.")
            if cost < 0:
                raise ValueError("candidate costs must be non-negative.")
            if practical < 0:
                raise ValueError("practical thresholds must be non-negative.")

            economics = EconomicsConfig(
                annual_traffic=annual_traffic,
                value_per_conversion=value,
                incumbent_cost_per_request=incumbent_cost_per_request,
                candidate_cost_per_request=cost,
            )

            results: list[PolicyResult] = [
                statistical_superiority_policy(effect),
                practical_significance_policy(effect, practical),
                economic_break_even_policy(effect, economics),
                risk_adjusted_expected_value_policy(effect, economics),
            ]

            for result in results:
                rows.append(
                    SensitivityPoint(
                        sample_size=n_users,
                        value_per_conversion=value,
                        candidate_cost_per_request=cost,
                        practical_threshold=practical,
                        policy=result.policy,
                        decision=result.decision.value,
                        estimate=result.estimate,
                        lower_bound=result.lower_bound,
                        upper_bound=result.upper_bound,
                        threshold=result.threshold,
                    )
                )

    return rows
