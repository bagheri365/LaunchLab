# LaunchLab

LaunchLab studies when an online experiment provides enough evidence to replace an incumbent ML model.

Implemented milestones:

- treatment-effect inference for two independent user-level conversion rates;
- confidence intervals;
- statistical power, MDE, and required sample size;
- user-level experiment configuration and simulation;
- assignment/exposure separation;
- A/A validation and SRM diagnostics;
- deployment economics, break-even lift, product quality floors, and regret;
- five `SHIP` / `REJECT` / `INCONCLUSIVE` launch policies;
- a small Monte Carlo benchmark for comparing decision quality and regret.

The small benchmark reports:

- correct decision rate;
- harmful launch rate;
- missed opportunity rate;
- inconclusive rate;
- mean economic regret.

Run it with:

```bash
python scripts/run_small_benchmark.py
```

Later milestones add repeated-user realism, broader benchmark regimes, and statistical-power vs decision-power analysis.
