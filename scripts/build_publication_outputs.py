from launchlab.publication_figures import (
    write_delay_crossover_svg,
    write_misspecification_heatmap_svg,
    write_policy_region_svg,
    write_sample_size_policy_svg,
)
from launchlab.publication_narrative import (
    build_publication_results,
    write_publication_results,
)


def main() -> None:
    joint = "results/tables/joint_decision_optima.csv"
    delay = "results/tables/delay_cost_optima.csv"
    misspec = "results/tables/economic_misspecification.csv"

    outputs = [
        write_policy_region_svg(
            joint,
            "results/figures/publication_policy_regions.svg",
        ),
        write_delay_crossover_svg(
            delay,
            "results/figures/publication_delay_crossover.svg",
        ),
        write_misspecification_heatmap_svg(
            misspec,
            "results/figures/publication_misspecification_regret.svg",
        ),
        write_sample_size_policy_svg(
            joint,
            "results/figures/publication_sample_size_policy.svg",
        ),
    ]

    narrative = build_publication_results(
        joint_optima_csv=joint,
        delay_optima_csv=delay,
        misspecification_csv=misspec,
    )
    outputs.append(
        write_publication_results(
            narrative,
            "results/reports/publication_results.md",
        )
    )

    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
