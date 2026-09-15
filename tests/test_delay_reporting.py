from launchlab.delay_reporting import (
    write_delay_optima_csv,
    write_delay_sensitivity_csv,
)
from launchlab.delay_sensitivity import DelayCostOptimum, DelaySensitivityPoint


def test_delay_sensitivity_csv_schema(tmp_path):
    rows = [
        DelaySensitivityPoint(
            treatment_effect=0.001,
            inconclusive_cost=1000.0,
            minimum_positive_value_probability=0.95,
            correct_decision_rate=0.1,
            harmful_launch_rate=0.0,
            missed_opportunity_rate=0.05,
            inconclusive_rate=0.85,
            mean_regret=5000.0,
        )
    ]
    path = write_delay_sensitivity_csv(rows, tmp_path / "delay.csv")
    header = path.read_text().splitlines()[0]
    assert "inconclusive_cost" in header
    assert "minimum_positive_value_probability" in header
    assert "mean_regret" in header


def test_delay_optima_csv_schema(tmp_path):
    rows = [
        DelayCostOptimum(
            treatment_effect=0.001,
            inconclusive_cost=1000.0,
            minimum_positive_value_probability=0.95,
            mean_regret=5000.0,
        )
    ]
    path = write_delay_optima_csv(rows, tmp_path / "optima.csv")
    header = path.read_text().splitlines()[0]
    assert header == (
        "treatment_effect,inconclusive_cost,"
        "minimum_positive_value_probability,mean_regret"
    )
