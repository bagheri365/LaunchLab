from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration for a fixed-horizon user-randomized experiment."""

    n_users: int
    treatment_share: float = 0.5
    exposure_probability: float = 1.0
    baseline_conversion: float = 0.05
    treatment_effect: float = 0.0
    seed: int = 0

    def __post_init__(self) -> None:
        if self.n_users <= 0:
            raise ValueError("n_users must be positive.")
        if not 0.0 < self.treatment_share < 1.0:
            raise ValueError("treatment_share must be between 0 and 1.")
        if not 0.0 <= self.exposure_probability <= 1.0:
            raise ValueError("exposure_probability must be between 0 and 1.")
        if not 0.0 < self.baseline_conversion < 1.0:
            raise ValueError("baseline_conversion must be between 0 and 1.")

        treatment_rate = self.baseline_conversion + self.treatment_effect
        if not 0.0 <= treatment_rate <= 1.0:
            raise ValueError(
                "baseline_conversion + treatment_effect must be between 0 and 1."
            )
