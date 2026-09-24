# Data documentation

## Included data

`sample.csv` contains 12 **synthetic observational records** created only to exercise the causal-analysis workflow.

The values are not learner study results.

## Current schema

- `learner`: synthetic row identifier
- `treatment`: binary observed treatment indicator, 1 treated and 0 control
- `outcome`: synthetic continuous post-intervention outcome
- `propensity`: supplied probability of observed treatment conditional on a hypothetical set of pre-treatment covariates
- `baseline_score`: synthetic pre-treatment baseline measure
- `prior_engagement`: synthetic pre-treatment engagement measure

Only pre-treatment covariates belong in the adjustment set used to estimate the propensity score or assess balance.

## Propensity-score provenance

The current integrated baseline accepts propensity scores as inputs.

For a real study, document:

- which pre-treatment variables were used
- why each variable was included
- the model or design used to estimate treatment probabilities
- model specification and transformations
- whether scores were estimated on the same analysis sample
- any trimming or clipping rule
- the estimand targeted by the weights

Do not include post-treatment variables in the propensity model simply because they improve prediction.

## Positivity

Propensity values at exactly 0 or 1 make ordinary ATE inverse-probability weights undefined.

The software therefore rejects endpoint scores unless the analyst **explicitly** supplies a clipping threshold. Any clipping is counted and surfaced in the output.

Clipping is a sensitivity/specification choice, not an automatic repair for a positivity problem.

## Common support

The repository reports empirical common support as the intersection of the observed treated and control propensity-score ranges.

It also reports the fraction of each treatment group inside that interval.

This is a simple diagnostic. It does not prove the positivity assumption and does not replace inspection of the full propensity and weight distributions.

## Covariate balance

Balance diagnostics should use variables measured before treatment.

The current implementation reports treated/control means and standardized mean differences before and after weighting.

An SMD that cannot be standardized because the within-group scale is not estimable is returned as `None`; it is not converted to zero.

## Missing data

The current baseline does not impute missing treatment, outcome, propensity, or covariate values.

Production analyses need a pre-specified missing-data strategy appropriate to the design and estimand.

## Do not commit

Do not commit personally identifiable learner records, protected educational data, private intervention logs, disability or health information, raw submissions, or licensed datasets that prohibit redistribution.

## Dataset card requirement

For empirical work, document the population, treatment definition, outcome definition and timing, pre-treatment covariates, propensity-model provenance, exclusions, missingness, overlap, weighting choices, attrition, protocol deviations, privacy protections, known biases, and permitted uses.
