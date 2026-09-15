from pathlib import Path

from launchlab.decision_power import compare_statistical_and_decision_power
from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario, run_monte_carlo_benchmark
from launchlab.reporting import (
    write_policy_aggregates_csv,
    write_power_comparison_svg,
    write_power_comparisons_csv,
    write_regret_svg,
)


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


def scenarios() -> list[BenchmarkScenario]:
    return [
        BenchmarkScenario(
            name="easy_large_win",
            n_users=40_000,
            baseline_conversion=0.05,
            treatment_effect=0.01,
            economics=econ(0.0012),
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


def main() -> None:
    out_tables = Path("results/tables")
    out_figures = Path("results/figures")
    benchmark_scenarios = scenarios()

    policy_rows = run_monte_carlo_benchmark(
        benchmark_scenarios,
        seeds_per_scenario=100,
    )
    power_rows = compare_statistical_and_decision_power(
        benchmark_scenarios,
        seeds_per_scenario=100,
    )

    outputs = [
        write_policy_aggregates_csv(
            policy_rows,
            out_tables / "policy_benchmark.csv",
        ),
        write_power_comparisons_csv(
            power_rows,
            out_tables / "decision_power.csv",
        ),
        write_power_comparison_svg(
            power_rows,
            out_figures / "decision_power_vs_statistical_power.svg",
        ),
        write_regret_svg(
            policy_rows,
            out_figures / "mean_regret_by_policy.svg",
        ),
    ]

    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
