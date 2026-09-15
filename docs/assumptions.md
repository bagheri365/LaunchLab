# Assumptions

LaunchLab v1 intentionally simplifies several production concerns so individual failure modes are visible.

- Users are independent across randomization units.
- Primary inference is fixed-horizon.
- Serving cost is treated as known metadata.
- The primary metric is binary user-level conversion.
- Network interference and spillovers are excluded.
- CUPED, sequential testing, multiple uncertain guardrails, bandits, and Bayesian decision rules are future work.
- Economic value per conversion may be misspecified in robustness experiments.
