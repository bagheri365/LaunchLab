# LaunchLab

LaunchLab studies when an online experiment provides enough evidence to replace an incumbent ML model.

Implemented milestones:

- treatment-effect inference, confidence intervals, power, MDE, and sample size;
- user-level simulation with assignment/exposure separation;
- A/A validation and SRM diagnostics;
- deployment economics, break-even lift, product quality floors, and regret;
- five `SHIP` / `REJECT` / `INCONCLUSIVE` launch policies;
- Monte Carlo benchmarking of decision quality;
- repeated-user realism and a naive request-level failure case;
- statistical-power vs decision-power analysis;
- economic-assumption misspecification;
- reproducible CSV/SVG reporting;
- a production-style end-to-end launch workflow with predeclared gates;
- decision-readiness traffic planning;
- sensitivity analysis over traffic, business value, serving cost, and practical thresholds.

Run:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
python scripts/run_decision_power.py
python scripts/run_reporting.py
python scripts/run_workflow.py
python scripts/run_traffic_planning.py
python scripts/run_sensitivity.py
```

The sensitivity runner writes:

```text
results/tables/sensitivity_grid.csv
results/figures/economic_break_even_sensitivity.svg
```

The grid makes policy flips explicit as sample size and business assumptions change.

<!-- LAUNCHLAB_PORTFOLIO_START -->

## LaunchLab in 30 seconds

**LaunchLab is a simulation framework for deciding whether an ML model should ship when statistical significance, business value, and launch risk disagree.**

It compares conventional significance testing with decision-aware launch policies and measures **decision power**: the probability of making the economically correct launch decision.

### What this project shows

- **No single launch rule dominates.** The minimum-regret policy changes across experiment size, economic assumptions, and delay cost.
- **Economic assumptions matter.** In the tested misspecification grid, mean regret for the economic break-even policy ranges from about **$1,850 to $119,405**.
- **Waiting has a price.** As the cost of an inconclusive decision rises, the minimum-regret probability threshold becomes less conservative.
- **Statistical power is not decision power.** Detecting a nonzero effect and making the economically correct launch decision are different objectives.

### Headline results

| Result | Finding |
| --- | --- |
| Joint decision surface | Statistical superiority wins 144 regions, practical significance 96, economic break-even 48 |
| Delay-cost crossover | Preferred probability threshold first relaxes around a $75,000 inconclusive cost in both tested scenarios |
| Economic misspecification | Economic break-even mean regret ranges from about $1,850 to $119,405 |
| Validation | Full test suite passes in the final portfolio check |

**Why it matters:** a model can be statistically distinguishable from an incumbent without being economically worth shipping, while an economically valuable model can remain statistically inconclusive longer than the business can afford to wait.

These are simulation results under the configured scenarios, not universal constants.

## Research question

**How does experiment size affect the probability of making the economically correct model-launch decision, and when do decision-aware launch rules outperform conventional statistical significance?**

A secondary question is how robust economically grounded launch rules remain when their business-value assumptions are wrong.

## What LaunchLab evaluates

LaunchLab treats model deployment as a decision problem rather than a significance test. The canonical experiment randomizes and analyzes at the **user** level, uses a **7-day user conversion rate** as the primary outcome, and separates assignment from exposure. Synthetic experiments are the primary benchmark so that true treatment effects and true economic value are known.

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
