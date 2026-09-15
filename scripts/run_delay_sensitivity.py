from launchlab.delay_reporting import (
    write_delay_optima_csv,
    write_delay_sensitivity_csv,
)
from launchlab.delay_sensitivity import (
    run_delay_cost_sensitivity,
    select_minimum_regret_thresholds,
)
from launchlab.economics import EconomicsConfig


def main() -> None:
    economics = EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )

    thresholds = [0.80, 0.90, 0.95, 0.975, 0.99]
    delay_costs = [
        0.0,
        1_000.0,
        5_000.0,
        10_000.0,
        25_000.0,
        50_000.0,
        75_000.0,
        100_000.0,
        150_000.0,
        250_000.0,
    ]

    rows = []
    for treatment_effect in [0.0010, 0.0008]:
        rows.extend(
            run_delay_cost_sensitivity(
                n_users=200_000,
                baseline_conversion=0.05,
                treatment_effect=treatment_effect,
                economics=economics,
                inconclusive_costs=delay_costs,
                probability_thresholds=thresholds,
                seeds_per_threshold=500,
            )
        )

    optima = select_minimum_regret_thresholds(rows)

    table = write_delay_sensitivity_csv(
        rows,
        "results/tables/delay_cost_sensitivity.csv",
    )
    optimum_table = write_delay_optima_csv(
        optima,
        "results/tables/delay_cost_optima.csv",
    )

    print(table)
    print(optimum_table)
    print()
    print(
        f"{'effect':>8} {'delay cost':>12} "
        f"{'best P(value>0)':>16} {'mean regret':>12}"
    )
    for row in optima:
        print(
            f"{row.treatment_effect:>8.4f} "
            f"{row.inconclusive_cost:>12.0f} "
            f"{row.minimum_positive_value_probability:>16.3f} "
            f"{row.mean_regret:>12.0f}"
        )


if __name__ == "__main__":
    main()
