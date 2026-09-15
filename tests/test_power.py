import pytest

from launchlab.power import (
    minimum_detectable_effect,
    power_for_two_proportions,
    required_sample_size_per_arm,
)


def test_power_is_close_to_alpha_under_null():
    power = power_for_two_proportions(
        p_control=0.05,
        p_treatment=0.05,
        n_per_arm=10_000,
        alpha=0.05,
    )
    assert power == pytest.approx(0.05)


def test_power_increases_with_sample_size():
    small = power_for_two_proportions(0.05, 0.055, 5_000)
    large = power_for_two_proportions(0.05, 0.055, 50_000)
    assert large > small


def test_required_sample_size_hits_target_power():
    n = required_sample_size_per_arm(
        p_control=0.05,
        p_treatment=0.055,
        alpha=0.05,
        target_power=0.80,
    )
    achieved = power_for_two_proportions(
        p_control=0.05,
        p_treatment=0.055,
        n_per_arm=n,
        alpha=0.05,
    )
    assert achieved >= 0.80


def test_mde_decreases_with_more_traffic():
    mde_small = minimum_detectable_effect(0.05, 10_000)
    mde_large = minimum_detectable_effect(0.05, 100_000)
    assert mde_large < mde_small
