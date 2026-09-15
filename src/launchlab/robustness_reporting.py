from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from .robustness import MisspecificationPoint


def write_misspecification_csv(
    rows: Iterable[MisspecificationPoint],
    path: str | Path,
) -> Path:
    rows = list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "assumed_value_multiplier",
        "assumed_cost_multiplier",
        "policy",
        "correct_decision_rate",
        "harmful_launch_rate",
        "missed_opportunity_rate",
        "inconclusive_rate",
        "mean_regret",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fields})

    return path


def write_misspecification_regret_svg(
    rows: Iterable[MisspecificationPoint],
    path: str | Path,
    *,
    policy: str,
) -> Path:
    rows = [row for row in rows if row.policy == policy]
    if not rows:
        raise ValueError("no rows found for requested policy.")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    values = sorted({row.assumed_value_multiplier for row in rows})
    costs = sorted({row.assumed_cost_multiplier for row in rows})
    max_regret = max((row.mean_regret for row in rows), default=1.0) or 1.0

    cell_w = 110
    cell_h = 46
    left = 150
    top = 80
    width = left + cell_w * len(costs) + 40
    height = top + cell_h * len(values) + 80

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="30" y="36" font-family="sans-serif" font-size="22" '
        f'font-weight="bold">{escape(policy)} regret under economic misspecification</text>',
    ]

    for ix, cost in enumerate(costs):
        x = left + ix * cell_w + cell_w / 2
        out.append(
            f'<text x="{x:.1f}" y="{top-15}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11">cost × {cost:g}</text>'
        )

    for iy, value in enumerate(reversed(values)):
        y = top + iy * cell_h
        out.append(
            f'<text x="{left-10}" y="{y+28}" text-anchor="end" '
            f'font-family="sans-serif" font-size="11">value × {value:g}</text>'
        )
        for ix, cost in enumerate(costs):
            row = next(
                r for r in rows
                if r.assumed_value_multiplier == value
                and r.assumed_cost_multiplier == cost
            )
            x = left + ix * cell_w
            intensity = 245 - int(145 * (row.mean_regret / max_regret))
            intensity = max(100, min(245, intensity))
            fill = f"rgb(255,{intensity},{intensity})"
            out.append(
                f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" '
                f'fill="{fill}" stroke="#cccccc"/>'
            )
            out.append(
                f'<text x="{x+cell_w/2:.1f}" y="{y+28}" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11">{row.mean_regret:.0f}</text>'
            )

    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")
    return path
