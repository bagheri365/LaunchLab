from __future__ import annotations

import csv
from pathlib import Path

from .delay_sensitivity import DelayCostOptimum, DelaySensitivityPoint


def write_delay_sensitivity_csv(
    rows: list[DelaySensitivityPoint],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "treatment_effect",
                "inconclusive_cost",
                "minimum_positive_value_probability",
                "correct_decision_rate",
                "harmful_launch_rate",
                "missed_opportunity_rate",
                "inconclusive_rate",
                "mean_regret",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.treatment_effect,
                    row.inconclusive_cost,
                    row.minimum_positive_value_probability,
                    row.correct_decision_rate,
                    row.harmful_launch_rate,
                    row.missed_opportunity_rate,
                    row.inconclusive_rate,
                    row.mean_regret,
                ]
            )

    return output


def write_delay_optima_csv(
    rows: list[DelayCostOptimum],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "treatment_effect",
                "inconclusive_cost",
                "minimum_positive_value_probability",
                "mean_regret",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.treatment_effect,
                    row.inconclusive_cost,
                    row.minimum_positive_value_probability,
                    row.mean_regret,
                ]
            )

    return output
