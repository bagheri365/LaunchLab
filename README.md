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
- direct comparison of statistical power and decision power;
- economic-assumption misspecification;
- reproducible CSV tables and dependency-light SVG figures.

Run the current demos with:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
python scripts/run_decision_power.py
python scripts/run_reporting.py
```

`run_reporting.py` writes reproducible artifacts to:

```text
results/
├── figures/
│   ├── decision_power_vs_statistical_power.svg
│   └── mean_regret_by_policy.svg
└── tables/
    ├── decision_power.csv
    └── policy_benchmark.csv
```

The reporting layer uses only the Python standard library for CSV and SVG generation, so it does not add a plotting dependency.
