# LaunchLab

When is A/B-test evidence strong enough to justify replacing an incumbent ML model?

LaunchLab is a controlled simulation study of statistical evidence, deployment economics, launch risk, and decision regret.

> Separate detectability from decision value, then evaluate the launch rule by the decision it produces.

<!-- LAUNCHLAB_PORTFOLIO_START -->

## At a Glance

- **Research question:** when does A/B-test evidence support the economically correct model-launch decision?
- **Canonical design:** user-randomized, user-analyzed experiment with a 7-day user conversion outcome.
- **Core distinction:** statistical power asks whether an effect is detectable; **decision power** asks whether the launch decision is economically correct.
- **Policies compared:** statistical superiority, practical significance, economic break-even, non-inferiority plus savings, expected value, and probability-based risk adjustment.
- **Main joint-surface result:** statistical superiority is minimum-regret in 144 tested regions, practical significance in 96, and economic break-even in 48.
- **Robustness result:** economic break-even mean regret ranges from about **$1,850 to $119,405** across the tested economic-misspecification grid.
- **Decision-timing result:** the preferred probability threshold first becomes less conservative around a **$75,000** inconclusive cost in both tested scenarios.

These are simulation results under the configured scenarios, not universal constants.

## Why This Project Exists

Online model launches often collapse into a single question:

> Is the A/B test statistically significant?

That is not the same as asking whether the candidate is worth shipping.

A candidate can be statistically distinguishable from an incumbent but economically unattractive after serving cost. A candidate can also be economically valuable while remaining statistically inconclusive longer than the business can afford to wait.

LaunchLab therefore separates three questions:

1. **Can the experiment detect the effect?**
2. **Is the effect large enough to matter operationally or economically?**
3. **Given uncertainty and delay cost, what launch action minimizes regret?**

The project evaluates launch rules by the decisions they produce, not only by whether they reject a null hypothesis.

## Experimental Design

The primary benchmark is synthetic so that the true treatment effect and the true economic value are known.

| Design choice | Canonical setting |
| --- | --- |
| Randomization unit | User |
| Analysis unit | User |
| Primary metric | 7-day user conversion rate |
| Assignment vs exposure | Modeled separately |
| Treatment effect | Absolute conversion-rate difference |
| Decision outcomes | `SHIP`, `REJECT`, `INCONCLUSIVE` |
| Primary evidence | Monte Carlo simulation |
| Economic objective | Minimize decision regret |

The framework also includes repeated-user simulations to show how request-level pseudo-replication can understate uncertainty when the true experimental unit is the user.

## Key Findings

### Statistical Power Is Not Decision Power

Statistical power is the probability of rejecting the null under a specified alternative.

Decision power is the probability of making the economically correct launch decision.

Those quantities can diverge because a detectable effect can still fall below a practical or economic launch threshold, while an economically attractive effect may remain uncertain at the available sample size.

### No Single Launch Rule Dominates the Joint Decision Surface

Across the tested joint surface of sample size, economic assumptions, delay cost, and true effect:

| Minimum-regret policy | Operating points |
| --- | ---: |
| Statistical superiority | 144 |
| Practical significance | 96 |
| Economic break-even | 48 |

Under the tested true effect of `0.0008`, practical significance and economic break-even win different regions. Under the tested true effect of `0.0010`, statistical superiority wins the evaluated regions.

The result is diagnostic rather than a universal policy ranking because the simulation conditions on known truth.

### Economic Assumptions Can Dominate Launch Regret

The misspecification study perturbs assumed conversion value and assumed incremental serving cost while keeping the experiment data-generating process fixed.

For the economic break-even policy, mean regret across that grid ranges from about:

- **$1,850** at the low end;
- **$119,405** at the high end.

The same experiment can therefore support very different economic decisions when the business-value model is wrong.

### Delay Cost Changes the Rational Level of Conservatism

The probability-based launch rule ships only when the probability of positive annual value clears a configured threshold.

At low delay cost, the minimum-regret threshold is `0.990` in both tested scenarios. At an inconclusive cost of about `$75,000`, the preferred threshold first relaxes:

- true effect `0.0008`: `0.990 -> 0.975`;
- true effect `0.0010`: `0.990 -> 0.900`.

The implication is not that one probability threshold is universally correct. The cost of waiting is part of the launch decision.

### Request-Level Pseudo-Replication Creates False Confidence

LaunchLab simulates repeated requests from the same users and compares the correct user-level analysis with a naive request-level analysis.

The purpose is to make a common experiment-design failure visible: treating correlated requests as independent observations can make uncertainty appear much smaller than it really is.

## Launch Decision Framework

| Policy | Decision idea |
| --- | --- |
| Statistical superiority | Ship when the candidate is statistically superior |
| Practical significance | Require improvement beyond a product-relevant threshold |
| Economic break-even | Require estimated value to exceed incremental serving cost |
| Non-inferiority + savings | Permit limited quality loss when savings justify it |
| Expected-value rule | Compare estimated annual value against the launch boundary |
| Probability risk adjustment | Require sufficient probability that annual value is positive |

A production-style workflow also adds an offline eligibility gate, exposed-user SRM checks, minimum exposed-user requirements, user-level inference, MDE calculation, and a conservative consensus decision.

## Research Evolution

The project develops the launch problem in layers:

> inference -> simulation -> validation -> economics -> policies -> decision power -> robustness -> delay cost -> joint decision surface -> reporting

Each layer isolates a different reason that “statistically significant” may fail to answer “should we ship?”

## Reproducibility

Run the full test suite:

```bash
pytest
```

Run the main research experiments:

```bash
python scripts/run_aa.py
python scripts/run_workflow.py
python scripts/run_sensitivity.py
python scripts/run_robustness.py
python scripts/run_risk_adjustment.py
python scripts/run_delay_sensitivity.py
python scripts/run_joint_surface.py
```

Build the research and publication outputs:

```bash
python scripts/build_research_report.py
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

For a lightweight portfolio validation:

```bash
python scripts/final_check.py
```

## Repository Structure

```text
src/launchlab/      statistical, economic, simulation, policy, and reporting code
scripts/            reproducible experiment and reporting entry points
tests/              unit and regression tests
configs/            confirmatory workflow and economics configuration
docs/               preregistration, assumptions, limitations, and reproducibility notes
results/            generated tables, figures, and reports (gitignored)
```

## Experimental Discipline

LaunchLab is built around a few explicit rules:

- randomize and analyze at the user level for the canonical experiment;
- separate assignment from exposure;
- run A/A checks and exposed-user SRM diagnostics;
- distinguish statistical detectability from product and economic thresholds;
- evaluate decisions against known simulated truth when benchmarking;
- keep true economics separate from assumed policy economics in misspecification studies;
- model `INCONCLUSIVE` as a temporary delay/continuation cost rather than permanent rejection;
- preserve reproducible tables, figures, and reports from deterministic experiment runners.

## Limitations

The current benchmark is deliberately controlled and synthetic.

- Outcomes are binary conversions rather than richer metric families.
- Traffic and treatment effects are simplified and mostly stationary.
- Business value is represented through conversion value and request cost.
- Policy comparisons cover a finite scenario grid.
- Minimum-regret policy counts should not be generalized outside that grid.
- The joint-surface optimum is diagnostic because it conditions on known simulated truth.
- The current framework does not yet model interference, clustered assignment, switchback designs, sequential testing, or adaptive experimentation.
- External-data validation is secondary rather than the primary source of causal identification.

See `docs/limitations.md` for additional detail.

## What the Experiments Suggest

The current evidence supports a decision-aware launch process:

- use statistical inference to quantify uncertainty;
- use product and economic thresholds to define what matters;
- treat serving cost and business value as part of the decision boundary;
- account for the cost of waiting when choosing how conservative to be;
- analyze at the unit that was actually randomized;
- evaluate launch policies by decision quality and regret, not significance alone.

A working design hypothesis from LaunchLab is:

> Ship rules should be calibrated to the economics and timing of the decision, not chosen from statistical significance alone.

## Future Research

Natural extensions include:

- ex-ante policy selection that integrates regret over a distribution of plausible true effects;
- richer outcome families beyond binary conversion;
- sequential and adaptive experimentation;
- clustered, networked, or switchback designs;
- stronger external-data validation;
- broader economic models including retention, long-run feedback, and strategic option value.

<!-- LAUNCHLAB_PORTFOLIO_END -->
