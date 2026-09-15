import pytest

from launchlab.delay_sensitivity import (
    run_delay_cost_sensitivity,
    select_minimum_regret_thresholds,
)
from launchlab.economics import EconomicsConfig


def economics() -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )


def test_grid_shape():
    rows = run_delay_cost_sensitivity(
        n_users=100_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=economics(),
        inconclusive_costs=[0.0, 1_000.0, 10_000.0],
        probability_thresholds=[0.80, 0.95],
        seeds_per_threshold=10,
    )
    assert len(rows) == 6


def test_inconclusive_cost_changes_regret_not_decision_rates():
    rows = run_delay_cost_sensitivity(
        n_users=100_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=economics(),
        inconclusive_costs=[0.0, 10_000.0],
        probability_thresholds=[0.95],
        seeds_per_threshold=20,
    )
    low, high = rows
    assert low.correct_decision_rate == high.correct_decision_rate
    assert low.inconclusive_rate == high.inconclusive_rate
    assert high.mean_regret >= low.mean_regret


def test_selects_one_optimum_per_delay_cost():
    rows = run_delay_cost_sensitivity(
        n_users=100_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=economics(),
        inconclusive_costs=[0.0, 10_000.0],
        probability_thresholds=[0.80, 0.95, 0.99],
        seeds_per_threshold=10,
    )
    optima = select_minimum_regret_thresholds(rows)
    assert len(optima) == 2


def test_invalid_costs_raise():
    with pytest.raises(ValueError):
        run_delay_cost_sensitivity(
            n_users=100_000,
            baseline_conversion=0.05,
            treatment_effect=0.001,
            economics=economics(),
            inconclusive_costs=[-1.0],
            probability_thresholds=[0.95],
            seeds_per_threshold=10,
        )
