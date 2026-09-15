import csv

from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario
from launchlab.robustness import run_economic_misspecification_grid
from launchlab.robustness_reporting import (
    write_misspecification_csv,
    write_misspecification_regret_svg,
)


def rows():
    scenario = BenchmarkScenario(
        name="reporting_case",
        n_users=30_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=EconomicsConfig(
            annual_traffic=50_000_000,
            value_per_conversion=20.0,
            incumbent_cost_per_request=0.0010,
            candidate_cost_per_request=0.0015,
        ),
        practical_threshold=0.001,
    )
    return run_economic_misspecification_grid(
        scenario,
        value_multipliers=[0.5, 1.0],
        cost_multipliers=[0.5, 1.0],
        runs=5,
    )


def test_csv_schema(tmp_path):
    path = write_misspecification_csv(rows(), tmp_path / "misspec.csv")
    with path.open(newline="", encoding="utf-8") as f:
        parsed = list(csv.DictReader(f))
    assert parsed
    assert "mean_regret" in parsed[0]
    assert "harmful_launch_rate" in parsed[0]


def test_svg_contains_policy_title(tmp_path):
    data = rows()
    policy = data[0].policy
    path = write_misspecification_regret_svg(
        data,
        tmp_path / "regret.svg",
        policy=policy,
    )
    text = path.read_text(encoding="utf-8")
    assert "<svg" in text
    assert policy in text
