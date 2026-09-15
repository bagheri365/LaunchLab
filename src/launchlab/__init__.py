"""LaunchLab."""

from .economics import (
    EconomicsConfig,
    OptimalAction,
    annual_cost_savings,
    annual_deployment_value,
    annual_incremental_serving_cost,
    economic_allowed_loss,
    economic_regret,
    effective_allowed_loss,
    optimal_action,
    required_lift_for_break_even,
    risk_weighted_loss,
)
from .experiment import ExperimentConfig
from .inference import ProportionEffect, estimate_proportion_effect
from .policies import (
    LaunchDecision,
    PolicyResult,
    economic_break_even_policy,
    non_inferiority_savings_policy,
    one_sided_bounds,
    practical_significance_policy,
    risk_adjusted_expected_value_policy,
    statistical_superiority_policy,
)
from .power import (
    minimum_detectable_effect,
    power_for_two_proportions,
    required_sample_size_per_arm,
)
from .simulation import SimulatedExperiment, simulate_experiment
from .validation import (
    AAValidationResult,
    SampleRatioMismatchResult,
    check_sample_ratio_mismatch,
    validate_aa_experiment,
)

__all__ = [
    "AAValidationResult",
    "EconomicsConfig",
    "ExperimentConfig",
    "LaunchDecision",
    "OptimalAction",
    "PolicyResult",
    "ProportionEffect",
    "SampleRatioMismatchResult",
    "SimulatedExperiment",
    "annual_cost_savings",
    "annual_deployment_value",
    "annual_incremental_serving_cost",
    "check_sample_ratio_mismatch",
    "economic_allowed_loss",
    "economic_break_even_policy",
    "economic_regret",
    "effective_allowed_loss",
    "estimate_proportion_effect",
    "minimum_detectable_effect",
    "non_inferiority_savings_policy",
    "one_sided_bounds",
    "optimal_action",
    "power_for_two_proportions",
    "practical_significance_policy",
    "required_lift_for_break_even",
    "required_sample_size_per_arm",
    "risk_adjusted_expected_value_policy",
    "risk_weighted_loss",
    "simulate_experiment",
    "statistical_superiority_policy",
    "validate_aa_experiment",
]
