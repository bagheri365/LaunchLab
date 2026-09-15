import pytest

from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario
from launchlab.robustness import run_economic_misspecification_grid


def scenario() -> BenchmarkScenario:
    return BenchmarkScenario(
        name="robustness_case",
        n_users=80_000,
        baseline_conversion=0.05,
        treatment_effect=0.0015,
        economics=EconomicsConfig(
            annual_traffic=100_000_000,
            value_per_conversion=20.0,
            incumbent_cost_per_request=0.0010,
            candidate_cost_per_request=0.0015,
            product_allowed_loss=0.0001,
            inconclusive_cost=1_000.0,
        ),
        practical_threshold=0.001,
    )


def test_grid_shape_matches_assumption_grid_and_policies():
    rows = run_economic_misspecification_grid(
        scenario(),
        value_multipliers=[0.5, 1.0, 2.0],
        cost_multipliers=[0.5, 1.0],
        runs=10,
    )
    policies = {row.policy for row in rows}
    assert len(rows) == 3 * 2 * len(policies)


def test_grid_contains_core_error_metrics():
    rows = run_economic_misspecification_grid(
        scenario(),
        value_multipliers=[1.0],
        cost_multipliers=[1.0],
        runs=10,
    )
    row = rows[0]
    assert 0.0 <= row.correct_decision_rate <= 1.0
    assert 0.0 <= row.harmful_launch_rate <= 1.0
    assert 0.0 <= row.missed_opportunity_rate <= 1.0
    assert 0.0 <= row.inconclusive_rate <= 1.0
    assert row.mean_regret >= 0.0


def test_invalid_grid_inputs_raise():
    with pytest.raises(ValueError):
        run_economic_misspecification_grid(
            scenario(),
            value_multipliers=[],
            cost_multipliers=[1.0],
            runs=5,
        )

    with pytest.raises(ValueError):
        run_economic_misspecification_grid(
            scenario(),
            value_multipliers=[1.0],
            cost_multipliers=[1.0],
            runs=0,
        )
