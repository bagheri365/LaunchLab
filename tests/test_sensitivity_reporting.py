import csv

from launchlab.reporting import write_sensitivity_csv, write_sensitivity_svg
from launchlab.sensitivity import run_sensitivity_grid


def rows():
    return run_sensitivity_grid(
        baseline_conversion=0.05,
        treatment_effect=0.003,
        annual_traffic=10_000_000,
        incumbent_cost_per_request=0.001,
        sample_sizes=[5_000, 20_000],
        values_per_conversion=[10.0, 20.0],
        candidate_costs=[0.001],
        practical_thresholds=[0.001],
        seed=3,
    )


def test_sensitivity_csv_schema(tmp_path):
    path = write_sensitivity_csv(rows(), tmp_path / "sensitivity.csv")
    with path.open(newline="", encoding="utf-8") as f:
        parsed = list(csv.DictReader(f))
    assert parsed
    assert "decision" in parsed[0]
    assert "threshold" in parsed[0]


def test_sensitivity_svg_contains_decisions(tmp_path):
    path = write_sensitivity_svg(
        rows(),
        tmp_path / "map.svg",
        policy="economic_break_even",
    )
    text = path.read_text(encoding="utf-8")
    assert "<svg" in text
    assert "economic_break_even sensitivity" in text
    assert any(word in text for word in ["SHIP", "REJECT", "INCONCLUSIVE"])
