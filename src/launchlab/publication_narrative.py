from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


def _read(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_publication_results(
    *,
    joint_optima_csv: str | Path,
    delay_optima_csv: str | Path,
    misspecification_csv: str | Path,
) -> str:
    joint = _read(joint_optima_csv)
    delay = _read(delay_optima_csv)
    misspec = _read(misspecification_csv)

    overall = Counter(row["policy"] for row in joint)
    by_effect: dict[float, Counter[str]] = defaultdict(Counter)
    for row in joint:
        by_effect[float(row["treatment_effect"])][row["policy"]] += 1

    delay_by_effect: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for row in delay:
        delay_by_effect[float(row["treatment_effect"])].append(
            (
                float(row["inconclusive_cost"]),
                float(row["minimum_positive_value_probability"]),
            )
        )

    economic_rows = [
        row for row in misspec if row["policy"] == "economic_break_even"
    ]
    min_regret = min(float(row["mean_regret"]) for row in economic_rows)
    max_regret = max(float(row["mean_regret"]) for row in economic_rows)

    lines = [
        "# Publication Results",
        "",
        "## Headline findings",
        "",
        "The joint decision surface shows that no single launch rule is uniformly "
        "minimum-regret across the evaluated operating conditions.",
        "",
        "Minimum-regret policy-region counts:",
    ]
    for policy, count in sorted(overall.items()):
        lines.append(f"- `{policy}`: {count} operating points")

    lines.extend(["", "By true treatment effect:"])
    for effect, counts in sorted(by_effect.items()):
        rendered = ", ".join(
            f"`{policy}` {count}"
            for policy, count in sorted(counts.items())
        )
        lines.append(f"- effect `{effect:.4f}`: {rendered}")

    lines.extend(
        [
            "",
            "## Cost of indecision",
            "",
        ]
    )
    for effect, points in sorted(delay_by_effect.items()):
        points = sorted(points)
        baseline = max(p for _, p in points)
        crossover = next(
            ((cost, p) for cost, p in points if p < baseline),
            None,
        )
        if crossover is None:
            lines.append(
                f"- effect `{effect:.4f}`: no risk-threshold crossover was observed."
            )
        else:
            cost, probability = crossover
            lines.append(
                f"- effect `{effect:.4f}`: the preferred probability threshold "
                f"first falls below `{baseline:.3f}` at an inconclusive cost of "
                f"`${cost:,.0f}`, where the preferred threshold is `{probability:.3f}`."
            )

    lines.extend(
        [
            "",
            "## Economic misspecification",
            "",
            "For the economic break-even policy, mean regret across the tested "
            f"misspecification grid ranges from `${min_regret:,.0f}` to "
            f"`${max_regret:,.0f}`.",
            "",
            "## Interpretation",
            "",
            "These experiments support a decision-aware view of model launches: "
            "sample size determines how quickly uncertainty contracts, economic "
            "assumptions determine where the launch boundary lies, and the cost "
            "of delay determines how conservative it is rational to be. The "
            "preferred launch rule therefore depends on the operating regime "
            "rather than on statistical significance alone.",
            "",
        ]
    )
    return "\n".join(lines)


def write_publication_results(text: str, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return output
