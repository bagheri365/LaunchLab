from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from scipy.stats import norm


@dataclass(frozen=True)
class ProportionEffect:
    control_rate: float
    treatment_rate: float
    absolute_effect: float
    relative_lift: float | None
    standard_error: float
    ci_low: float
    ci_high: float
    z_stat: float
    p_value_two_sided: float


def _validate_counts(successes: int, n: int, name: str) -> None:
    if n <= 0:
        raise ValueError(f"{name} sample size must be positive.")
    if successes < 0 or successes > n:
        raise ValueError(f"{name} successes must be between 0 and n.")


def estimate_proportion_effect(
    control_successes: int,
    control_n: int,
    treatment_successes: int,
    treatment_n: int,
    confidence: float = 0.95,
) -> ProportionEffect:
    """Estimate the absolute treatment effect for two independent proportions."""
    _validate_counts(control_successes, control_n, "control")
    _validate_counts(treatment_successes, treatment_n, "treatment")

    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1.")

    p_c = control_successes / control_n
    p_t = treatment_successes / treatment_n
    effect = p_t - p_c

    se_unpooled = sqrt(
        p_c * (1.0 - p_c) / control_n
        + p_t * (1.0 - p_t) / treatment_n
    )

    alpha = 1.0 - confidence
    z_crit = norm.ppf(1.0 - alpha / 2.0)
    ci_low = effect - z_crit * se_unpooled
    ci_high = effect + z_crit * se_unpooled

    pooled = (control_successes + treatment_successes) / (control_n + treatment_n)
    se_pooled = sqrt(
        pooled * (1.0 - pooled) * (1.0 / control_n + 1.0 / treatment_n)
    )

    if se_pooled == 0.0:
        z_stat = 0.0 if effect == 0.0 else float("inf")
        p_value = 1.0 if effect == 0.0 else 0.0
    else:
        z_stat = effect / se_pooled
        p_value = 2.0 * norm.sf(abs(z_stat))

    relative_lift = None if p_c == 0.0 else effect / p_c

    return ProportionEffect(
        control_rate=p_c,
        treatment_rate=p_t,
        absolute_effect=effect,
        relative_lift=relative_lift,
        standard_error=se_unpooled,
        ci_low=ci_low,
        ci_high=ci_high,
        z_stat=z_stat,
        p_value_two_sided=p_value,
    )
