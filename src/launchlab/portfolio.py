from __future__ import annotations

from pathlib import Path

START = "<!-- LAUNCHLAB_PORTFOLIO_START -->"
END = "<!-- LAUNCHLAB_PORTFOLIO_END -->"

SECTION = r"""
<!-- LAUNCHLAB_PORTFOLIO_START -->

## Research question

**How does experiment size affect the probability of making the economically correct model-launch decision, and when do decision-aware launch rules outperform conventional statistical significance?**

LaunchLab treats model deployment as a decision problem rather than a significance test. The project separates statistical evidence from economic value, models the cost of waiting, and evaluates launch rules by whether they lead to the economically correct action.

A secondary question is how robust economically grounded launch rules remain when their business-value assumptions are wrong.

## What LaunchLab evaluates

The canonical experiment randomizes and analyzes at the **user** level, uses a **7-day user conversion rate** as the primary outcome, and separates assignment from exposure. Synthetic experiments are the primary benchmark so that true treatment effects and true economic value are known.

The framework compares:

- statistical superiority;
- practical significance;
- economic break-even;
- non-inferiority plus cost savings;
- expected-value launch rules;
- probability-based risk adjustment.

The key distinction is:

- **statistical power**: probability of rejecting the null under a specified alternative;
- **decision power**: probability of making the economically correct launch decision.

## Main findings

The reproducible simulation studies show that **no single launch rule is uniformly minimum-regret across all tested operating conditions**.

Across the current joint decision surface:

| Minimum-regret policy | Operating points won |
| --- | ---: |
| Economic break-even | 48 |
| Practical significance | 96 |
| Statistical superiority | 144 |

The operating regime matters. Under a true effect of `0.0008`, economic and practical thresholds dominate different regions; under a true effect of `0.0010`, statistical superiority wins the tested regions.

The cost of indecision also changes the rational level of conservatism. In the probability-based policy study, the preferred launch-confidence threshold begins to fall from `0.990` once the configured inconclusive cost reaches about `$75,000` in both tested economic scenarios.

Economic assumptions can be consequential even when experiment data do not change. Across the tested misspecification grid, mean regret for the economic break-even policy ranges from about `$1,850` to `$119,405`.

These are simulation results under the configured scenarios, not universal constants.

## Reproduce the research outputs

Run the full test suite:

```bash
pytest
```

Generate the core research summary:

```bash
python scripts/build_research_report.py
```

Generate the publication outputs:

```bash
python scripts/build_publication_outputs.py
```

Key generated artifacts include:

```text
results/reports/research_summary.md
results/reports/publication_results.md
results/figures/publication_policy_regions.svg
results/figures/publication_delay_crossover.svg
results/figures/publication_misspecification_regret.svg
results/figures/publication_sample_size_policy.svg
```

Generated analysis outputs live under `results/` and are intentionally ignored by Git.

## End-to-end workflow

LaunchLab includes a production-oriented decision workflow that performs:

1. an offline eligibility gate;
2. exposed-user sample-ratio-mismatch checks;
3. minimum exposed-user checks;
4. user-level treatment-effect inference;
5. minimum-detectable-effect calculation;
6. policy-specific launch decisions;
7. a conservative consensus decision of `SHIP`, `REJECT`, or `INCONCLUSIVE`.

The repository also includes repeated-user simulations to demonstrate how analyzing request-level observations as if they were independent can materially understate uncertainty.

## Project structure

```text
src/launchlab/      statistical, economic, simulation, policy, and reporting code
scripts/            reproducible experiment and reporting entry points
tests/              unit and regression tests
configs/            confirmatory workflow and economics configuration
docs/               preregistration, assumptions, limitations, and reproducibility notes
results/            generated tables, figures, and reports (gitignored)
```

## Why this matters

A model can be statistically distinguishable from an incumbent without being economically worth shipping, and an economically valuable model can remain statistically inconclusive for longer than the business can afford to wait.

LaunchLab makes those trade-offs explicit. It connects experiment design, statistical uncertainty, business value, launch risk, and delay cost in one reproducible framework.

## Limitations

The current benchmark is deliberately controlled and synthetic. The main limitations are:

- binary conversion outcomes rather than richer metric families;
- simplified and mostly stationary traffic and effect assumptions;
- business value represented through configured conversion value and request cost;
- policy comparisons evaluated over a finite scenario grid;
- no claim that the current minimum-regret policy counts generalize outside those scenarios;
- the current joint-surface optimum is diagnostic because it conditions on known simulated truth;
- external-data validation is secondary rather than the primary source of causal identification.

See `docs/limitations.md` for additional detail.

## Reproducibility checklist

A clean validation run should include:

```bash
pytest
python scripts/run_aa.py
python scripts/run_workflow.py
python scripts/run_sensitivity.py
python scripts/run_robustness.py
python scripts/run_risk_adjustment.py
python scripts/run_delay_sensitivity.py
python scripts/run_joint_surface.py
python scripts/build_research_report.py
python scripts/build_publication_outputs.py
```

For a lightweight portfolio check, run:

```bash
python scripts/final_check.py
```

<!-- LAUNCHLAB_PORTFOLIO_END -->
""".strip()


def update_readme(path: str | Path = "README.md") -> Path:
    target = Path(path)
    original = target.read_text(encoding="utf-8") if target.exists() else "# LaunchLab\n"

    if START in original and END in original:
        before = original.split(START, 1)[0].rstrip()
        after = original.split(END, 1)[1].lstrip()
        pieces = [before, SECTION]
        if after:
            pieces.append(after)
        updated = "\n\n".join(piece for piece in pieces if piece)
    else:
        updated = original.rstrip() + "\n\n" + SECTION

    target.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return target
