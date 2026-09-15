import numpy as np
import pytest

from launchlab.experiment import ExperimentConfig
from launchlab.inference import estimate_proportion_effect
from launchlab.simulation import simulate_experiment


def test_simulation_is_reproducible_for_same_seed():
    config = ExperimentConfig(
        n_users=2_000,
        treatment_share=0.5,
        exposure_probability=0.8,
        baseline_conversion=0.05,
        treatment_effect=0.01,
        seed=42,
    )

    first = simulate_experiment(config)
    second = simulate_experiment(config)

    assert np.array_equal(first.treatment, second.treatment)
    assert np.array_equal(first.exposed, second.exposed)
    assert np.array_equal(first.converted, second.converted)


def test_assignment_is_user_level_and_near_requested_split():
    experiment = simulate_experiment(
        ExperimentConfig(n_users=100_000, treatment_share=0.4, seed=7)
    )

    assert experiment.n_users == 100_000
    observed_share = float(np.mean(experiment.treatment))
    assert observed_share == pytest.approx(0.4, abs=0.005)


def test_exposure_is_separate_from_assignment():
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=100_000,
            treatment_share=0.5,
            exposure_probability=0.7,
            seed=11,
        )
    )

    observed_exposure = float(np.mean(experiment.exposed))
    assert observed_exposure == pytest.approx(0.7, abs=0.005)
    assert np.all(experiment.converted <= experiment.exposed)


def test_large_experiment_recovers_known_treatment_effect():
    true_effect = 0.01
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=400_000,
            treatment_share=0.5,
            exposure_probability=1.0,
            baseline_conversion=0.05,
            treatment_effect=true_effect,
            seed=123,
        )
    )

    c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
    estimate = estimate_proportion_effect(c_success, c_n, t_success, t_n)

    assert estimate.absolute_effect == pytest.approx(true_effect, abs=0.001)


def test_zero_exposure_produces_zero_exposed_counts():
    experiment = simulate_experiment(
        ExperimentConfig(
            n_users=1_000,
            exposure_probability=0.0,
            seed=3,
        )
    )

    assert experiment.exposed_arm_counts() == (0, 0)
    assert experiment.exposed_conversion_counts() == (0, 0, 0, 0)
