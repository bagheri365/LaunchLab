from launchlab.joint_reporting import (
    write_joint_optima_csv,
    write_joint_surface_csv,
)
from launchlab.joint_surface import JointSurfaceOptimum, JointSurfacePoint


def test_joint_surface_csv(tmp_path):
    row = JointSurfacePoint(
        treatment_effect=0.001,
        n_users=100_000,
        assumed_value_multiplier=1.0,
        assumed_cost_multiplier=1.0,
        inconclusive_cost=1_000.0,
        policy="economic_break_even",
        correct_decision_rate=0.1,
        harmful_launch_rate=0.0,
        missed_opportunity_rate=0.05,
        inconclusive_rate=0.85,
        mean_regret=5_000.0,
    )
    path = write_joint_surface_csv([row], tmp_path / "joint.csv")
    header = path.read_text().splitlines()[0]
    assert "n_users" in header
    assert "assumed_value_multiplier" in header
    assert "inconclusive_cost" in header
    assert "mean_regret" in header


def test_joint_optima_csv(tmp_path):
    row = JointSurfaceOptimum(
        treatment_effect=0.001,
        n_users=100_000,
        assumed_value_multiplier=1.0,
        assumed_cost_multiplier=1.0,
        inconclusive_cost=1_000.0,
        policy="economic_break_even",
        mean_regret=5_000.0,
    )
    path = write_joint_optima_csv([row], tmp_path / "optima.csv")
    assert path.read_text().splitlines()[0] == (
        "treatment_effect,n_users,assumed_value_multiplier,assumed_cost_multiplier,"
        "inconclusive_cost,policy,mean_regret"
    )
