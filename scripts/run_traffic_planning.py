from launchlab.economics import EconomicsConfig
from launchlab.experiment import ExperimentConfig
from launchlab.planning import plan_decision_readiness
from launchlab.simulation import simulate_experiment
from launchlab.workflow import WorkflowConfig, run_launch_workflow


def main() -> None:
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=250_000,
            baseline_conversion=0.05,
            treatment_effect=0.0015,
            exposure_probability=0.95,
            seed=42,
        )
    )

    economics = EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=0.0014,
        product_allowed_loss=0.0001,
        inconclusive_cost=1_000.0,
    )

    workflow = run_launch_workflow(
        experiment,
        economics,
        config=WorkflowConfig(
            minimum_exposed_per_arm=10_000,
            practical_threshold=0.001,
        ),
    )

    plan = plan_decision_readiness(
        workflow,
        economics,
        practical_threshold=0.001,
        alpha=0.05,
        power=0.80,
    )

    print(f"baseline conversion: {plan.baseline_rate:.4f}")
    print(f"current exposed per arm: {plan.current_per_arm:,}")
    print()

    for req in plan.requirements:
        print(
            f"{req.name:<24} "
            f"threshold={req.threshold:.6f} "
            f"margin={req.decision_margin:+.6f} "
            f"required/arm={req.required_per_arm:,} "
            f"additional/arm={req.additional_per_arm:,}"
        )

    print()
    print(
        "binding requirement: "
        f"{plan.binding_requirement.name} "
        f"({plan.binding_requirement.required_per_arm:,} per arm)"
    )
    print(f"additional users needed: {plan.total_additional_users:,}")


if __name__ == "__main__":
    main()
