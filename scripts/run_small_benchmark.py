from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario, run_monte_carlo_benchmark


def econ(candidate_cost: float) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=0.0001,
        inconclusive_cost=1_000.0,
    )


def main() -> None:
    scenarios = [
        BenchmarkScenario(
            name="easy_large_win",
            n_users=20_000,
            baseline_conversion=0.05,
            treatment_effect=0.01,
            economics=econ(0.0011),
        ),
        BenchmarkScenario(
            name="small_profitable_win",
            n_users=20_000,
            baseline_conversion=0.05,
            treatment_effect=0.001,
            economics=econ(0.0010),
        ),
        BenchmarkScenario(
            name="cheap_slight_loss",
            n_users=20_000,
            baseline_conversion=0.05,
            treatment_effect=-0.00002,
            economics=econ(0.0),
        ),
    ]

    results = run_monte_carlo_benchmark(scenarios, seeds_per_scenario=50)

    header = (
        f"{'scenario':<22} {'policy':<30} {'correct':>8} "
        f"{'harmful':>8} {'missed':>8} {'inconcl':>8} {'regret':>12}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        print(
            f"{r.scenario:<22} {r.policy:<30} "
            f"{r.correct_decision_rate:>8.2f} "
            f"{r.harmful_launch_rate:>8.2f} "
            f"{r.missed_opportunity_rate:>8.2f} "
            f"{r.inconclusive_rate:>8.2f} "
            f"{r.mean_regret:>12.0f}"
        )


if __name__ == "__main__":
    main()
