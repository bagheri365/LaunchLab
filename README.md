# LaunchLab

LaunchLab studies when an online experiment provides enough evidence to replace an incumbent ML model.

Implemented milestones:

- treatment-effect inference for two independent user-level conversion rates;
- confidence intervals;
- statistical power, MDE, and required sample size;
- user-level experiment configuration and simulation;
- explicit separation of assignment and exposure;
- A/A validation;
- sample-ratio mismatch (SRM) diagnostics;
- annual deployment value and serving-cost economics;
- break-even lift and economically acceptable degradation;
- product quality floors;
- raw economic regret and asymmetric risk-weighted loss.

The canonical v1 experiment randomizes at the user level and analyzes a user-level conversion outcome.
Later milestones add launch policies, repeated-user realism, Monte Carlo evaluation, and decision-power analysis.
