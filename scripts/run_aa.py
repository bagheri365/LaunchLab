from launchlab.experiment import ExperimentConfig
from launchlab.simulation import simulate_experiment
from launchlab.validation import check_sample_ratio_mismatch, validate_aa_experiment


def main() -> None:
    config = ExperimentConfig(
        n_users=100_000,
        treatment_share=0.5,
        baseline_conversion=0.05,
        treatment_effect=0.0,
        seed=17,
    )
    experiment = simulate_experiment(config)

    srm = check_sample_ratio_mismatch(
        experiment,
        expected_treatment_share=config.treatment_share,
    )
    aa = validate_aa_experiment(experiment)

    print(f"SRM passed: {srm.passed} (p={srm.p_value:.4g})")
    print(
        f"A/A passed: {aa.passed} "
        f"(effect={aa.effect.absolute_effect:.6f}, "
        f"p={aa.effect.p_value_two_sided:.4g})"
    )


if __name__ == "__main__":
    main()
