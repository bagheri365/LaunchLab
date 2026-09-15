import numpy as np
import pytest

from launchlab.repeated import (
    analyze_at_user_level,
    analyze_naively_at_request_level,
    simulate_repeated_user_experiment,
)


def test_repeated_user_simulation_is_reproducible():
    kwargs = dict(
        n_users=5_000,
        baseline_user_conversion=0.05,
        treatment_effect=0.005,
        mean_requests_per_user=8.0,
        seed=42,
    )
    first = simulate_repeated_user_experiment(**kwargs)
    second = simulate_repeated_user_experiment(**kwargs)

    assert np.array_equal(first.treatment, second.treatment)
    assert np.array_equal(first.requests_per_user, second.requests_per_user)
    assert np.array_equal(first.converted_user, second.converted_user)
    assert np.array_equal(first.request_converted, second.request_converted)


def test_each_user_has_sticky_assignment_across_requests():
    exp = simulate_repeated_user_experiment(
        n_users=2_000,
        mean_requests_per_user=6.0,
        seed=9,
    )

    assert np.array_equal(
        exp.request_treatment,
        exp.treatment[exp.request_user_id],
    )


def test_request_rows_exceed_user_rows():
    exp = simulate_repeated_user_experiment(
        n_users=5_000,
        mean_requests_per_user=10.0,
        seed=1,
    )

    assert exp.n_requests > exp.n_users
    assert exp.requests_per_user.min() >= 1


def test_user_level_analysis_recovers_known_effect_in_large_sample():
    exp = simulate_repeated_user_experiment(
        n_users=300_000,
        baseline_user_conversion=0.05,
        treatment_effect=0.01,
        mean_requests_per_user=5.0,
        seed=123,
    )

    result = analyze_at_user_level(exp)
    assert result.absolute_effect == pytest.approx(0.01, abs=0.001)


def test_naive_request_level_analysis_has_smaller_standard_error():
    exp = simulate_repeated_user_experiment(
        n_users=50_000,
        baseline_user_conversion=0.05,
        treatment_effect=0.0,
        mean_requests_per_user=12.0,
        activity_shape=1.0,
        seed=7,
    )

    user_result = analyze_at_user_level(exp)
    request_result = analyze_naively_at_request_level(exp)

    assert request_result.standard_error < user_result.standard_error


def test_request_level_effect_is_not_same_estimand_as_user_conversion_effect():
    exp = simulate_repeated_user_experiment(
        n_users=100_000,
        baseline_user_conversion=0.05,
        treatment_effect=0.01,
        mean_requests_per_user=8.0,
        seed=17,
    )

    user_result = analyze_at_user_level(exp)
    request_result = analyze_naively_at_request_level(exp)

    assert abs(user_result.absolute_effect - request_result.absolute_effect) > 0.001


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_users": 0},
        {"n_users": 100, "baseline_user_conversion": 0.0},
        {"n_users": 100, "treatment_share": 1.0},
        {"n_users": 100, "mean_requests_per_user": 0.0},
        {"n_users": 100, "activity_shape": 0.0},
        {
            "n_users": 100,
            "baseline_user_conversion": 0.99,
            "treatment_effect": 0.02,
        },
    ],
)
def test_invalid_repeated_user_config_raises(kwargs):
    with pytest.raises(ValueError):
        simulate_repeated_user_experiment(**kwargs)
