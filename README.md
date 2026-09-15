# LaunchLab

LaunchLab studies when an online experiment provides enough evidence to replace an incumbent ML model.

Implemented milestones:

- treatment-effect inference for two independent user-level conversion rates;
- confidence intervals;
- statistical power;
- minimum detectable effect (MDE);
- required sample size;
- user-level experiment configuration;
- deterministic control/treatment assignment;
- explicit separation of assignment and exposure;
- synthetic exposed-user conversion outcomes;
- A/A validation;
- sample-ratio mismatch (SRM) diagnostics.

The canonical v1 experiment randomizes at the user level and analyzes a user-level conversion outcome.
Later milestones add economics, launch policies, repeated-user realism, and decision regret.
