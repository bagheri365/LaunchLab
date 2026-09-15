import pytest

from launchlab.sensitivity import run_sensitivity_grid


def base_grid():
    return run_sensitivity_grid(
        baseline_conversion=0.05,
        treatment_effect=0.002,
        annual_traffic=100_000_000,
        incumbent_cost_per_request=0.001,
        sample_sizes=[10_000, 50_000],
        values_per_conversion=[10.0, 20.0],
        candidate_costs=[0.001, 0.002],
        practical_thresholds=[0.001],
        seed=7,
    )


def test_grid_shape_matches_cartesian_product_and_policies():
    rows = base_grid()
    assert len(rows) == 2 * 2 * 2 * 1 * 4


def test_grid_contains_expected_policies():
    rows = base_grid()
    assert {row.policy for row in rows} == {
        "statistical_superiority",
        "practical_significance",
        "economic_break_even",
        "risk_adjusted_expected_value",
    }


def test_sample_size_changes_uncertainty():
    rows = [
        row for row in base_grid()
        if row.policy == "statistical_superiority"
        and row.value_per_conversion == 10.0
        and row.candidate_cost_per_request == 0.001
    ]
    small = next(row for row in rows if row.sample_size == 10_000)
    large = next(row for row in rows if row.sample_size == 50_000)

    assert (large.upper_bound - large.lower_bound) < (
        small.upper_bound - small.lower_bound
    )


def test_invalid_grid_inputs_raise():
    with pytest.raises(ValueError):
        run_sensitivity_grid(
            baseline_conversion=0.05,
            treatment_effect=0.001,
            annual_traffic=1_000_000,
            incumbent_cost_per_request=0.001,
            sample_sizes=[],
            values_per_conversion=[20.0],
            candidate_costs=[0.001],
            practical_thresholds=[0.001],
        )
