from launchlab.economics import EconomicsConfig
from launchlab.risk_adjustment import run_probability_risk_benchmark


def print_case(
    *,
    label: str,
    treatment_effect: float,
    economics: EconomicsConfig,
) -> None:
    rows = run_probability_risk_benchmark(
        n_users=200_000,
        baseline_conversion=0.05,
        treatment_effect=treatment_effect,
        economics=economics,
        probability_thresholds=[0.80, 0.90, 0.95, 0.975, 0.99],
        seeds_per_threshold=500,
    )

    print(f"\n{label} (true effect={treatment_effect:.4f})")
    print(
        f"{'P(value>0)':>10} {'correct':>8} {'harmful':>8} "
        f"{'missed':>8} {'inconcl':>8} {'regret':>10}"
    )
    for row in rows:
        print(
            f"{row.minimum_positive_value_probability:>10.3f} "
            f"{row.correct_decision_rate:>8.3f} "
            f"{row.harmful_launch_rate:>8.3f} "
            f"{row.missed_opportunity_rate:>8.3f} "
            f"{row.inconclusive_rate:>8.3f} "
            f"{row.mean_regret:>10.0f}"
        )


def main() -> None:
    economics = EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.001,
        candidate_cost_per_request=0.019,
        inconclusive_cost=1_000.0,
    )

    # Break-even lift is 0.0009. Evaluate one case on each side so the
    # benchmark can measure both missed opportunities and harmful launches.
    print_case(
        label="Profitable candidate",
        treatment_effect=0.0010,
        economics=economics,
    )
    print_case(
        label="Unprofitable candidate",
        treatment_effect=0.0008,
        economics=economics,
    )


if __name__ == "__main__":
    main()
