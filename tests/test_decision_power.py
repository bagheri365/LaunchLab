import pytest

from launchlab.decision_power import (
    compare_statistical_and_decision_power,
    statistical_power_for_scenario,
)
from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario, run_monte_carlo_benchmark


def econ(
    *,
    value_per_conversion: float = 20.0,
    candidate_cost: float = 0.001,
    product_allowed_loss: float = 0.0001,
) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=value_per_conversion,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=product_allowed_loss,
        inconclusive_cost=1_000.0,
    )


def test_statistical_power_is_probability():
    scenario = BenchmarkScenario(
        name="power",
        n_users=20_000,
        baseline_conversion=0.05,
        treatment_effect=0.005,
        economics=econ(),
    )
    power = statistical_power_for_scenario(scenario)
    assert 0.0 <= power <= 1.0


def test_power_comparison_returns_policy_rows():
    scenario = BenchmarkScenario(
        name="easy",
        n_users=20_000,
        baseline_conversion=0.05,
        treatment_effect=0.01,
        economics=econ(candidate_cost=0.0011),
    )

    results = compare_statistical_and_decision_power(
        [scenario],
        seeds_per_scenario=20,
    )

    assert len(results) == 4
    assert all(r.scenario == "easy" for r in results)
    assert all(r.gap == pytest.approx(r.decision_power - r.statistical_power) for r in results)


def test_misspecified_economics_can_change_decision_power():
    truth = econ(value_per_conversion=20.0, candidate_cost=0.0014)
    pessimistic_policy = econ(value_per_conversion=5.0, candidate_cost=0.0014)

    correctly_specified = BenchmarkScenario(
        name="correct",
        n_users=80_000,
        baseline_conversion=0.05,
        treatment_effect=0.0005,
        economics=truth,
    )
    misspecified = BenchmarkScenario(
        name="misspecified",
        n_users=80_000,
        baseline_conversion=0.05,
        treatment_effect=0.0005,
        economics=truth,
        policy_economics=pessimistic_policy,
    )

    results = run_monte_carlo_benchmark(
        [correctly_specified, misspecified],
        seeds_per_scenario=40,
    )

    correct_econ = next(
        r for r in results
        if r.scenario == "correct" and r.policy == "economic_break_even"
    )
    misspec_econ = next(
        r for r in results
        if r.scenario == "misspecified" and r.policy == "economic_break_even"
    )

    assert correct_econ.correct_decision_rate >= misspec_econ.correct_decision_rate


def test_near_break_even_can_have_high_statistical_power_but_low_decision_power():
    scenario = BenchmarkScenario(
        name="near_break_even",
        n_users=800_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=econ(
            value_per_conversion=20.0,
            candidate_cost=0.020,
        ),
    )

    comparisons = compare_statistical_and_decision_power(
        [scenario],
        seeds_per_scenario=50,
    )
    economic = next(r for r in comparisons if r.policy == "economic_break_even")

    assert economic.statistical_power > 0.5
    assert economic.decision_power < economic.statistical_power
