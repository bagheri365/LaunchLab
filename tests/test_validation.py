import numpy as np
import pytest

from launchlab.experiment import ExperimentConfig
from launchlab.simulation import SimulatedExperiment, simulate_experiment
from launchlab.validation import check_sample_ratio_mismatch, validate_aa_experiment


def test_srm_passes_for_well_randomized_experiment():
    experiment = simulate_experiment(
        ExperimentConfig(n_users=100_000, treatment_share=0.5, seed=1234)
    )
    result = check_sample_ratio_mismatch(
        experiment,
        expected_treatment_share=0.5,
    )
    assert result.passed
    assert result.observed_treatment_share == pytest.approx(0.5, abs=0.01)


def test_srm_detects_deliberately_broken_split():
    n = 10_000
    treatment = np.zeros(n, dtype=bool)
    treatment[:7_000] = True

    experiment = SimulatedExperiment(
        user_id=np.arange(n),
        treatment=treatment,
        eligible=np.ones(n, dtype=bool),
        exposed=np.ones(n, dtype=bool),
        converted=np.zeros(n, dtype=bool),
    )

    result = check_sample_ratio_mismatch(
        experiment,
        expected_treatment_share=0.5,
    )

    assert not result.passed
    assert result.p_value < 0.001
    assert result.observed_treatment_share == pytest.approx(0.7)


def test_srm_can_use_exposed_users_only():
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=50_000,
            treatment_share=0.5,
            exposure_probability=0.8,
            seed=99,
        )
    )
    result = check_sample_ratio_mismatch(
        experiment,
        expected_treatment_share=0.5,
        exposed_only=True,
    )
    assert result.control_count + result.treatment_count == int(experiment.exposed.sum())


def test_aa_validation_passes_for_known_null_seed():
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=100_000,
            baseline_conversion=0.05,
            treatment_effect=0.0,
            seed=17,
        )
    )
    result = validate_aa_experiment(experiment)

    assert result.passed
    assert abs(result.effect.absolute_effect) < 0.005


def test_aa_validation_rejects_clear_non_null():
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=200_000,
            baseline_conversion=0.05,
            treatment_effect=0.02,
            seed=22,
        )
    )
    result = validate_aa_experiment(experiment)

    assert not result.passed
    assert result.effect.p_value_two_sided < 0.05
