from __future__ import annotations

import csv
from pathlib import Path

from .joint_surface import JointSurfaceOptimum, JointSurfacePoint


def write_joint_surface_csv(
    rows: list[JointSurfacePoint],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "treatment_effect",
                "n_users",
                "assumed_value_multiplier",
                "assumed_cost_multiplier",
                "inconclusive_cost",
                "policy",
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
                    row.n_users,
                    row.assumed_value_multiplier,
                    row.assumed_cost_multiplier,
                    row.inconclusive_cost,
                    row.policy,
                    row.correct_decision_rate,
                    row.harmful_launch_rate,
                    row.missed_opportunity_rate,
                    row.inconclusive_rate,
                    row.mean_regret,
                ]
            )

    return output


def write_joint_optima_csv(
    rows: list[JointSurfaceOptimum],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "treatment_effect",
                "n_users",
                "assumed_value_multiplier",
                "assumed_cost_multiplier",
                "inconclusive_cost",
                "policy",
                "mean_regret",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.treatment_effect,
                    row.n_users,
                    row.assumed_value_multiplier,
                    row.assumed_cost_multiplier,
                    row.inconclusive_cost,
                    row.policy,
                    row.mean_regret,
                ]
            )

    return output
