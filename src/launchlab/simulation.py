from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .experiment import ExperimentConfig


@dataclass(frozen=True)
class SimulatedExperiment:
    user_id: np.ndarray
    treatment: np.ndarray
    eligible: np.ndarray
    exposed: np.ndarray
    converted: np.ndarray

    @property
    def n_users(self) -> int:
        return int(self.user_id.size)

    def exposed_arm_counts(self) -> tuple[int, int]:
        exposed = self.exposed
        control_n = int(np.sum(exposed & ~self.treatment))
        treatment_n = int(np.sum(exposed & self.treatment))
        return control_n, treatment_n

    def exposed_conversion_counts(self) -> tuple[int, int, int, int]:
        exposed = self.exposed

        control_mask = exposed & ~self.treatment
        treatment_mask = exposed & self.treatment

        control_successes = int(np.sum(self.converted & control_mask))
        treatment_successes = int(np.sum(self.converted & treatment_mask))

        return (
            control_successes,
            int(np.sum(control_mask)),
            treatment_successes,
            int(np.sum(treatment_mask)),
        )


def simulate_experiment(config: ExperimentConfig) -> SimulatedExperiment:
    """Simulate a simple user-randomized, fixed-horizon A/B experiment.

    Treatment is assigned once per user. Eligibility is fixed to True in v1;
    exposure is modeled separately from assignment. Conversion is only observed
    for exposed users, matching the project's canonical exposed-user metric.
    """
    rng = np.random.default_rng(config.seed)

    user_id = np.arange(config.n_users, dtype=np.int64)
    treatment = rng.random(config.n_users) < config.treatment_share
    eligible = np.ones(config.n_users, dtype=bool)
    exposed = eligible & (rng.random(config.n_users) < config.exposure_probability)

    conversion_probability = np.full(
        config.n_users,
        config.baseline_conversion,
        dtype=float,
    )
    conversion_probability[treatment] += config.treatment_effect

    converted = exposed & (rng.random(config.n_users) < conversion_probability)

    return SimulatedExperiment(
        user_id=user_id,
        treatment=treatment,
        eligible=eligible,
        exposed=exposed,
        converted=converted,
    )
