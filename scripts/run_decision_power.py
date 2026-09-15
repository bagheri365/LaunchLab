from launchlab.decision_power import compare_statistical_and_decision_power
from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario


def econ(
    candidate_cost: float,
    value_per_conversion: float = 20.0,
    product_allowed_loss: float = 0.0001,
) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=value_per_conversion,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=product_allowed_loss,
        inconclusive_cost=1_000.0,
    )


def main() -> None:
    scenarios = [
        BenchmarkScenario(
            name="easy_large_win",
            n_users=40_000,
            baseline_conversion=0.05,
            treatment_effect=0.01,
            economics=econ(0.0012),
        ),
        BenchmarkScenario(
            name="expensive_quality_gain",
            n_users=100_000,
            baseline_conversion=0.05,
            treatment_effect=0.0015,
            economics=econ(0.0040),
        ),
        BenchmarkScenario(
            name="cheaper_slight_loss",
            n_users=120_000,
            baseline_conversion=0.05,
            treatment_effect=-0.00003,
            economics=econ(0.0),
        ),
        BenchmarkScenario(
            name="near_break_even",
            n_users=800_000,
            baseline_conversion=0.05,
            treatment_effect=0.001,
            economics=econ(0.020),
        ),
        BenchmarkScenario(
            name="misspecified_value",
            n_users=100_000,
            baseline_conversion=0.05,
            treatment_effect=0.0008,
            economics=econ(0.0014, value_per_conversion=20.0),
            policy_economics=econ(0.0014, value_per_conversion=5.0),
        ),
    ]

    rows = compare_statistical_and_decision_power(
        scenarios,
        seeds_per_scenario=100,
    )

    print(
        f"{'scenario':<24} {'policy':<30} "
        f"{'stat_power':>10} {'decision_power':>14} {'gap':>9}"
    )
    print("-" * 92)

    for row in rows:
        print(
            f"{row.scenario:<24} {row.policy:<30} "
            f"{row.statistical_power:>10.2f} "
            f"{row.decision_power:>14.2f} "
            f"{row.gap:>9.2f}"
        )


if __name__ == "__main__":
    main()
