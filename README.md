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
- decision-readiness traffic planning for inconclusive experiments.

Run:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
python scripts/run_decision_power.py
python scripts/run_reporting.py
python scripts/run_workflow.py
python scripts/run_traffic_planning.py
```

The traffic planner estimates required and additional per-arm sample sizes for the observed effect, the practical-significance threshold, and any positive economic break-even threshold. The largest requirement is reported as the binding decision-readiness constraint.
