from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DelayCrossover:
    treatment_effect: float
    baseline_probability_threshold: float
    crossover_inconclusive_cost: float | None
    crossover_probability_threshold: float | None


@dataclass(frozen=True)
class MisspecificationRegretRange:
    policy: str
    minimum_mean_regret: float
    maximum_mean_regret: float


@dataclass(frozen=True)
class ResearchSummary:
    joint_policy_counts: tuple[tuple[str, int], ...]
    joint_policy_counts_by_effect: tuple[
        tuple[float, tuple[tuple[str, int], ...]],
        ...
    ]
    delay_crossovers: tuple[DelayCrossover, ...]
    misspecification_regret_ranges: tuple[MisspecificationRegretRange, ...]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"required research table not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _joint_policy_counts(
    rows: list[dict[str, str]],
) -> tuple[
    tuple[tuple[str, int], ...],
    tuple[tuple[float, tuple[tuple[str, int], ...]], ...],
]:
    overall = Counter(row["policy"] for row in rows)
    by_effect: dict[float, Counter[str]] = defaultdict(Counter)

    for row in rows:
        effect = float(row["treatment_effect"])
        by_effect[effect][row["policy"]] += 1

    overall_rows = tuple(sorted(overall.items()))
    effect_rows = tuple(
        (effect, tuple(sorted(counter.items())))
        for effect, counter in sorted(by_effect.items())
    )
    return overall_rows, effect_rows


def _delay_crossovers(
    rows: list[dict[str, str]],
) -> tuple[DelayCrossover, ...]:
    grouped: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        grouped[float(row["treatment_effect"])].append(
            (
                float(row["inconclusive_cost"]),
                float(row["minimum_positive_value_probability"]),
            )
        )

    output: list[DelayCrossover] = []
    for effect, points in sorted(grouped.items()):
        points.sort()
        baseline = max(probability for _, probability in points)

        crossover_cost = None
        crossover_probability = None
        for cost, probability in points:
            if probability < baseline:
                crossover_cost = cost
                crossover_probability = probability
                break

        output.append(
            DelayCrossover(
                treatment_effect=effect,
                baseline_probability_threshold=baseline,
                crossover_inconclusive_cost=crossover_cost,
                crossover_probability_threshold=crossover_probability,
            )
        )

    return tuple(output)


def _misspecification_regret_ranges(
    rows: list[dict[str, str]],
) -> tuple[MisspecificationRegretRange, ...]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["policy"]].append(float(row["mean_regret"]))

    return tuple(
        MisspecificationRegretRange(
            policy=policy,
            minimum_mean_regret=min(values),
            maximum_mean_regret=max(values),
        )
        for policy, values in sorted(grouped.items())
    )


def build_research_summary(
    tables_dir: str | Path = "results/tables",
) -> ResearchSummary:
    root = Path(tables_dir)

    joint_rows = _read_csv(root / "joint_decision_optima.csv")
    delay_rows = _read_csv(root / "delay_cost_optima.csv")
    misspec_rows = _read_csv(root / "economic_misspecification.csv")

    overall_counts, counts_by_effect = _joint_policy_counts(joint_rows)

    return ResearchSummary(
        joint_policy_counts=overall_counts,
        joint_policy_counts_by_effect=counts_by_effect,
        delay_crossovers=_delay_crossovers(delay_rows),
        misspecification_regret_ranges=_misspecification_regret_ranges(
            misspec_rows
        ),
    )


def render_research_summary_markdown(summary: ResearchSummary) -> str:
    lines = [
        "# LaunchLab Research Summary",
        "",
        "This report is generated from reproducible benchmark tables produced by "
        "the economic misspecification, delay-cost, and joint decision-surface "
        "experiments.",
        "",
        "## Minimum-regret policy regions",
        "",
        "| Policy | Joint-surface wins |",
        "| --- | ---: |",
    ]

    for policy, count in summary.joint_policy_counts:
        lines.append(f"| `{policy}` | {count} |")

    lines.extend(
        [
            "",
            "### Wins by true treatment effect",
            "",
            "| True effect | Policy | Wins |",
            "| ---: | --- | ---: |",
        ]
    )
    for effect, counts in summary.joint_policy_counts_by_effect:
        for policy, count in counts:
            lines.append(f"| {effect:.4f} | `{policy}` | {count} |")

    lines.extend(
        [
            "",
            "## Delay-cost crossover",
            "",
            "The crossover is the first tested inconclusive-cost level where the "
            "minimum-regret probability threshold becomes less conservative than "
            "the maximum threshold selected at low delay cost.",
            "",
            "| True effect | Low-cost threshold | Crossover delay cost | "
            "Threshold after crossover |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary.delay_crossovers:
        crossover_cost = (
            "not observed"
            if row.crossover_inconclusive_cost is None
            else f"{row.crossover_inconclusive_cost:,.0f}"
        )
        crossover_probability = (
            "not observed"
            if row.crossover_probability_threshold is None
            else f"{row.crossover_probability_threshold:.3f}"
        )
        lines.append(
            f"| {row.treatment_effect:.4f} | "
            f"{row.baseline_probability_threshold:.3f} | "
            f"{crossover_cost} | {crossover_probability} |"
        )

    lines.extend(
        [
            "",
            "## Economic misspecification regret range",
            "",
            "| Policy | Minimum mean regret | Maximum mean regret |",
            "| --- | ---: | ---: |",
        ]
    )
    for row in summary.misspecification_regret_ranges:
        lines.append(
            f"| `{row.policy}` | "
            f"{row.minimum_mean_regret:,.0f} | "
            f"{row.maximum_mean_regret:,.0f} |"
        )

    lines.extend(
        [
            "",
            "## Main empirical takeaways",
            "",
            "- No single launch rule is uniformly minimum-regret across the joint "
            "operating surface.",
            "- The economically preferred degree of risk aversion depends on the "
            "cost of delaying a decision.",
            "- Economic misspecification can materially change regret even when "
            "the underlying experiment data are unchanged.",
            "- Sample size, economic assumptions, and delay cost therefore need "
            "to be evaluated jointly when assessing launch readiness.",
            "",
            "## Source tables",
            "",
            "- `results/tables/joint_decision_optima.csv`",
            "- `results/tables/delay_cost_optima.csv`",
            "- `results/tables/economic_misspecification.csv`",
            "",
        ]
    )

    return "\n".join(lines)


def write_research_summary(
    summary: ResearchSummary,
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_research_summary_markdown(summary),
        encoding="utf-8",
    )
    return output
