from __future__ import annotations

from dataclasses import dataclass

from scipy.stats import chisquare

from .inference import ProportionEffect, estimate_proportion_effect
from .simulation import SimulatedExperiment


@dataclass(frozen=True)
class SampleRatioMismatchResult:
    control_count: int
    treatment_count: int
    expected_treatment_share: float
    observed_treatment_share: float
    chi_square_stat: float
    p_value: float
    passed: bool


@dataclass(frozen=True)
class AAValidationResult:
    effect: ProportionEffect
    alpha: float
    passed: bool


def check_sample_ratio_mismatch(
    experiment: SimulatedExperiment,
    expected_treatment_share: float,
    alpha: float = 0.001,
    exposed_only: bool = False,
) -> SampleRatioMismatchResult:
    """Check whether observed arm counts match the intended allocation."""
    if not 0.0 < expected_treatment_share < 1.0:
        raise ValueError("expected_treatment_share must be between 0 and 1.")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if exposed_only:
        control_count, treatment_count = experiment.exposed_arm_counts()
    else:
        treatment_count = int(experiment.treatment.sum())
        control_count = experiment.n_users - treatment_count

    total = control_count + treatment_count
    if total == 0:
        raise ValueError("cannot run SRM check with zero observations.")

    expected = [
        total * (1.0 - expected_treatment_share),
        total * expected_treatment_share,
    ]
    result = chisquare(
        f_obs=[control_count, treatment_count],
        f_exp=expected,
    )

    return SampleRatioMismatchResult(
        control_count=control_count,
        treatment_count=treatment_count,
        expected_treatment_share=expected_treatment_share,
        observed_treatment_share=treatment_count / total,
        chi_square_stat=float(result.statistic),
        p_value=float(result.pvalue),
        passed=bool(result.pvalue >= alpha),
    )


def validate_aa_experiment(
    experiment: SimulatedExperiment,
    alpha: float = 0.05,
) -> AAValidationResult:
    """Check whether an A/A experiment is consistent with the null."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
    if c_n == 0 or t_n == 0:
        raise ValueError("both exposed arms must contain at least one user.")

    effect = estimate_proportion_effect(
        c_success,
        c_n,
        t_success,
        t_n,
        confidence=1.0 - alpha,
    )

    return AAValidationResult(
        effect=effect,
        alpha=alpha,
        passed=bool(effect.p_value_two_sided >= alpha),
    )
