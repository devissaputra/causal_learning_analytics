# Ethics, Validity, and Misuse Risks

## Intended use

This repository is a reproducible observational study of early non-banked assessment submission and later course outcome in an OULAD day-30 landmark population.

It is intended for causal-methodology inspection and AI in Education research, not for operational learner scoring.

## Main risk: causal overclaiming

Inverse-probability weighting can produce a precise-looking contrast while important confounders remain unmeasured.

The repository therefore distinguishes:
- the observed weighted contrast;
- measured overlap and balance;
- sampling/model uncertainty;
- assumptions required for causal interpretation;
- assumptions that remain unverified.

## Landmark-selection risk

The study conditions on remaining registered through day 30. That fixes the prior timing problem but changes the target population.

Learners who withdraw earlier are outside the landmark estimand. The result must not be generalized back to all original registrations without a separate argument.

## Positivity and support

The runner:
- reports propensity overlap;
- flags extreme ATE weights;
- removes categorical baseline levels with no observed exposed/unexposed comparison before weighting;
- reports those exclusions;
- provides common-support and overlap-weighted sensitivity analyses.

These operations change the represented population and are recorded explicitly. They are not chosen based on whether the outcome estimate becomes more favorable.

## Sensitive baseline variables

Gender, disability, deprivation band and region appear only as aggregate baseline adjustment variables.

Their use here does not justify:
- individual profiling;
- ranking;
- access restriction;
- automated support allocation;
- claims that subgroup differences are causal.

## Missing-data risk

The primary study uses complete cases for the frozen adjustment set. Missing deprivation information is therefore a source of possible selection bias.

The generated evidence reports missing counts and complete-case exclusions rather than treating them as harmless.

## Educational interpretation

Early submission can reflect:
- preparation;
- time availability;
- employment constraints;
- accessibility;
- course structure;
- prior achievement;
- motivation;
- support.

A positive observational contrast does not show that forcing earlier submission would improve learning.

## Privacy

OULAD is anonymized public research data. Do not attempt re-identification or link its learner identifiers to external identities.

Do not collect additional sensitive data merely to improve propensity prediction.

## Excluded uses

This repository alone must not be used for:
- grading;
- admissions;
- disciplinary action;
- learner ability labeling;
- mandatory intervention;
- teacher or employee sanctions;
- covert experimentation;
- automated subgroup targeting;
- claims that early submission is proven effective.

## Before any real intervention

A real educational intervention would require:
1. a prospectively specified treatment;
2. separate causal or experimental validation;
3. learner and educator oversight;
4. accessibility and fairness review;
5. privacy/data-governance review;
6. monitoring and rollback criteria.
