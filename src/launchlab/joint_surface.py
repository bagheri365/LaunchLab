from __future__ import annotations

from dataclasses import dataclass, replace

from .economics import (
    EconomicsConfig,
    OptimalAction,
    economic_regret,
    optimal_action,
)
from .evaluation import BenchmarkScenario, run_monte_carlo_benchmark
from .experiment import ExperimentConfig
from .inference import estimate_proportion_effect
from .policies import LaunchDecision
from .risk_adjustment import probability_risk_adjusted_policy
from .simulation import simulate_experiment


@dataclass(frozen=True)
class JointSurfacePoint:
    treatment_effect: float
    n_users: int
    assumed_value_multiplier: float
    assumed_cost_multiplier: float
    inconclusive_cost: float
    policy: str
    correct_decision_rate: float
    harmful_launch_rate: float
    missed_opportunity_rate: float
    inconclusive_rate: float
    harmful_launch_regret: float
    missed_opportunity_regret: float
    inconclusive_regret: float
    mean_regret: float


@dataclass(frozen=True)
class JointSurfaceOptimum:
    treatment_effect: float
    n_users: int
    assumed_value_multiplier: float
    assumed_cost_multiplier: float
    inconclusive_cost: float
    policy: str
    mean_regret: float


def _assumed_economics(
    true_economics: EconomicsConfig,
    *,
    value_multiplier: float,
    cost_multiplier: float,
    inconclusive_cost: float,
) -> EconomicsConfig:
    incremental_cost = (
        true_economics.candidate_cost_per_request
        - true_economics.incumbent_cost_per_request
    )
    return replace(
        true_economics,
        value_per_conversion=(
            true_economics.value_per_conversion * value_multiplier
        ),
        candidate_cost_per_request=(
            true_economics.incumbent_cost_per_request
            + incremental_cost * cost_multiplier
        ),
        inconclusive_cost=inconclusive_cost,
    )


def _regret_components(
    *,
    treatment_effect: float,
    true_economics: EconomicsConfig,
    harmful_launch_rate: float,
    missed_opportunity_rate: float,
    inconclusive_rate: float,
) -> tuple[float, float, float]:
    harmful_cost = economic_regret(
        treatment_effect,
        LaunchDecision.SHIP.value,
        true_economics,
    )
    missed_cost = economic_regret(
        treatment_effect,
        LaunchDecision.REJECT.value,
        true_economics,
    )
    inconclusive_cost = economic_regret(
        treatment_effect,
        LaunchDecision.INCONCLUSIVE.value,
        true_economics,
    )
    return (
        harmful_launch_rate * harmful_cost,
        missed_opportunity_rate * missed_cost,
        inconclusive_rate * inconclusive_cost,
    )


def _run_probability_policy(
    *,
    n_users: int,
    baseline_conversion: float,
    treatment_effect: float,
    true_economics: EconomicsConfig,
    policy_economics: EconomicsConfig,
    probability_threshold: float,
    runs: int,
) -> tuple[float, float, float, float, float]:
    truth = optimal_action(treatment_effect, true_economics)
    correct = 0
    harmful = 0
    missed = 0
    inconclusive = 0
    regret = 0.0

    for seed in range(runs):
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
            policy_economics,
            minimum_positive_value_probability=probability_threshold,
        )
        decision = result.decision

        correct += int(
            (
                truth is OptimalAction.SHIP
                and decision is LaunchDecision.SHIP
            )
            or (
                truth is OptimalAction.REJECT
                and decision is LaunchDecision.REJECT
            )
        )
        harmful += int(
            truth is OptimalAction.REJECT
            and decision is LaunchDecision.SHIP
        )
        missed += int(
            truth is OptimalAction.SHIP
            and decision is LaunchDecision.REJECT
        )
        inconclusive += int(decision is LaunchDecision.INCONCLUSIVE)
        regret += economic_regret(
            treatment_effect,
            decision.value,
            true_economics,
        )

    return (
        correct / runs,
        harmful / runs,
        missed / runs,
        inconclusive / runs,
        regret / runs,
    )


def run_joint_decision_surface(
    *,
    baseline_conversion: float,
    treatment_effect: float,
    true_economics: EconomicsConfig,
    n_users_values: list[int],
    value_multipliers: list[float],
    cost_multipliers: list[float],
    inconclusive_costs: list[float],
    probability_threshold: float = 0.95,
    runs: int = 100,
) -> list[JointSurfacePoint]:
    if runs <= 0:
        raise ValueError("runs must be positive.")
    if not n_users_values:
        raise ValueError("n_users_values must not be empty.")
    if not value_multipliers:
        raise ValueError("value_multipliers must not be empty.")
    if not cost_multipliers:
        raise ValueError("cost_multipliers must not be empty.")
    if not inconclusive_costs:
        raise ValueError("inconclusive_costs must not be empty.")
    if any(n <= 0 for n in n_users_values):
        raise ValueError("n_users values must be positive.")
    if any(v <= 0 for v in value_multipliers):
        raise ValueError("value multipliers must be positive.")
    if any(c < 0 for c in cost_multipliers):
        raise ValueError("cost multipliers must be non-negative.")
    if any(c < 0 for c in inconclusive_costs):
        raise ValueError("inconclusive costs must be non-negative.")

    rows: list[JointSurfacePoint] = []

    for n_users in n_users_values:
        for value_multiplier in value_multipliers:
            for cost_multiplier in cost_multipliers:
                for inconclusive_cost in inconclusive_costs:
                    policy_economics = _assumed_economics(
                        true_economics,
                        value_multiplier=value_multiplier,
                        cost_multiplier=cost_multiplier,
                        inconclusive_cost=inconclusive_cost,
                    )
                    truth_economics = replace(
                        true_economics,
                        inconclusive_cost=inconclusive_cost,
                    )

                    scenario = BenchmarkScenario(
                        name="joint_surface",
                        n_users=n_users,
                        baseline_conversion=baseline_conversion,
                        treatment_effect=treatment_effect,
                        economics=truth_economics,
                        practical_threshold=0.001,
                        policy_economics=policy_economics,
                    )
                    aggregates = run_monte_carlo_benchmark(
                        [scenario],
                        seeds_per_scenario=runs,
                    )

                    for aggregate in aggregates:
                        rows.append(
                            JointSurfacePoint(
                                treatment_effect=treatment_effect,
                                n_users=n_users,
                                assumed_value_multiplier=value_multiplier,
                                assumed_cost_multiplier=cost_multiplier,
                                inconclusive_cost=inconclusive_cost,
                                policy=aggregate.policy,
                                correct_decision_rate=(
                                    aggregate.correct_decision_rate
                                ),
                                harmful_launch_rate=(
                                    aggregate.harmful_launch_rate
                                ),
                                missed_opportunity_rate=(
                                    aggregate.missed_opportunity_rate
                                ),
                                inconclusive_rate=aggregate.inconclusive_rate,
                                harmful_launch_regret=_regret_components(
                                    treatment_effect=treatment_effect,
                                    true_economics=truth_economics,
                                    harmful_launch_rate=aggregate.harmful_launch_rate,
                                    missed_opportunity_rate=aggregate.missed_opportunity_rate,
                                    inconclusive_rate=aggregate.inconclusive_rate,
                                )[0],
                                missed_opportunity_regret=_regret_components(
                                    treatment_effect=treatment_effect,
                                    true_economics=truth_economics,
                                    harmful_launch_rate=aggregate.harmful_launch_rate,
                                    missed_opportunity_rate=aggregate.missed_opportunity_rate,
                                    inconclusive_rate=aggregate.inconclusive_rate,
                                )[1],
                                inconclusive_regret=_regret_components(
                                    treatment_effect=treatment_effect,
                                    true_economics=truth_economics,
                                    harmful_launch_rate=aggregate.harmful_launch_rate,
                                    missed_opportunity_rate=aggregate.missed_opportunity_rate,
                                    inconclusive_rate=aggregate.inconclusive_rate,
                                )[2],
                                mean_regret=aggregate.mean_regret,
                            )
                        )

                    (
                        correct,
                        harmful,
                        missed,
                        inconclusive,
                        mean_regret,
                    ) = _run_probability_policy(
                        n_users=n_users,
                        baseline_conversion=baseline_conversion,
                        treatment_effect=treatment_effect,
                        true_economics=truth_economics,
                        policy_economics=policy_economics,
                        probability_threshold=probability_threshold,
                        runs=runs,
                    )
                    rows.append(
                        JointSurfacePoint(
                            treatment_effect=treatment_effect,
                            n_users=n_users,
                            assumed_value_multiplier=value_multiplier,
                            assumed_cost_multiplier=cost_multiplier,
                            inconclusive_cost=inconclusive_cost,
                            policy=(
                                "probability_risk_adjusted_"
                                f"{probability_threshold:.3f}"
                            ),
                            correct_decision_rate=correct,
                            harmful_launch_rate=harmful,
                            missed_opportunity_rate=missed,
                            inconclusive_rate=inconclusive,
                            harmful_launch_regret=_regret_components(
                                treatment_effect=treatment_effect,
                                true_economics=truth_economics,
                                harmful_launch_rate=harmful,
                                missed_opportunity_rate=missed,
                                inconclusive_rate=inconclusive,
                            )[0],
                            missed_opportunity_regret=_regret_components(
                                treatment_effect=treatment_effect,
                                true_economics=truth_economics,
                                harmful_launch_rate=harmful,
                                missed_opportunity_rate=missed,
                                inconclusive_rate=inconclusive,
                            )[1],
                            inconclusive_regret=_regret_components(
                                treatment_effect=treatment_effect,
                                true_economics=truth_economics,
                                harmful_launch_rate=harmful,
                                missed_opportunity_rate=missed,
                                inconclusive_rate=inconclusive,
                            )[2],
                            mean_regret=mean_regret,
                        )
                    )

    return rows


def select_minimum_regret_policies(
    rows: list[JointSurfacePoint],
) -> list[JointSurfaceOptimum]:
    if not rows:
        raise ValueError("rows must not be empty.")

    grouped: dict[
        tuple[float, int, float, float, float],
        list[JointSurfacePoint],
    ] = {}

    for row in rows:
        key = (
            row.treatment_effect,
            row.n_users,
            row.assumed_value_multiplier,
            row.assumed_cost_multiplier,
            row.inconclusive_cost,
        )
        grouped.setdefault(key, []).append(row)

    output: list[JointSurfaceOptimum] = []
    for key, group in sorted(grouped.items()):
        best = min(group, key=lambda row: (row.mean_regret, row.policy))
        output.append(
            JointSurfaceOptimum(
                treatment_effect=key[0],
                n_users=key[1],
                assumed_value_multiplier=key[2],
                assumed_cost_multiplier=key[3],
                inconclusive_cost=key[4],
                policy=best.policy,
                mean_regret=best.mean_regret,
            )
        )

    return output
