from dataclasses import replace

import pytest

from launchlab.economics import EconomicsConfig
from launchlab.inference import ProportionEffect
from launchlab.policies import (
    LaunchDecision,
    economic_break_even_policy,
    non_inferiority_savings_policy,
    one_sided_bounds,
    practical_significance_policy,
    risk_adjusted_expected_value_policy,
    statistical_superiority_policy,
)


def effect(estimate: float, se: float) -> ProportionEffect:
    return ProportionEffect(
        control_rate=0.05,
        treatment_rate=0.05 + estimate,
        absolute_effect=estimate,
        relative_lift=estimate / 0.05,
        standard_error=se,
        ci_low=estimate - 1.96 * se,
        ci_high=estimate + 1.96 * se,
        z_stat=estimate / se if se else 0.0,
        p_value_two_sided=0.5,
    )


def economics(**overrides) -> EconomicsConfig:
    values = dict(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=0.0012,
        product_allowed_loss=0.0010,
    )
    values.update(overrides)
    return EconomicsConfig(**values)


def test_one_sided_bounds_narrow_as_se_decreases():
    wide = one_sided_bounds(effect(0.001, 0.001))
    narrow = one_sided_bounds(effect(0.001, 0.0001))

    assert (wide[1] - wide[0]) > (narrow[1] - narrow[0])


@pytest.mark.parametrize(
    ("estimate", "se", "expected"),
    [
        (0.01, 0.001, LaunchDecision.SHIP),
        (-0.01, 0.001, LaunchDecision.REJECT),
        (0.001, 0.001, LaunchDecision.INCONCLUSIVE),
    ],
)
def test_statistical_superiority_three_way_decision(estimate, se, expected):
    result = statistical_superiority_policy(effect(estimate, se))
    assert result.decision is expected
    assert result.threshold == pytest.approx(0.0)


def test_practical_significance_requires_more_than_zero():
    observed = effect(0.0010, 0.0001)

    superiority = statistical_superiority_policy(observed)
    practical = practical_significance_policy(
        observed,
        practical_threshold=0.0012,
    )

    assert superiority.decision is LaunchDecision.SHIP
    assert practical.decision is LaunchDecision.REJECT


def test_economic_break_even_can_reject_statistically_positive_effect():
    observed = effect(0.000005, 0.000001)
    config = economics(candidate_cost_per_request=0.0012)

    superiority = statistical_superiority_policy(observed)
    economic = economic_break_even_policy(observed, config)

    assert superiority.decision is LaunchDecision.SHIP
    assert economic.decision is LaunchDecision.REJECT
    assert economic.threshold > 0


def test_non_inferiority_can_ship_slightly_worse_but_cheaper_model():
    config = economics(
        candidate_cost_per_request=0.0,
        product_allowed_loss=0.0001,
    )
    observed = effect(-0.00002, 0.000005)

    result = non_inferiority_savings_policy(observed, config)

    assert result.decision is LaunchDecision.SHIP
    assert result.threshold < 0


def test_non_inferiority_rejects_when_candidate_has_no_cost_savings():
    config = economics(candidate_cost_per_request=0.0020)
    observed = effect(0.0, 0.0001)

    result = non_inferiority_savings_policy(observed, config)

    assert result.decision is LaunchDecision.REJECT
    assert "no serving-cost savings" in result.rationale


def test_expected_value_policy_uses_uncertainty_not_point_value_only():
    config = economics()
    observed = effect(0.00002, 0.00002)

    result = risk_adjusted_expected_value_policy(observed, config)

    assert result.estimate > 0
    assert result.decision is LaunchDecision.INCONCLUSIVE


def test_expected_value_policy_ships_when_value_interval_is_positive():
    config = economics()
    observed = effect(0.001, 0.00005)

    result = risk_adjusted_expected_value_policy(observed, config)

    assert result.lower_bound > 0
    assert result.decision is LaunchDecision.SHIP


def test_expected_value_policy_rejects_when_value_interval_is_negative():
    config = economics(candidate_cost_per_request=0.0020)
    observed = effect(0.0, 0.00001)

    result = risk_adjusted_expected_value_policy(observed, config)

    assert result.upper_bound < 0
    assert result.decision is LaunchDecision.REJECT


def test_invalid_confidence_raises():
    with pytest.raises(ValueError, match="confidence"):
        statistical_superiority_policy(effect(0.0, 0.001), confidence=0.5)
