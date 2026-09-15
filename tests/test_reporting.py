import csv

from launchlab.decision_power import PowerComparison
from launchlab.evaluation import PolicyAggregate
from launchlab.reporting import (
    write_policy_aggregates_csv,
    write_power_comparison_svg,
    write_power_comparisons_csv,
    write_regret_svg,
)


def policy_rows():
    return [
        PolicyAggregate(
            scenario="s1",
            policy="economic_break_even",
            runs=10,
            correct_decision_rate=0.7,
            harmful_launch_rate=0.1,
            missed_opportunity_rate=0.1,
            inconclusive_rate=0.1,
            mean_regret=123.0,
        )
    ]


def power_rows():
    return [
        PowerComparison(
            scenario="s1",
            policy="economic_break_even",
            statistical_power=0.8,
            decision_power=0.5,
            gap=-0.3,
        )
    ]


def test_policy_csv_schema(tmp_path):
    path = write_policy_aggregates_csv(policy_rows(), tmp_path / "policy.csv")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0]) == [
        "scenario",
        "policy",
        "runs",
        "correct_decision_rate",
        "harmful_launch_rate",
        "missed_opportunity_rate",
        "inconclusive_rate",
        "mean_regret",
    ]
    assert rows[0]["scenario"] == "s1"


def test_power_csv_schema(tmp_path):
    path = write_power_comparisons_csv(power_rows(), tmp_path / "power.csv")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0]) == [
        "scenario",
        "policy",
        "statistical_power",
        "decision_power",
        "gap",
    ]


def test_power_svg_is_written(tmp_path):
    path = write_power_comparison_svg(power_rows(), tmp_path / "power.svg")
    text = path.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "Statistical power vs decision power" in text
    assert "economic_break_even" in text


def test_regret_svg_is_written(tmp_path):
    path = write_regret_svg(policy_rows(), tmp_path / "regret.svg")
    text = path.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "Mean economic regret by policy" in text
    assert "123" in text
