from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from .decision_power import PowerComparison
from .evaluation import PolicyAggregate


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_policy_aggregates_csv(
    rows: Iterable[PolicyAggregate],
    path: str | Path,
) -> Path:
    path = Path(path)
    _ensure_parent(path)
    fieldnames = [
        "scenario",
        "policy",
        "runs",
        "correct_decision_rate",
        "harmful_launch_rate",
        "missed_opportunity_rate",
        "inconclusive_rate",
        "mean_regret",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: getattr(row, name) for name in fieldnames})
    return path


def write_power_comparisons_csv(
    rows: Iterable[PowerComparison],
    path: str | Path,
) -> Path:
    path = Path(path)
    _ensure_parent(path)
    fieldnames = [
        "scenario",
        "policy",
        "statistical_power",
        "decision_power",
        "gap",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: getattr(row, name) for name in fieldnames})
    return path


def _svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="40" y="38" font-family="sans-serif" font-size="22" '
        f'font-weight="bold">{escape(title)}</text>',
    ]


def write_power_comparison_svg(
    rows: Iterable[PowerComparison],
    path: str | Path,
) -> Path:
    rows = list(rows)
    path = Path(path)
    _ensure_parent(path)

    width = 1100
    row_h = 28
    top = 80
    left = 350
    plot_w = 680
    height = max(220, top + row_h * len(rows) + 70)

    out = _svg_header(width, height, "Statistical power vs decision power")
    out += [
        f'<line x1="{left}" y1="{top-15}" x2="{left}" y2="{height-45}" stroke="black"/>',
        f'<line x1="{left}" y1="{height-45}" x2="{left+plot_w}" y2="{height-45}" stroke="black"/>',
    ]

    for tick in range(0, 11, 2):
        x = left + plot_w * (tick / 10)
        out.append(
            f'<line x1="{x:.1f}" y1="{top-15}" x2="{x:.1f}" y2="{height-45}" '
            'stroke="#dddddd"/>'
        )
        out.append(
            f'<text x="{x:.1f}" y="{height-20}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="12">{tick/10:.1f}</text>'
        )

    for i, row in enumerate(rows):
        y = top + i * row_h
        label = f"{row.scenario} · {row.policy}"
        out.append(
            f'<text x="{left-12}" y="{y+12}" text-anchor="end" '
            f'font-family="sans-serif" font-size="11">{escape(label)}</text>'
        )
        stat_w = max(0.0, min(1.0, row.statistical_power)) * plot_w
        dec_w = max(0.0, min(1.0, row.decision_power)) * plot_w
        out.append(
            f'<rect x="{left}" y="{y}" width="{stat_w:.1f}" height="8" fill="#999999"/>'
        )
        out.append(
            f'<rect x="{left}" y="{y+11}" width="{dec_w:.1f}" height="8" fill="#222222"/>'
        )

    out += [
        f'<rect x="{left}" y="52" width="14" height="8" fill="#999999"/>',
        f'<text x="{left+20}" y="60" font-family="sans-serif" font-size="12">statistical power</text>',
        f'<rect x="{left+150}" y="52" width="14" height="8" fill="#222222"/>',
        f'<text x="{left+170}" y="60" font-family="sans-serif" font-size="12">decision power</text>',
        "</svg>",
    ]
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def write_regret_svg(
    rows: Iterable[PolicyAggregate],
    path: str | Path,
) -> Path:
    rows = list(rows)
    path = Path(path)
    _ensure_parent(path)

    width = 1100
    row_h = 24
    top = 70
    left = 350
    plot_w = 680
    height = max(220, top + row_h * len(rows) + 60)
    max_regret = max((row.mean_regret for row in rows), default=1.0) or 1.0

    out = _svg_header(width, height, "Mean economic regret by policy")
    out.append(
        f'<line x1="{left}" y1="{height-45}" x2="{left+plot_w}" y2="{height-45}" stroke="black"/>'
    )

    for i, row in enumerate(rows):
        y = top + i * row_h
        label = f"{row.scenario} · {row.policy}"
        bar_w = (row.mean_regret / max_regret) * plot_w
        out.append(
            f'<text x="{left-12}" y="{y+12}" text-anchor="end" '
            f'font-family="sans-serif" font-size="11">{escape(label)}</text>'
        )
        out.append(
            f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="14" fill="#444444"/>'
        )
        out.append(
            f'<text x="{left+bar_w+6:.1f}" y="{y+12}" '
            f'font-family="sans-serif" font-size="11">{row.mean_regret:.0f}</text>'
        )

    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")
    return path
