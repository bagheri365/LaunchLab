from __future__ import annotations

from dataclasses import dataclass

from .economics import EconomicsConfig, OptimalAction, optimal_action
from .evaluation import BenchmarkScenario, run_monte_carlo_benchmark
from .power import power_for_two_proportions


@dataclass(frozen=True)
class PowerComparison:
    scenario: str
    policy: str
    statistical_power: float
    decision_power: float
    gap: float


def statistical_power_for_scenario(
    scenario: BenchmarkScenario,
    alpha: float = 0.05,
) -> float:
    """Two-sided statistical power for the scenario's true treatment effect."""
    return power_for_two_proportions(
        p_control=scenario.baseline_conversion,
        p_treatment=scenario.baseline_conversion + scenario.treatment_effect,
        n_per_arm=scenario.n_users / 2,
        alpha=alpha,
    )


def compare_statistical_and_decision_power(
    scenarios: list[BenchmarkScenario],
    seeds_per_scenario: int = 200,
) -> list[PowerComparison]:
    benchmark = run_monte_carlo_benchmark(
        scenarios,
        seeds_per_scenario=seeds_per_scenario,
    )

    scenario_map = {scenario.name: scenario for scenario in scenarios}
    comparisons: list[PowerComparison] = []

    for result in benchmark:
        scenario = scenario_map[result.scenario]
        stat_power = statistical_power_for_scenario(scenario)
        comparisons.append(
            PowerComparison(
                scenario=result.scenario,
                policy=result.policy,
                statistical_power=stat_power,
                decision_power=result.correct_decision_rate,
                gap=result.correct_decision_rate - stat_power,
            )
        )

    return comparisons


def decision_truth(
    treatment_effect: float,
    economics: EconomicsConfig,
) -> OptimalAction:
    return optimal_action(treatment_effect, economics)
