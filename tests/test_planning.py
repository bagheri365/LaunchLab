import pytest

from launchlab.economics import EconomicsConfig
from launchlab.experiment import ExperimentConfig
from launchlab.planning import plan_decision_readiness
from launchlab.simulation import simulate_experiment
from launchlab.workflow import WorkflowConfig, run_launch_workflow


def econ(candidate_cost: float = 0.0014) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=0.0001,
        inconclusive_cost=1_000.0,
    )


def workflow_result():
    exp = simulate_experiment(
        ExperimentConfig(
            n_users=250_000,
            baseline_conversion=0.05,
            treatment_effect=0.0015,
            exposure_probability=0.95,
            seed=42,
        )
    )
    return run_launch_workflow(
        exp,
        econ(),
        config=WorkflowConfig(
            minimum_exposed_per_arm=10_000,
            practical_threshold=0.001,
        ),
    )


def test_planner_returns_binding_requirement():
    result = workflow_result()
    plan = plan_decision_readiness(
        result,
        econ(),
        practical_threshold=0.001,
    )

    assert plan.requirements
    assert plan.binding_requirement.required_per_arm == max(
        r.required_per_arm for r in plan.requirements
    )
    assert plan.total_additional_users >= 0


def test_planner_includes_superiority_and_practical_thresholds():
    result = workflow_result()
    plan = plan_decision_readiness(
        result,
        econ(),
        practical_threshold=0.001,
    )

    names = {r.name for r in plan.requirements}
    assert "statistical_superiority" in names
    assert "practical_significance" in names


def test_expensive_candidate_includes_positive_economic_threshold():
    result = workflow_result()
    plan = plan_decision_readiness(
        result,
        econ(candidate_cost=0.0030),
        practical_threshold=0.001,
    )

    economic = next(r for r in plan.requirements if r.name == "economic_break_even")
    assert economic.threshold > 0
    assert economic.decision_margin == pytest.approx(
        result.effect.absolute_effect - economic.threshold
    )


def test_cheaper_candidate_skips_negative_economic_threshold():
    result = workflow_result()
    plan = plan_decision_readiness(
        result,
        econ(candidate_cost=0.0005),
        practical_threshold=0.001,
    )

    assert all(r.name != "economic_break_even" for r in plan.requirements)


def test_invalid_inputs_raise():
    result = workflow_result()

    with pytest.raises(ValueError, match="practical_threshold"):
        plan_decision_readiness(result, econ(), practical_threshold=0.0)


def test_economic_threshold_is_not_treated_as_effect_size():
    result = workflow_result()
    plan = plan_decision_readiness(
        result,
        econ(candidate_cost=0.0014),
        practical_threshold=0.001,
    )

    economic = next(r for r in plan.requirements if r.name == "economic_break_even")
    superiority = next(r for r in plan.requirements if r.name == "statistical_superiority")

    # The economic threshold is tiny, but the observed effect is far above it.
    # Planning should therefore use the distance from observed effect to the
    # threshold, not the threshold itself as the detectable effect.
    assert economic.threshold < 0.0001
    assert economic.required_per_arm < 10_000_000
    assert economic.required_per_arm == pytest.approx(
        superiority.required_per_arm, rel=0.15
    )
