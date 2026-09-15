from types import SimpleNamespace

import pytest

from launchlab.economics import EconomicsConfig
from launchlab.policies import LaunchDecision
from launchlab.risk_adjustment import (
    probability_risk_adjusted_policy,
    run_probability_risk_benchmark,
)


def econ() -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )


def effect(estimate: float, se: float):
    return SimpleNamespace(
        absolute_effect=estimate,
        standard_error=se,
    )


def test_higher_probability_requirement_is_more_conservative():
    observed = effect(0.0013, 0.00025)

    relaxed = probability_risk_adjusted_policy(
        observed,
        econ(),
        minimum_positive_value_probability=0.80,
    )
    strict = probability_risk_adjusted_policy(
        observed,
        econ(),
        minimum_positive_value_probability=0.99,
    )

    assert relaxed.decision is LaunchDecision.SHIP
    assert strict.decision is LaunchDecision.INCONCLUSIVE


def test_strong_negative_value_can_reject():
    observed = effect(0.0002, 0.0001)
    result = probability_risk_adjusted_policy(
        observed,
        econ(),
        minimum_positive_value_probability=0.95,
    )
    assert result.decision is LaunchDecision.REJECT


def test_invalid_probability_raises():
    with pytest.raises(ValueError):
        probability_risk_adjusted_policy(
            effect(0.001, 0.0002),
            econ(),
            minimum_positive_value_probability=0.5,
        )


def test_stricter_threshold_does_not_reduce_inconclusive_rate():
    rows = run_probability_risk_benchmark(
        n_users=200_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=econ(),
        probability_thresholds=[0.80, 0.99],
        seeds_per_threshold=50,
    )
    relaxed, strict = rows
    assert strict.inconclusive_rate >= relaxed.inconclusive_rate
