# LaunchLab

LaunchLab studies when an online experiment provides enough evidence to replace an incumbent ML model.

Implemented milestones:

- treatment-effect inference for two independent user-level conversion rates;
- confidence intervals;
- statistical power, MDE, and required sample size;
- user-level experiment configuration and simulation;
- explicit separation of assignment and exposure;
- A/A validation and sample-ratio mismatch diagnostics;
- deployment economics, break-even lift, product quality floors, and regret;
- five three-way launch policies returning `SHIP`, `REJECT`, or `INCONCLUSIVE`.

Canonical v1 launch policies:

1. statistical superiority;
2. practical significance;
3. economic break-even;
4. non-inferiority plus serving-cost savings;
5. risk-adjusted expected value.

Later milestones add repeated-user realism, Monte Carlo evaluation, and statistical-power vs decision-power analysis.
