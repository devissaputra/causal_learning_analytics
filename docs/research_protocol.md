# Empirical Research Protocol

## Causal question
For a fixed OULAD module-presentation, what ATE-style weighted contrast in favorable final result is associated with submitting at least one assessment by day 30?

## Temporal order
Only registration/background variables are used for propensity estimation. Assessment scores, later VLE activity and later outcomes are excluded from the adjustment set.

## Cohort rule
If module/presentation are not supplied, select the largest cohort with at least 30 exposed and 30 unexposed records after complete-case construction of the predefined covariates.

## Propensity model
Logistic regression on standardized numeric encodings of the predefined covariates. The propensity model is a design tool, not a treatment-prediction contest.

## Diagnostics before interpretation
- treated/control propensity ranges;
- empirical common-support fraction;
- maximum/mean weights;
- total and group effective sample size;
- SMDs before and after weighting;
- residual balance flags.

## Effect reporting
Keep separate:
- raw treated-minus-control mean difference;
- Horvitz-Thompson ATE;
- normalized Hájek ATE;
- fixed-propensity percentile-bootstrap interval.

## Identification assumptions
A causal interpretation additionally requires consistency, conditional exchangeability, positivity, no relevant interference and valid treatment/outcome measurement. These cannot be verified by the code.

## Main threats
Unmeasured motivation and prior achievement; selection into early submission; informative withdrawal; measurement/cohort heterogeneity; missing deprivation data; propensity misspecification; overlap failures.
