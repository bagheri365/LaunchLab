import pytest

from launchlab.inference import estimate_proportion_effect


def test_effect_estimate_and_ci_are_sensible():
    result = estimate_proportion_effect(
        control_successes=500,
        control_n=10_000,
        treatment_successes=550,
        treatment_n=10_000,
    )

    assert result.control_rate == pytest.approx(0.05)
    assert result.treatment_rate == pytest.approx(0.055)
    assert result.absolute_effect == pytest.approx(0.005)
    assert result.relative_lift == pytest.approx(0.10)
    assert result.ci_low < result.absolute_effect < result.ci_high
    assert 0.0 <= result.p_value_two_sided <= 1.0


def test_zero_control_rate_has_no_relative_lift():
    result = estimate_proportion_effect(
        control_successes=0,
        control_n=100,
        treatment_successes=1,
        treatment_n=100,
    )
    assert result.relative_lift is None


def test_invalid_counts_raise():
    with pytest.raises(ValueError):
        estimate_proportion_effect(101, 100, 5, 100)
