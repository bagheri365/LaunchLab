from pathlib import Path

from launchlab.reporting import write_sensitivity_csv, write_sensitivity_svg
from launchlab.sensitivity import run_sensitivity_grid


def main() -> None:
    rows = run_sensitivity_grid(
        baseline_conversion=0.05,
        treatment_effect=0.0015,
        annual_traffic=100_000_000,
        incumbent_cost_per_request=0.0010,
        sample_sizes=[25_000, 100_000, 400_000, 1_600_000],
        values_per_conversion=[5.0, 10.0, 20.0, 40.0],
        candidate_costs=[0.0010, 0.0014, 0.0020],
        practical_thresholds=[0.0005, 0.0010, 0.0020],
        seed=42,
    )

    table = write_sensitivity_csv(
        rows,
        Path("results/tables/sensitivity_grid.csv"),
    )

    figure = write_sensitivity_svg(
        [
            row for row in rows
            if row.candidate_cost_per_request == 0.0014
            and row.practical_threshold == 0.0010
        ],
        Path("results/figures/economic_break_even_sensitivity.svg"),
        policy="economic_break_even",
        x_field="sample_size",
        y_field="value_per_conversion",
    )

    print(table)
    print(figure)


if __name__ == "__main__":
    main()
