from launchlab.research_report import (
    build_research_summary,
    write_research_summary,
)


def main() -> None:
    summary = build_research_summary("results/tables")
    output = write_research_summary(
        summary,
        "results/reports/research_summary.md",
    )

    print(output)
    print()
    print("minimum-regret policy counts")
    for policy, count in summary.joint_policy_counts:
        print(f"{policy:<35} {count:>4}")

    print()
    print("delay-cost crossovers")
    for row in summary.delay_crossovers:
        cost = (
            "not observed"
            if row.crossover_inconclusive_cost is None
            else f"{row.crossover_inconclusive_cost:,.0f}"
        )
        threshold = (
            "not observed"
            if row.crossover_probability_threshold is None
            else f"{row.crossover_probability_threshold:.3f}"
        )
        print(
            f"effect={row.treatment_effect:.4f} "
            f"crossover_cost={cost} "
            f"threshold={threshold}"
        )


if __name__ == "__main__":
    main()
