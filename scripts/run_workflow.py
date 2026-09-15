from launchlab.economics import EconomicsConfig
from launchlab.experiment import ExperimentConfig
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

    result = run_launch_workflow(
        experiment,
        economics,
        config=WorkflowConfig(
            expected_treatment_share=0.5,
            srm_alpha=0.001,
            minimum_exposed_per_arm=10_000,
            practical_threshold=0.001,
        ),
    )

    print(f"offline gate: {result.offline_gate_passed}")
    print(f"exposure gate: {result.exposure_gate_passed}")
    print(f"SRM passed: {result.srm.passed} (p={result.srm.p_value:.4g})")

    if result.effect is not None:
        print(f"effect: {result.effect.absolute_effect:.6f}")
        print(f"95% CI: [{result.effect.ci_low:.6f}, {result.effect.ci_high:.6f}]")
        print(f"MDE @ 80% power: {result.mde:.6f}")

    print()
    for policy in result.policy_results:
        print(
            f"{policy.policy:<30} {policy.decision.value:<12} "
            f"threshold={policy.threshold:.6f}"
        )

    print()
    print(f"FINAL: {result.final_decision.value}")
    if result.reasons:
        for reason in result.reasons:
            print(f"- {reason}")


if __name__ == "__main__":
    main()
