# Limitations and Scope

LaunchLab is a controlled decision-science benchmark for model-launch experimentation. Its purpose is to make statistical and economic assumptions explicit, not to claim that one launch policy is universally optimal.

## Simulation-first evidence

The primary benchmark is synthetic. This is useful because the true treatment effect and true economic value are known, allowing direct measurement of decision correctness and regret. The trade-off is that external validity depends on how well the simulated scenarios approximate a real product setting.

## Simplified outcome model

The canonical outcome is a binary user-level conversion measured over seven days. Real ML products may optimize continuous, count, survival, ranking, latency, safety, or multi-objective metrics. Those require different estimators and may change the geometry of the launch decision.

## Economic model

Economic value is represented by traffic, conversion value, and incremental request cost. This deliberately transparent formulation omits many possible effects, including retention, cannibalization, long-run feedback loops, support costs, platform constraints, and strategic option value.

## Misspecification study

The economic robustness experiments vary assumed conversion value and incremental cost around configured truth. They do not exhaust the space of possible business-model error. Correlated or structural misspecification could behave differently.

## Delay cost

`INCONCLUSIVE` is assigned a configurable temporary cost. That representation is more realistic than treating indecision as permanent rejection, but it is still a simplification. In practice, delay cost may be nonlinear, time-varying, or state-dependent.

## Scenario-grid interpretation

Minimum-regret policy counts describe the finite operating grid that LaunchLab evaluates. They should not be interpreted as population-level frequencies or as evidence that one rule will dominate in another organization.

The joint decision surface also conditions on the simulated true effect when reporting which policy has minimum regret. This is diagnostically useful, but an operator does not know the true effect at decision time. A fully ex-ante policy comparison would integrate regret over a prior or scenario distribution before choosing the policy.

## Experiment assumptions

The canonical workflow assumes user-level randomization and user-level analysis. Repeated-user simulations demonstrate why request-level pseudo-replication is unsafe, but the framework does not yet cover interference, network effects, switchback designs, clustered assignment, sequential testing, or adaptive experimentation.

## External validation

External observational or uplift datasets can provide useful secondary validation, but they do not replace the controlled synthetic benchmark for evaluating decision correctness because true counterfactual economic value is generally unavailable.

## Interpretation

LaunchLab is best viewed as a reproducible framework for reasoning about launch decisions under uncertainty. The outputs are scenario-dependent and should be used to surface assumptions and trade-offs rather than as universal deployment thresholds.
