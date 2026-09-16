from collections import Counter

from launchlab.economics import EconomicsConfig
from launchlab.joint_reporting import (
    write_joint_optima_csv,
    write_joint_surface_csv,
)
from launchlab.joint_surface import (
    run_joint_decision_surface,
    select_minimum_regret_policies,
)


def main() -> None:
    economics = EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )

    rows = []
    for treatment_effect in [0.0010, 0.0008]:
        rows.extend(
            run_joint_decision_surface(
                baseline_conversion=0.05,
                treatment_effect=treatment_effect,
                true_economics=economics,
                n_users_values=[50_000, 100_000, 200_000, 500_000],
                value_multipliers=[0.75, 1.0, 1.25],
                cost_multipliers=[0.75, 1.0, 1.25],
                inconclusive_costs=[1_000.0, 25_000.0, 75_000.0, 150_000.0],
                probability_threshold=0.95,
                runs=100,
            )
        )

    optima = select_minimum_regret_policies(rows)

    detail_path = write_joint_surface_csv(
        rows,
        "results/tables/joint_decision_surface.csv",
    )
    optima_path = write_joint_optima_csv(
        optima,
        "results/tables/joint_decision_optima.csv",
    )

    print(detail_path)
    print(optima_path)
    print()

    counts = Counter(row.policy for row in optima)
    print("minimum-regret policy counts")
    for policy, count in sorted(counts.items()):
        print(f"{policy:<35} {count:>4}")

    print()
    print("regret decomposition at correctly specified operating points")
    lookup = {
        (
            row.treatment_effect,
            row.n_users,
            row.assumed_value_multiplier,
            row.assumed_cost_multiplier,
            row.inconclusive_cost,
            row.policy,
        ): row
        for row in rows
    }
    for optimum in optima:
        if (
            optimum.assumed_value_multiplier == 1.0
            and optimum.assumed_cost_multiplier == 1.0
        ):
            row = lookup[(
                optimum.treatment_effect,
                optimum.n_users,
                optimum.assumed_value_multiplier,
                optimum.assumed_cost_multiplier,
                optimum.inconclusive_cost,
                optimum.policy,
            )]
            print(
                f"effect={row.treatment_effect:.4f} "
                f"n={row.n_users:<7} "
                f"delay={row.inconclusive_cost:>8.0f} "
                f"policy={row.policy:<25} "
                f"harmful={row.harmful_launch_regret:>9.0f} "
                f"missed={row.missed_opportunity_regret:>9.0f} "
                f"delay_regret={row.inconclusive_regret:>9.0f} "
                f"total={row.mean_regret:>9.0f}"
            )

    print()
    print("selected correctly specified operating points")
    for row in optima:
        if (
            row.assumed_value_multiplier == 1.0
            and row.assumed_cost_multiplier == 1.0
        ):
            print(
                f"effect={row.treatment_effect:.4f} "
                f"n={row.n_users:<7} "
                f"delay={row.inconclusive_cost:>8.0f} "
                f"policy={row.policy:<35} "
                f"regret={row.mean_regret:>10.0f}"
            )


if __name__ == "__main__":
    main()
