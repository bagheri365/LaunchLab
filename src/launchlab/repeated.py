from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .inference import ProportionEffect, estimate_proportion_effect


@dataclass(frozen=True)
class RepeatedUserExperiment:
    user_id: np.ndarray
    treatment: np.ndarray
    requests_per_user: np.ndarray
    converted_user: np.ndarray
    request_user_id: np.ndarray
    request_treatment: np.ndarray
    request_converted: np.ndarray

    @property
    def n_users(self) -> int:
        return int(self.user_id.size)

    @property
    def n_requests(self) -> int:
        return int(self.request_user_id.size)


def simulate_repeated_user_experiment(
    *,
    n_users: int,
    baseline_user_conversion: float = 0.05,
    treatment_effect: float = 0.0,
    treatment_share: float = 0.5,
    mean_requests_per_user: float = 5.0,
    activity_shape: float = 1.5,
    seed: int = 0,
) -> RepeatedUserExperiment:
    """Simulate sticky user assignment with heterogeneous repeated request counts.

    User conversion is the canonical outcome. If a user converts, exactly one of
    that user's requests is marked as the conversion request. Requests from the
    same user are therefore correlated by construction.
    """
    if n_users <= 0:
        raise ValueError("n_users must be positive.")
    if not 0.0 < baseline_user_conversion < 1.0:
        raise ValueError("baseline_user_conversion must be between 0 and 1.")
    if not 0.0 < treatment_share < 1.0:
        raise ValueError("treatment_share must be between 0 and 1.")
    if mean_requests_per_user <= 0:
        raise ValueError("mean_requests_per_user must be positive.")
    if activity_shape <= 0:
        raise ValueError("activity_shape must be positive.")

    treatment_rate = baseline_user_conversion + treatment_effect
    if not 0.0 <= treatment_rate <= 1.0:
        raise ValueError(
            "baseline_user_conversion + treatment_effect must be between 0 and 1."
        )

    rng = np.random.default_rng(seed)

    user_id = np.arange(n_users, dtype=np.int64)
    treatment = rng.random(n_users) < treatment_share

    # Gamma-Poisson mixture gives realistic over-dispersion in user activity.
    gamma_scale = mean_requests_per_user / activity_shape
    latent_activity = rng.gamma(shape=activity_shape, scale=gamma_scale, size=n_users)
    requests_per_user = rng.poisson(latent_activity) + 1

    user_conversion_probability = np.full(
        n_users,
        baseline_user_conversion,
        dtype=float,
    )
    user_conversion_probability[treatment] += treatment_effect
    converted_user = rng.random(n_users) < user_conversion_probability

    request_user_id = np.repeat(user_id, requests_per_user)
    request_treatment = np.repeat(treatment, requests_per_user)
    request_converted = np.zeros(request_user_id.size, dtype=bool)

    offsets = np.concatenate(([0], np.cumsum(requests_per_user)))
    converted_indices = np.flatnonzero(converted_user)
    for uid in converted_indices:
        start = offsets[uid]
        stop = offsets[uid + 1]
        chosen = rng.integers(start, stop)
        request_converted[chosen] = True

    return RepeatedUserExperiment(
        user_id=user_id,
        treatment=treatment,
        requests_per_user=requests_per_user,
        converted_user=converted_user,
        request_user_id=request_user_id,
        request_treatment=request_treatment,
        request_converted=request_converted,
    )


def analyze_at_user_level(
    experiment: RepeatedUserExperiment,
) -> ProportionEffect:
    control = ~experiment.treatment
    treatment = experiment.treatment

    return estimate_proportion_effect(
        control_successes=int(np.sum(experiment.converted_user & control)),
        control_n=int(np.sum(control)),
        treatment_successes=int(np.sum(experiment.converted_user & treatment)),
        treatment_n=int(np.sum(treatment)),
    )


def analyze_naively_at_request_level(
    experiment: RepeatedUserExperiment,
) -> ProportionEffect:
    """Incorrectly treat repeated requests as independent observations."""
    control = ~experiment.request_treatment
    treatment = experiment.request_treatment

    return estimate_proportion_effect(
        control_successes=int(np.sum(experiment.request_converted & control)),
        control_n=int(np.sum(control)),
        treatment_successes=int(np.sum(experiment.request_converted & treatment)),
        treatment_n=int(np.sum(treatment)),
    )
