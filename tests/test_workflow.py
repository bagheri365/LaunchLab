import pytest

from launchlab.economics import EconomicsConfig
from launchlab.experiment import ExperimentConfig
from launchlab.policies import LaunchDecision
from launchlab.simulation import simulate_experiment
from launchlab.workflow import WorkflowConfig, run_launch_workflow


def econ(candidate_cost: float = 0.0010) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=0.0001,
        inconclusive_cost=1_000.0,
    )


def test_offline_gate_failure_stops_inference():
    exp = simulate_experiment(ExperimentConfig(n_users=10_000, seed=1))
    result = run_launch_workflow(exp, econ(), offline_gate_passed=False)

    assert result.final_decision is LaunchDecision.INCONCLUSIVE
    assert result.effect is None
    assert "offline eligibility gate failed" in result.reasons


def test_exposure_gate_failure_stops_inference():
    exp = simulate_experiment(
        ExperimentConfig(n_users=1_000, exposure_probability=0.01, seed=2)
    )
    result = run_launch_workflow(
        exp,
        econ(),
        config=WorkflowConfig(minimum_exposed_per_arm=50),
    )

    assert result.final_decision is LaunchDecision.INCONCLUSIVE
    assert result.effect is None
    assert "insufficient exposed users per arm" in result.reasons


def test_valid_experiment_produces_effect_mde_and_policies():
    exp = simulate_experiment(
        ExperimentConfig(
            n_users=200_000,
            baseline_conversion=0.05,
            treatment_effect=0.01,
            seed=3,
        )
    )
    result = run_launch_workflow(exp, econ(candidate_cost=0.0011))

    assert result.effect is not None
    assert result.mde is not None
    assert result.mde > 0
    assert len(result.policy_results) == 4


def test_cheaper_candidate_includes_non_inferiority_policy():
    exp = simulate_experiment(
        ExperimentConfig(
            n_users=200_000,
            baseline_conversion=0.05,
            treatment_effect=0.001,
            seed=4,
        )
    )
    result = run_launch_workflow(exp, econ(candidate_cost=0.0005))

    names = {policy.policy for policy in result.policy_results}
    assert "non_inferiority_savings" in names


def test_strong_win_can_reach_ship_consensus():
    exp = simulate_experiment(
        ExperimentConfig(
            n_users=400_000,
            baseline_conversion=0.05,
            treatment_effect=0.02,
            seed=5,
        )
    )
    result = run_launch_workflow(
        exp,
        econ(candidate_cost=0.0010),
        config=WorkflowConfig(practical_threshold=0.001),
    )

    assert result.final_decision is LaunchDecision.SHIP
    assert not result.reasons


@pytest.mark.parametrize(
    "kwargs",
    [
        {"expected_treatment_share": 0.0},
        {"srm_alpha": 0.0},
        {"minimum_exposed_per_arm": 0},
        {"confidence": 0.5},
        {"power": 1.0},
    ],
)
def test_invalid_workflow_config_raises(kwargs):
    with pytest.raises(ValueError):
        WorkflowConfig(**kwargs)
