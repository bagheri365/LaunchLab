import pytest

from launchlab.economics import (
    EconomicsConfig,
    OptimalAction,
    annual_cost_savings,
    annual_deployment_value,
    annual_incremental_serving_cost,
    economic_allowed_loss,
    economic_regret,
    effective_allowed_loss,
    optimal_action,
    required_lift_for_break_even,
    risk_weighted_loss,
)


def base_config(**overrides):
    values = dict(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=0.0012,
        product_allowed_loss=0.0010,
        harmful_launch_weight=2.0,
        missed_opportunity_weight=1.0,
        inconclusive_cost=10_000.0,
    )
    values.update(overrides)
    return EconomicsConfig(**values)


def test_incremental_serving_cost_and_break_even_lift():
    config = base_config()

    incremental_cost = annual_incremental_serving_cost(config)
    assert incremental_cost == pytest.approx(20_000.0)

    required_lift = required_lift_for_break_even(config)
    assert required_lift == pytest.approx(0.00001)


def test_cheaper_model_produces_positive_savings_and_allowed_loss():
    config = base_config(
        candidate_cost_per_request=0.0006,
        product_allowed_loss=0.0010,
    )

    assert annual_cost_savings(config) == pytest.approx(40_000.0)
    assert economic_allowed_loss(config) == pytest.approx(0.00002)
    assert effective_allowed_loss(config) == pytest.approx(0.00002)


def test_product_floor_can_be_stricter_than_economic_margin():
    config = base_config(
        candidate_cost_per_request=0.0,
        product_allowed_loss=0.00001,
    )

    assert economic_allowed_loss(config) > config.product_allowed_loss
    assert effective_allowed_loss(config) == pytest.approx(0.00001)


def test_annual_deployment_value_combines_quality_and_cost():
    config = base_config()
    value = annual_deployment_value(true_effect=0.001, config=config)

    expected_conversion_value = 100_000_000 * 0.001 * 20.0
    expected_incremental_cost = 20_000.0
    assert value == pytest.approx(expected_conversion_value - expected_incremental_cost)


def test_profitable_candidate_is_optimal_to_ship():
    config = base_config()
    assert optimal_action(0.001, config) is OptimalAction.SHIP


def test_product_floor_can_force_rejection_even_if_economically_positive():
    config = base_config(
        candidate_cost_per_request=0.0,
        product_allowed_loss=0.00001,
    )

    # Saving $100k/year offsets a -0.004 pp conversion loss ($80k/year),
    # but the product floor allows only -0.001 pp.
    effect = -0.00004
    assert annual_deployment_value(effect, config) > 0
    assert optimal_action(effect, config) is OptimalAction.REJECT


def test_rejecting_profitable_model_creates_regret():
    config = base_config()
    value = annual_deployment_value(0.001, config)

    assert economic_regret(0.001, "REJECT", config) == pytest.approx(value)


def test_shipping_unprofitable_model_creates_regret():
    config = base_config(candidate_cost_per_request=0.0020)
    value = annual_deployment_value(0.0, config)
    assert value < 0

    assert economic_regret(0.0, "SHIP", config) == pytest.approx(-value)


def test_inconclusive_pays_configured_delay_cost_only():
    config = base_config(inconclusive_cost=5_000.0)

    regret = economic_regret(0.001, "INCONCLUSIVE", config)
    assert regret == pytest.approx(5_000.0)


def test_risk_weighting_penalizes_harmful_launch_more():
    config = base_config(
        candidate_cost_per_request=0.0020,
        harmful_launch_weight=3.0,
    )
    raw = economic_regret(0.0, "SHIP", config)
    weighted = risk_weighted_loss(0.0, "SHIP", config)

    assert weighted == pytest.approx(3.0 * raw)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"annual_traffic": 0},
        {"value_per_conversion": 0},
        {"incumbent_cost_per_request": -1},
        {"candidate_cost_per_request": -1},
        {"product_allowed_loss": -0.01},
        {"harmful_launch_weight": 0},
        {"missed_opportunity_weight": 0},
        {"inconclusive_cost": -1},
    ],
)
def test_invalid_economics_config_raises(kwargs):
    values = dict(
        annual_traffic=100,
        value_per_conversion=10,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.001,
    )
    values.update(kwargs)

    with pytest.raises(ValueError):
        EconomicsConfig(**values)
