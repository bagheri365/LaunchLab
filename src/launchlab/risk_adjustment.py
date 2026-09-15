from __future__ import annotations

from dataclasses import dataclass

from scipy.stats import norm

from .economics import EconomicsConfig, OptimalAction, economic_regret, optimal_action
from .experiment import ExperimentConfig
from .inference import ProportionEffect, estimate_proportion_effect
from .policies import LaunchDecision
from .simulation import simulate_experiment


@dataclass(frozen=True)
class ProbabilityRiskResult:
    decision: LaunchDecision
    probability_positive_value: float
    annual_value_estimate: float
    annual_value_standard_error: float
    minimum_positive_value_probability: float


@dataclass(frozen=True)
class RiskThresholdAggregate:
    minimum_positive_value_probability: float
    runs: int
    correct_decision_rate: float
    harmful_launch_rate: float
    missed_opportunity_rate: float
    inconclusive_rate: float
    mean_regret: float


def probability_positive_annual_value(
    effect: ProportionEffect,
    economics: EconomicsConfig,
) -> tuple[float, float, float]:
    annual_value_estimate = economics.annual_traffic * (
        effect.absolute_effect * economics.value_per_conversion
        - (
            economics.candidate_cost_per_request
            - economics.incumbent_cost_per_request
        )
    )
    annual_value_se = (
        economics.annual_traffic
        * economics.value_per_conversion
        * effect.standard_error
    )

    if annual_value_se == 0:
        probability = 1.0 if annual_value_estimate > 0 else 0.0
    else:
        probability = float(norm.cdf(annual_value_estimate / annual_value_se))

    return probability, annual_value_estimate, annual_value_se


def probability_risk_adjusted_policy(
    effect: ProportionEffect,
    economics: EconomicsConfig,
    *,
    minimum_positive_value_probability: float = 0.95,
) -> ProbabilityRiskResult:
    if not 0.5 < minimum_positive_value_probability < 1.0:
        raise ValueError(
            "minimum_positive_value_probability must be between 0.5 and 1."
        )

    probability, annual_value_estimate, annual_value_se = (
        probability_positive_annual_value(effect, economics)
    )
    reject_cutoff = 1.0 - minimum_positive_value_probability

    if probability >= minimum_positive_value_probability:
        decision = LaunchDecision.SHIP
    elif probability <= reject_cutoff:
        decision = LaunchDecision.REJECT
    else:
        decision = LaunchDecision.INCONCLUSIVE

    return ProbabilityRiskResult(
        decision=decision,
        probability_positive_value=probability,
        annual_value_estimate=annual_value_estimate,
        annual_value_standard_error=annual_value_se,
        minimum_positive_value_probability=minimum_positive_value_probability,
    )


def run_probability_risk_benchmark(
    *,
    n_users: int,
    baseline_conversion: float,
    treatment_effect: float,
    economics: EconomicsConfig,
    probability_thresholds: list[float],
    seeds_per_threshold: int = 100,
) -> list[RiskThresholdAggregate]:
    if n_users <= 0:
        raise ValueError("n_users must be positive.")
    if seeds_per_threshold <= 0:
        raise ValueError("seeds_per_threshold must be positive.")
    if not probability_thresholds:
        raise ValueError("probability_thresholds must not be empty.")

    truth = optimal_action(treatment_effect, economics)
    rows: list[RiskThresholdAggregate] = []

    for probability_threshold in probability_thresholds:
        correct = 0
        harmful = 0
        missed = 0
        inconclusive = 0
        regret = 0.0

        for seed in range(seeds_per_threshold):
            experiment = simulate_experiment(
                ExperimentConfig(
                    n_users=n_users,
                    baseline_conversion=baseline_conversion,
                    treatment_effect=treatment_effect,
                    seed=seed,
                )
            )
            c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
            effect = estimate_proportion_effect(c_success, c_n, t_success, t_n)
            result = probability_risk_adjusted_policy(
                effect,
                economics,
                minimum_positive_value_probability=probability_threshold,
            )

            decision = result.decision
            if (
                truth is OptimalAction.SHIP
                and decision is LaunchDecision.SHIP
            ) or (
                truth is OptimalAction.REJECT
                and decision is LaunchDecision.REJECT
            ):
                correct += 1

            harmful += int(
                truth is OptimalAction.REJECT
                and decision is LaunchDecision.SHIP
            )
            missed += int(
                truth is OptimalAction.SHIP
                and decision is LaunchDecision.REJECT
            )
            inconclusive += int(decision is LaunchDecision.INCONCLUSIVE)
            regret += economic_regret(treatment_effect, decision.value, economics)

        rows.append(
            RiskThresholdAggregate(
                minimum_positive_value_probability=probability_threshold,
                runs=seeds_per_threshold,
                correct_decision_rate=correct / seeds_per_threshold,
                harmful_launch_rate=harmful / seeds_per_threshold,
                missed_opportunity_rate=missed / seeds_per_threshold,
                inconclusive_rate=inconclusive / seeds_per_threshold,
                mean_regret=regret / seeds_per_threshold,
            )
        )

    return rows
