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
- economic-assumption misspecification through separate true vs assumed economics.

Run the current demos with:

```bash
python scripts/run_small_benchmark.py
python scripts/run_repeated_user_demo.py
python scripts/run_decision_power.py
```

`run_decision_power.py` is the first research-style benchmark: it shows that the probability of rejecting a statistical null can differ materially from the probability of making the economically correct launch decision.
