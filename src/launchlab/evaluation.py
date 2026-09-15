from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .economics import EconomicsConfig, OptimalAction, economic_regret, optimal_action
from .experiment import ExperimentConfig
from .inference import estimate_proportion_effect
from .policies import (
    LaunchDecision,
    PolicyResult,
    economic_break_even_policy,
    non_inferiority_savings_policy,
    practical_significance_policy,
    risk_adjusted_expected_value_policy,
    statistical_superiority_policy,
)
from .simulation import simulate_experiment


@dataclass(frozen=True)
class BenchmarkScenario:
    name: str
    n_users: int
    baseline_conversion: float
    treatment_effect: float
    economics: EconomicsConfig
    practical_threshold: float = 0.001


@dataclass(frozen=True)
class PolicyAggregate:
    scenario: str
    policy: str
    runs: int
    correct_decision_rate: float
    harmful_launch_rate: float
    missed_opportunity_rate: float
    inconclusive_rate: float
    mean_regret: float


def _policy_results(
    effect,
    economics: EconomicsConfig,
    practical_threshold: float,
) -> list[PolicyResult]:
    results = [
        statistical_superiority_policy(effect),
        practical_significance_policy(effect, practical_threshold),
        economic_break_even_policy(effect, economics),
        risk_adjusted_expected_value_policy(effect, economics),
    ]

    # Savings-based non-inferiority is only meaningful for a cheaper candidate.
    if economics.candidate_cost_per_request < economics.incumbent_cost_per_request:
        results.append(non_inferiority_savings_policy(effect, economics))

    return results


def run_monte_carlo_benchmark(
    scenarios: Iterable[BenchmarkScenario],
    seeds_per_scenario: int = 100,
) -> list[PolicyAggregate]:
    if seeds_per_scenario <= 0:
        raise ValueError("seeds_per_scenario must be positive.")

    results: list[PolicyAggregate] = []

    for scenario in scenarios:
        policy_names = [
            "statistical_superiority",
            "practical_significance",
            "economic_break_even",
            "risk_adjusted_expected_value",
        ]
        if (
            scenario.economics.candidate_cost_per_request
            < scenario.economics.incumbent_cost_per_request
        ):
            policy_names.append("non_inferiority_savings")
        stats = {
            name: {
                "correct": 0,
                "harmful": 0,
                "missed": 0,
                "inconclusive": 0,
                "regret": 0.0,
            }
            for name in policy_names
        }

        truth = optimal_action(scenario.treatment_effect, scenario.economics)

        for seed in range(seeds_per_scenario):
            experiment = simulate_experiment(
                ExperimentConfig(
                    n_users=scenario.n_users,
                    baseline_conversion=scenario.baseline_conversion,
                    treatment_effect=scenario.treatment_effect,
                    seed=seed,
                )
            )
            c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
            effect = estimate_proportion_effect(c_success, c_n, t_success, t_n)

            for policy_result in _policy_results(
                effect,
                scenario.economics,
                scenario.practical_threshold,
            ):
                s = stats[policy_result.policy]
                decision = policy_result.decision

                if decision is LaunchDecision.INCONCLUSIVE:
                    s["inconclusive"] += 1
                elif truth is OptimalAction.SHIP and decision is LaunchDecision.SHIP:
                    s["correct"] += 1
                elif truth is OptimalAction.REJECT and decision is LaunchDecision.REJECT:
                    s["correct"] += 1
                elif truth is OptimalAction.REJECT and decision is LaunchDecision.SHIP:
                    s["harmful"] += 1
                elif truth is OptimalAction.SHIP and decision is LaunchDecision.REJECT:
                    s["missed"] += 1

                s["regret"] += economic_regret(
                    scenario.treatment_effect,
                    decision.value,
                    scenario.economics,
                )

        for policy_name in policy_names:
            s = stats[policy_name]
            runs = seeds_per_scenario
            results.append(
                PolicyAggregate(
                    scenario=scenario.name,
                    policy=policy_name,
                    runs=runs,
                    correct_decision_rate=s["correct"] / runs,
                    harmful_launch_rate=s["harmful"] / runs,
                    missed_opportunity_rate=s["missed"] / runs,
                    inconclusive_rate=s["inconclusive"] / runs,
                    mean_regret=s["regret"] / runs,
                )
            )

    return results
