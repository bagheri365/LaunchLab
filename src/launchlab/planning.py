from __future__ import annotations

from dataclasses import dataclass

from .economics import EconomicsConfig, required_lift_for_break_even
from .power import required_sample_size_per_arm
from .workflow import WorkflowResult


@dataclass(frozen=True)
class TrafficRequirement:
    name: str
    threshold: float
    assumed_effect: float
    decision_margin: float
    required_per_arm: int
    current_per_arm: int
    additional_per_arm: int

    @property
    def total_required(self) -> int:
        return 2 * self.required_per_arm

    @property
    def total_additional(self) -> int:
        return 2 * self.additional_per_arm


@dataclass(frozen=True)
class DecisionReadinessPlan:
    baseline_rate: float
    current_per_arm: int
    requirements: tuple[TrafficRequirement, ...]
    binding_requirement: TrafficRequirement

    @property
    def total_additional_users(self) -> int:
        return self.binding_requirement.total_additional


def plan_decision_readiness(
    workflow_result: WorkflowResult,
    economics: EconomicsConfig,
    *,
    practical_threshold: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> DecisionReadinessPlan:
    if workflow_result.effect is None:
        raise ValueError("workflow_result must contain an estimated effect.")
    if workflow_result.srm.control_count <= 0 or workflow_result.srm.treatment_count <= 0:
        raise ValueError("workflow_result must contain positive exposed arm counts.")
    if practical_threshold <= 0:
        raise ValueError("practical_threshold must be positive.")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")
    if not 0.0 < power < 1.0:
        raise ValueError("power must be between 0 and 1.")

    baseline = workflow_result.effect.control_rate
    current_per_arm = min(
        workflow_result.srm.control_count,
        workflow_result.srm.treatment_count,
    )

    observed = workflow_result.effect.absolute_effect
    thresholds: list[tuple[str, float]] = [
        ("statistical_superiority", 0.0),
        ("practical_significance", practical_threshold),
    ]

    economic_threshold = required_lift_for_break_even(economics)
    if economic_threshold > 0:
        thresholds.append(("economic_break_even", economic_threshold))

    requirements: list[TrafficRequirement] = []
    for name, threshold in thresholds:
        null_rate = baseline + threshold
        assumed_rate = baseline + observed
        if not 0.0 < null_rate < 1.0 or not 0.0 < assumed_rate < 1.0:
            raise ValueError("planned conversion rates must lie between 0 and 1.")

        margin = observed - threshold
        if margin == 0:
            required = 10**18
        else:
            required = required_sample_size_per_arm(
                p_control=min(null_rate, assumed_rate),
                p_treatment=max(null_rate, assumed_rate),
                alpha=alpha,
                target_power=power,
            )

        requirements.append(
            TrafficRequirement(
                name=name,
                threshold=threshold,
                assumed_effect=observed,
                decision_margin=margin,
                required_per_arm=required,
                current_per_arm=current_per_arm,
                additional_per_arm=max(0, required - current_per_arm),
            )
        )

    binding = max(requirements, key=lambda item: item.required_per_arm)
    return DecisionReadinessPlan(
        baseline_rate=baseline,
        current_per_arm=current_per_arm,
        requirements=tuple(requirements),
        binding_requirement=binding,
    )
