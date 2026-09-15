# LaunchLab confirmatory preregistration

## Primary question

How does experiment size affect the probability of making the economically correct model-launch decision, and when do decision-aware launch rules outperform conventional statistical significance?

## Experimental unit

- Randomization unit: user
- Analysis unit: user
- Assignment is sticky at the user level.
- Exposure is analyzed separately from assignment.

## Primary metric

7-day user conversion rate: the fraction of exposed users who convert at least once within 7 days of first exposure.

## Fixed-horizon analysis

The confirmatory benchmark uses fixed-horizon inference. Naive repeated p-value peeking is out of scope for v1.

## Validity gates

Before launch interpretation:

1. offline eligibility checks must pass;
2. A/A validation must have been completed for the system;
3. sample-ratio mismatch is checked;
4. exposure counts must exceed the predeclared minimum;
5. the analysis unit must match the randomization unit.

## Decisions

Applicable policies return `SHIP`, `REJECT`, or `INCONCLUSIVE`. The production-style workflow only returns a consensus `SHIP` or `REJECT` when all applicable policies agree; disagreement remains `INCONCLUSIVE`.
