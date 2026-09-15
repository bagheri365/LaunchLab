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
- a small Monte Carlo benchmark for decision quality and regret;
- repeated-user simulation with sticky assignment;
- a failure-mode comparison between correct user-level analysis and naive request-level analysis.

Run the current demos with:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
```

The repeated-user demo illustrates why the analysis unit must match the randomization unit: treating correlated requests as independent can produce narrower confidence intervals and a different estimand than user-level conversion.
