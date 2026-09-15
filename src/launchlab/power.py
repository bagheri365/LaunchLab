from __future__ import annotations

from math import ceil, sqrt

from scipy.optimize import brentq
from scipy.stats import norm


def _validate_rate(p: float, name: str) -> None:
    if not 0.0 < p < 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1.")


def _validate_alpha_power(alpha: float, power: float | None = None) -> None:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")
    if power is not None and not 0.0 < power < 1.0:
        raise ValueError("power must be between 0 and 1.")


def power_for_two_proportions(
    p_control: float,
    p_treatment: float,
    n_per_arm: int,
    alpha: float = 0.05,
) -> float:
    """Approximate two-sided z-test power for equal-sized independent arms."""
    _validate_rate(p_control, "p_control")
    _validate_rate(p_treatment, "p_treatment")
    _validate_alpha_power(alpha)

    if n_per_arm <= 0:
        raise ValueError("n_per_arm must be positive.")

    effect = abs(p_treatment - p_control)
    if effect == 0.0:
        return alpha

    pooled = (p_control + p_treatment) / 2.0
    null_se = sqrt(2.0 * pooled * (1.0 - pooled) / n_per_arm)
    alt_se = sqrt(
        (
            p_control * (1.0 - p_control)
            + p_treatment * (1.0 - p_treatment)
        )
        / n_per_arm
    )

    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    mean_shift = effect / alt_se
    threshold = z_alpha * null_se / alt_se

    return float(
        norm.sf(threshold - mean_shift)
        + norm.cdf(-threshold - mean_shift)
    )


def required_sample_size_per_arm(
    p_control: float,
    p_treatment: float,
    alpha: float = 0.05,
    target_power: float = 0.80,
) -> int:
    """Approximate required per-arm sample size for a two-sided z-test."""
    _validate_rate(p_control, "p_control")
    _validate_rate(p_treatment, "p_treatment")
    _validate_alpha_power(alpha, target_power)

    if p_control == p_treatment:
        raise ValueError("p_control and p_treatment must differ.")

    effect = abs(p_treatment - p_control)
    pooled = (p_control + p_treatment) / 2.0

    z_alpha = norm.ppf(1.0 - alpha / 2.0)
    z_beta = norm.ppf(target_power)

    numerator = (
        z_alpha * sqrt(2.0 * pooled * (1.0 - pooled))
        + z_beta
        * sqrt(
            p_control * (1.0 - p_control)
            + p_treatment * (1.0 - p_treatment)
        )
    ) ** 2

    return ceil(numerator / (effect**2))


def minimum_detectable_effect(
    p_control: float,
    n_per_arm: int,
    alpha: float = 0.05,
    target_power: float = 0.80,
    direction: str = "increase",
) -> float:
    """Return the smallest absolute rate change meeting target power."""
    _validate_rate(p_control, "p_control")
    _validate_alpha_power(alpha, target_power)

    if n_per_arm <= 0:
        raise ValueError("n_per_arm must be positive.")
    if direction not in {"increase", "decrease"}:
        raise ValueError("direction must be 'increase' or 'decrease'.")

    if direction == "increase":
        max_effect = (1.0 - p_control) - 1e-12

        def achieved(effect: float) -> float:
            return power_for_two_proportions(
                p_control, p_control + effect, n_per_arm, alpha
            )
    else:
        max_effect = p_control - 1e-12

        def achieved(effect: float) -> float:
            return power_for_two_proportions(
                p_control, p_control - effect, n_per_arm, alpha
            )

    if achieved(max_effect) < target_power:
        raise ValueError("target power is unattainable for the supplied sample size.")

    return float(
        brentq(
            lambda effect: achieved(effect) - target_power,
            1e-12,
            max_effect,
        )
    )
