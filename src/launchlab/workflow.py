from __future__ import annotations

from dataclasses import dataclass

from .economics import EconomicsConfig
from .inference import ProportionEffect, estimate_proportion_effect
from .policies import (
    LaunchDecision,
    PolicyResult,
    economic_break_even_policy,
    non_inferiority_savings_policy,
    practical_significance_policy,
    risk_adjusted_expected_value_policy,
    statistical_superiority_policy,
)
from .power import minimum_detectable_effect
from .simulation import SimulatedExperiment
from .validation import SampleRatioMismatchResult, check_sample_ratio_mismatch


@dataclass(frozen=True)
class WorkflowConfig:
    expected_treatment_share: float = 0.5
    srm_alpha: float = 0.001
    minimum_exposed_per_arm: int = 100
    practical_threshold: float = 0.001
    confidence: float = 0.95
    power: float = 0.80

    def __post_init__(self) -> None:
        if not 0.0 < self.expected_treatment_share < 1.0:
            raise ValueError("expected_treatment_share must be between 0 and 1.")
        if not 0.0 < self.srm_alpha < 1.0:
            raise ValueError("srm_alpha must be between 0 and 1.")
        if self.minimum_exposed_per_arm <= 0:
            raise ValueError("minimum_exposed_per_arm must be positive.")
        if not 0.5 < self.confidence < 1.0:
            raise ValueError("confidence must be between 0.5 and 1.")
        if not 0.0 < self.power < 1.0:
            raise ValueError("power must be between 0 and 1.")


@dataclass(frozen=True)
class WorkflowResult:
    offline_gate_passed: bool
    exposure_gate_passed: bool
    srm: SampleRatioMismatchResult
    effect: ProportionEffect | None
    mde: float | None
    policy_results: tuple[PolicyResult, ...]
    final_decision: LaunchDecision
    reasons: tuple[str, ...]


def _consensus_decision(results: tuple[PolicyResult, ...]) -> LaunchDecision:
    if not results:
        return LaunchDecision.INCONCLUSIVE

    decisions = {result.decision for result in results}
    if decisions == {LaunchDecision.SHIP}:
        return LaunchDecision.SHIP
    if decisions == {LaunchDecision.REJECT}:
        return LaunchDecision.REJECT
    return LaunchDecision.INCONCLUSIVE


def run_launch_workflow(
    experiment: SimulatedExperiment,
    economics: EconomicsConfig,
    *,
    config: WorkflowConfig = WorkflowConfig(),
    offline_gate_passed: bool = True,
) -> WorkflowResult:
    reasons: list[str] = []

    srm = check_sample_ratio_mismatch(
        experiment,
        expected_treatment_share=config.expected_treatment_share,
        alpha=config.srm_alpha,
        exposed_only=True,
    )

    control_exposed, treatment_exposed = experiment.exposed_arm_counts()
    exposure_gate_passed = (
        control_exposed >= config.minimum_exposed_per_arm
        and treatment_exposed >= config.minimum_exposed_per_arm
    )

    if not offline_gate_passed:
        reasons.append("offline eligibility gate failed")
    if not srm.passed:
        reasons.append("sample-ratio mismatch detected")
    if not exposure_gate_passed:
        reasons.append("insufficient exposed users per arm")

    if reasons:
        return WorkflowResult(
            offline_gate_passed=offline_gate_passed,
            exposure_gate_passed=exposure_gate_passed,
            srm=srm,
            effect=None,
            mde=None,
            policy_results=(),
            final_decision=LaunchDecision.INCONCLUSIVE,
            reasons=tuple(reasons),
        )

    c_success, c_n, t_success, t_n = experiment.exposed_conversion_counts()
    effect = estimate_proportion_effect(
        c_success,
        c_n,
        t_success,
        t_n,
        confidence=config.confidence,
    )

    n_per_arm = min(c_n, t_n)
    mde = minimum_detectable_effect(
        p_control=effect.control_rate,
        n_per_arm=n_per_arm,
        alpha=1.0 - config.confidence,
        target_power=config.power,
    )

    results = [
        statistical_superiority_policy(effect, confidence=config.confidence),
        practical_significance_policy(
            effect,
            practical_threshold=config.practical_threshold,
            confidence=config.confidence,
        ),
        economic_break_even_policy(effect, economics, confidence=config.confidence),
        risk_adjusted_expected_value_policy(
            effect,
            economics,
            confidence=config.confidence,
        ),
    ]

    if economics.candidate_cost_per_request < economics.incumbent_cost_per_request:
        results.append(
            non_inferiority_savings_policy(
                effect,
                economics,
                confidence=config.confidence,
            )
        )

    policy_results = tuple(results)
    final_decision = _consensus_decision(policy_results)

    if final_decision is LaunchDecision.INCONCLUSIVE:
        reasons.append("applicable launch policies do not unanimously agree")

    return WorkflowResult(
        offline_gate_passed=True,
        exposure_gate_passed=True,
        srm=srm,
        effect=effect,
        mde=mde,
        policy_results=policy_results,
        final_decision=final_decision,
        reasons=tuple(reasons),
    )
