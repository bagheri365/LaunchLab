import pytest

from launchlab.economics import EconomicsConfig
from launchlab.evaluation import BenchmarkScenario, run_monte_carlo_benchmark


def economics(candidate_cost: float) -> EconomicsConfig:
    return EconomicsConfig(
        annual_traffic=100_000_000,
        value_per_conversion=20.0,
        incumbent_cost_per_request=0.0010,
        candidate_cost_per_request=candidate_cost,
        product_allowed_loss=0.0001,
        inconclusive_cost=1_000.0,
    )


def test_benchmark_returns_all_policies_for_each_scenario():
    scenarios = [
        BenchmarkScenario(
            name="easy_win",
            n_users=20_000,
            baseline_conversion=0.05,
            treatment_effect=0.01,
            economics=economics(0.0011),
        ),
        BenchmarkScenario(
            name="cheap_slight_loss",
            n_users=20_000,
            baseline_conversion=0.05,
            treatment_effect=-0.00002,
            economics=economics(0.0),
        ),
    ]

    results = run_monte_carlo_benchmark(scenarios, seeds_per_scenario=10)

    assert len(results) == 9
    assert {r.scenario for r in results} == {"easy_win", "cheap_slight_loss"}

    easy_policies = {r.policy for r in results if r.scenario == "easy_win"}
    cheap_policies = {r.policy for r in results if r.scenario == "cheap_slight_loss"}

    assert "non_inferiority_savings" not in easy_policies
    assert "non_inferiority_savings" in cheap_policies


def test_rates_are_valid_probabilities():
    scenario = BenchmarkScenario(
        name="null",
        n_users=5_000,
        baseline_conversion=0.05,
        treatment_effect=0.0,
        economics=economics(0.0010),
    )

    results = run_monte_carlo_benchmark([scenario], seeds_per_scenario=20)

    for result in results:
        assert 0.0 <= result.correct_decision_rate <= 1.0
        assert 0.0 <= result.harmful_launch_rate <= 1.0
        assert 0.0 <= result.missed_opportunity_rate <= 1.0
        assert 0.0 <= result.inconclusive_rate <= 1.0
        assert result.mean_regret >= 0.0


def test_easy_large_win_is_usually_shipped_by_superiority_policy():
    scenario = BenchmarkScenario(
        name="easy_win",
        n_users=50_000,
        baseline_conversion=0.05,
        treatment_effect=0.01,
        economics=economics(0.0011),
    )

    results = run_monte_carlo_benchmark([scenario], seeds_per_scenario=30)
    superiority = next(r for r in results if r.policy == "statistical_superiority")

    assert superiority.correct_decision_rate > 0.8


def test_invalid_seed_count_raises():
    scenario = BenchmarkScenario(
        name="x",
        n_users=100,
        baseline_conversion=0.05,
        treatment_effect=0.0,
        economics=economics(0.001),
    )
    with pytest.raises(ValueError, match="seeds_per_scenario"):
        run_monte_carlo_benchmark([scenario], seeds_per_scenario=0)


def test_non_inferiority_is_not_scored_when_candidate_is_not_cheaper():
    scenario = BenchmarkScenario(
        name="more_expensive",
        n_users=5_000,
        baseline_conversion=0.05,
        treatment_effect=0.001,
        economics=economics(0.0012),
    )

    results = run_monte_carlo_benchmark([scenario], seeds_per_scenario=5)

    assert all(r.policy != "non_inferiority_savings" for r in results)
