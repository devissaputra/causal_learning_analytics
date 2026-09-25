# Early Assessment Submission and Course Outcome in OULAD: A Transparent IPW Study

## Abstract

Learning-analytics studies often report associations between early engagement and course success without making the temporal and identification assumptions explicit. This study uses a single Open University Learning Analytics Dataset module-presentation cohort to estimate an ATE-style inverse-probability-weighted contrast between submitting at least one assessment by day 30 and a favorable final result. The design freezes pre-treatment covariates, reports overlap, weight and balance diagnostics, compares raw and weighted contrasts, and retains explicit non-claims about causal identification.

## Research question

Within one OULAD module-presentation cohort, what adjusted outcome contrast is associated with at least one assessment submission by day 30 after weighting on the measured pre-treatment covariates?

## Data

The runner obtains OULAD through UCI dataset 349 (DOI 10.24432/C5KK69), records the archive SHA-256 and uses `studentInfo.csv`, `studentRegistration.csv`, `assessments.csv`, and `studentAssessment.csv`.

## Design

The exposure is defined before outcome measurement. The favorable-outcome indicator is Pass or Distinction versus Fail or Withdrawn. The propensity model uses studied credits, previous attempts, registration timing, age band, prior education, deprivation-band midpoint, disability indicator and gender indicator. Assessment scores and later behavior are excluded.

## Analysis

A standardized logistic model estimates propensity scores. The study reports empirical common support, inverse-probability weights, effective sample sizes, covariate standardized mean differences before and after weighting, raw mean difference, Horvitz-Thompson and Hájek estimates, bootstrap uncertainty, and analysis flags.

## Results

Numerical evidence is generated into `results/oulad_metrics.json`, `results/summary.md`, and `paper/results.md`. The manuscript does not hand-enter a favorable result.

## Limitations

The study remains vulnerable to unmeasured confounding, selection, missing-data bias, propensity misspecification and cohort-specific effects. The adjusted contrast should be described as observational unless the required causal assumptions can be justified independently.
