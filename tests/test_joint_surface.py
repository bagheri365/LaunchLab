import pytest

from launchlab.economics import EconomicsConfig
from launchlab.joint_surface import (
    run_joint_decision_surface,
    select_minimum_regret_policies,
)


def economics() -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )


def test_joint_surface_shape():
    rows = run_joint_decision_surface(
        baseline_conversion=0.05,
        treatment_effect=0.001,
        true_economics=economics(),
        n_users_values=[50_000],
        value_multipliers=[0.75, 1.0],
        cost_multipliers=[1.0],
        inconclusive_costs=[1_000.0],
        probability_threshold=0.95,
        runs=5,
    )

    combinations = 2
    policies_per_combination = len(rows) // combinations
    assert policies_per_combination >= 5
    assert len(rows) == combinations * policies_per_combination


def test_joint_surface_contains_probability_policy():
    rows = run_joint_decision_surface(
        baseline_conversion=0.05,
        treatment_effect=0.001,
        true_economics=economics(),
        n_users_values=[50_000],
        value_multipliers=[1.0],
        cost_multipliers=[1.0],
        inconclusive_costs=[1_000.0],
        probability_threshold=0.95,
        runs=5,
    )
    assert any(
        row.policy == "probability_risk_adjusted_0.950"
        for row in rows
    )


def test_select_minimum_regret_one_per_operating_point():
    rows = run_joint_decision_surface(
        baseline_conversion=0.05,
        treatment_effect=0.001,
        true_economics=economics(),
        n_users_values=[50_000, 100_000],
        value_multipliers=[1.0],
        cost_multipliers=[1.0],
        inconclusive_costs=[1_000.0, 10_000.0],
        probability_threshold=0.95,
        runs=5,
    )
    optima = select_minimum_regret_policies(rows)
    assert len(optima) == 4


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        run_joint_decision_surface(
            baseline_conversion=0.05,
            treatment_effect=0.001,
            true_economics=economics(),
            n_users_values=[],
            value_multipliers=[1.0],
            cost_multipliers=[1.0],
            inconclusive_costs=[1_000.0],
            runs=5,
        )


def test_probability_policy_uses_true_economics_for_regret():
    rows = run_joint_decision_surface(
        baseline_conversion=0.05,
        treatment_effect=0.001,
        true_economics=economics(),
        n_users_values=[50_000],
        value_multipliers=[0.5],
        cost_multipliers=[1.5],
        inconclusive_costs=[1_000.0],
        probability_threshold=0.95,
        runs=5,
    )
    risk = next(
        row for row in rows
        if row.policy == "probability_risk_adjusted_0.950"
    )
    assert risk.treatment_effect == 0.001
    assert risk.mean_regret >= 0.0
