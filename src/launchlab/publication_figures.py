from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"required table not found: {source}")
    with source.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _svg_text(x: float, y: float, text: str, *, size: int = 13, anchor: str = "start") -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" '
        f'text-anchor="{anchor}" font-family="Arial, Helvetica, sans-serif">'
        f"{escaped}</text>"
    )


def _write_svg(path: str | Path, body: list[str], *, width: int = 900, height: int = 560) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        *body,
        "</svg>",
    ]
    output.write_text("\n".join(svg), encoding="utf-8")
    return output


def write_policy_region_svg(
    joint_optima_csv: str | Path,
    output_path: str | Path,
) -> Path:
    rows = _read_csv(joint_optima_csv)
    by_effect: dict[float, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_effect[float(row["treatment_effect"])][row["policy"]] += 1

    policies = sorted({row["policy"] for row in rows})
    effects = sorted(by_effect)
    width, height = 920, 560
    left, top = 185, 105
    cell_w = 220
    cell_h = 72

    maximum = max(
        count
        for counts in by_effect.values()
        for count in counts.values()
    )

    body = [
        _svg_text(40, 42, "Minimum-regret policy regions", size=24),
        _svg_text(
            40,
            68,
            "Cell intensity is proportional to the number of joint-surface operating points won.",
            size=13,
        ),
    ]

    for j, policy in enumerate(policies):
        body.append(
            _svg_text(
                left + j * cell_w + cell_w / 2,
                top - 20,
                policy.replace("_", " "),
                size=12,
                anchor="middle",
            )
        )

    for i, effect in enumerate(effects):
        y = top + i * cell_h
        body.append(_svg_text(40, y + 43, f"true effect {effect:.4f}", size=14))
        for j, policy in enumerate(policies):
            count = by_effect[effect][policy]
            opacity = 0.08 if maximum == 0 else 0.08 + 0.72 * count / maximum
            x = left + j * cell_w
            body.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 8}" '
                f'fill="black" fill-opacity="{opacity:.3f}" stroke="black" stroke-width="1"/>'
            )
            body.append(
                _svg_text(
                    x + (cell_w - 8) / 2,
                    y + 42,
                    str(count),
                    size=20,
                    anchor="middle",
                )
            )

    return _write_svg(output_path, body, width=width, height=height)


def write_delay_crossover_svg(
    delay_optima_csv: str | Path,
    output_path: str | Path,
) -> Path:
    rows = _read_csv(delay_optima_csv)
    grouped: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        grouped[float(row["treatment_effect"])].append(
            (
                float(row["inconclusive_cost"]),
                float(row["minimum_positive_value_probability"]),
            )
        )

    width, height = 900, 560
    left, right, top, bottom = 95, 845, 90, 470
    costs = [c for points in grouped.values() for c, _ in points]
    min_cost, max_cost = min(costs), max(costs)
    min_p, max_p = 0.79, 1.0

    def sx(value: float) -> float:
        if max_cost == min_cost:
            return left
        return left + (value - min_cost) / (max_cost - min_cost) * (right - left)

    def sy(value: float) -> float:
        return bottom - (value - min_p) / (max_p - min_p) * (bottom - top)

    body = [
        _svg_text(40, 42, "Delay cost changes the preferred risk threshold", size=24),
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="black"/>',
        _svg_text((left + right) / 2, 535, "inconclusive / delay cost", size=14, anchor="middle"),
        _svg_text(18, 285, "minimum-regret P(value > 0)", size=13),
    ]

    for p in [0.80, 0.90, 0.95, 0.99]:
        y = sy(p)
        body.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" stroke="black" stroke-opacity="0.12"/>')
        body.append(_svg_text(left - 12, y + 4, f"{p:.2f}", size=12, anchor="end"))

    for cost in sorted(set(costs)):
        x = sx(cost)
        body.append(_svg_text(x, bottom + 24, f"{cost/1000:.0f}k", size=11, anchor="middle"))

    dash_patterns = ["", ' stroke-dasharray="8,5"']
    for idx, (effect, points) in enumerate(sorted(grouped.items())):
        points = sorted(points)
        coords = " ".join(f"{sx(c):.1f},{sy(p):.1f}" for c, p in points)
        dash = dash_patterns[idx % len(dash_patterns)]
        body.append(
            f'<polyline points="{coords}" fill="none" stroke="black" stroke-width="2.5"{dash}/>'
        )
        for c, p in points:
            body.append(
                f'<circle cx="{sx(c):.1f}" cy="{sy(p):.1f}" r="4" fill="white" stroke="black" stroke-width="2"/>'
            )
        body.append(
            _svg_text(
                right - 180,
                105 + idx * 24,
                f"true effect {effect:.4f}",
                size=13,
            )
        )
        x1 = right - 225
        y1 = 101 + idx * 24
        body.append(f'<line x1="{x1}" y1="{y1}" x2="{x1+32}" y2="{y1}" stroke="black" stroke-width="2.5"{dash}/>')

    return _write_svg(output_path, body, width=width, height=height)


def write_misspecification_heatmap_svg(
    misspecification_csv: str | Path,
    output_path: str | Path,
    *,
    policy: str = "economic_break_even",
) -> Path:
    rows = [
        row
        for row in _read_csv(misspecification_csv)
        if row["policy"] == policy
    ]
    values = sorted({float(row["assumed_value_multiplier"]) for row in rows})
    costs = sorted({float(row["assumed_cost_multiplier"]) for row in rows})
    lookup = {
        (
            float(row["assumed_value_multiplier"]),
            float(row["assumed_cost_multiplier"]),
        ): float(row["mean_regret"])
        for row in rows
    }
    maximum = max(lookup.values()) if lookup else 1.0

    width, height = 900, 620
    left, top = 150, 105
    cell_w = min(100, 650 / max(1, len(costs)))
    cell_h = min(72, 410 / max(1, len(values)))

    body = [
        _svg_text(40, 42, "Economic misspecification regret surface", size=24),
        _svg_text(40, 68, f"Policy: {policy.replace('_', ' ')}", size=13),
    ]

    for j, cost in enumerate(costs):
        body.append(
            _svg_text(
                left + j * cell_w + cell_w / 2,
                top - 18,
                f"{cost:.2f}×",
                size=12,
                anchor="middle",
            )
        )
    body.append(_svg_text(left + len(costs) * cell_w / 2, 585, "assumed incremental-cost multiplier", size=14, anchor="middle"))

    for i, value in enumerate(values):
        y = top + i * cell_h
        body.append(_svg_text(35, y + cell_h / 2 + 4, f"value {value:.2f}×", size=12))
        for j, cost in enumerate(costs):
            regret = lookup[(value, cost)]
            opacity = 0.08 + 0.78 * regret / maximum
            x = left + j * cell_w
            body.append(
                f'<rect x="{x}" y="{y}" width="{cell_w-6}" height="{cell_h-6}" '
                f'fill="black" fill-opacity="{opacity:.3f}" stroke="black" stroke-width="1"/>'
            )
            body.append(
                _svg_text(
                    x + (cell_w - 6) / 2,
                    y + cell_h / 2 + 4,
                    f"{regret/1000:.0f}k",
                    size=11,
                    anchor="middle",
                )
            )

    return _write_svg(output_path, body, width=width, height=height)


def write_sample_size_policy_svg(
    joint_optima_csv: str | Path,
    output_path: str | Path,
) -> Path:
    rows = _read_csv(joint_optima_csv)
    grouped: dict[int, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[int(row["n_users"])][row["policy"]] += 1

    sizes = sorted(grouped)
    policies = sorted({row["policy"] for row in rows})
    width, height = 920, 560
    left, right, top, bottom = 95, 850, 90, 470

    maximum = max(sum(grouped[n].values()) for n in sizes)

    body = [
        _svg_text(40, 42, "Minimum-regret policy regions by experiment size", size=24),
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="black"/>',
    ]

    bar_group = (right - left) / max(1, len(sizes))
    bar_w = bar_group / (len(policies) + 1)

    for i, n_users in enumerate(sizes):
        x0 = left + i * bar_group
        body.append(
            _svg_text(
                x0 + bar_group / 2,
                bottom + 26,
                f"{n_users/1000:.0f}k",
                size=12,
                anchor="middle",
            )
        )
        for j, policy in enumerate(policies):
            count = grouped[n_users][policy]
            height_px = 0 if maximum == 0 else (bottom - top) * count / maximum
            x = x0 + (j + 0.5) * bar_w
            y = bottom - height_px
            opacity = 0.25 + 0.18 * j
            body.append(
                f'<rect x="{x}" y="{y}" width="{bar_w*0.72}" height="{height_px}" '
                f'fill="black" fill-opacity="{min(opacity,0.9):.2f}" stroke="black"/>'
            )

    body.append(_svg_text((left + right) / 2, 535, "users per experiment", size=14, anchor="middle"))

    legend_y = 102
    for j, policy in enumerate(policies):
        body.append(
            f'<rect x="{right-245}" y="{legend_y + j*24 - 10}" width="16" height="12" '
            f'fill="black" fill-opacity="{min(0.25+0.18*j,0.9):.2f}" stroke="black"/>'
        )
        body.append(_svg_text(right - 220, legend_y + j * 24, policy.replace("_", " "), size=12))

    return _write_svg(output_path, body, width=width, height=height)
