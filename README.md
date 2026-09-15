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
- a production-style end-to-end launch workflow with predeclared gates.

Run:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
python scripts/run_decision_power.py
python scripts/run_reporting.py
python scripts/run_workflow.py
```

The production workflow applies offline eligibility, SRM, exposure-count validation, user-level inference, MDE context, economics, and all applicable launch policies. A final `SHIP` or `REJECT` is returned only when applicable policies agree; otherwise the result remains `INCONCLUSIVE`.

Confirmatory assumptions and example configuration live in:

```text
configs/confirmatory.yaml
configs/economics.yaml
docs/preregistration.md
docs/assumptions.md
```
