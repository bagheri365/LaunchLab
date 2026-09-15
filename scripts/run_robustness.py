from pathlib import Path

from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario
from launchlab.robustness import run_economic_misspecification_grid
from launchlab.robustness_reporting import (
    write_misspecification_csv,
    write_misspecification_regret_svg,
)


def main() -> None:
    scenario = BenchmarkScenario(
        name="misspecification_study",
        n_users=200_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        # The candidate is deliberately near economic break-even:
        # true lift = 0.001 and incremental serving cost = 0.018/request,
        # so the true break-even lift is 0.0009. This makes misspecification
        # large enough to move the economic launch policies.
        economics=EconomicsConfig(
            annual_traffic=100_000_000,
            value_per_conversion=20.0,
            incumbent_cost_per_request=0.0010,
            candidate_cost_per_request=0.0190,
            product_allowed_loss=0.0001,
            inconclusive_cost=1_000.0,
        ),
        practical_threshold=0.001,
    )

    rows = run_economic_misspecification_grid(
        scenario,
        value_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        cost_multipliers=[0.5, 0.75, 1.0, 1.25, 1.5],
        runs=200,
    )

    table = write_misspecification_csv(
        rows,
        Path("results/tables/economic_misspecification.csv"),
    )

    figure = write_misspecification_regret_svg(
        rows,
        Path("results/figures/economic_misspecification_regret.svg"),
        policy="economic_break_even",
    )

    print(table)
    print(figure)


if __name__ == "__main__":
    main()
