# Research protocol

## Project

Causal Learning Analytics

## Research questions

1. What causal estimand is being targeted, and what assumptions would identify it?
2. How different is the unadjusted outcome contrast from the inverse-probability-weighted estimate?
3. Do treated and control observations occupy sufficient empirical common support?
4. Does weighting improve measured pre-treatment covariate balance?
5. How stable are estimates to propensity clipping and alternative propensity-model specifications?
6. How much precision is lost through unstable weights or low effective sample size?

## Current baseline

The current implementation supports an inspectable ATE workflow with:

- binary treatment validation
- finite numeric outcome and propensity validation
- a dependency-free logistic propensity baseline for continuous pre-treatment covariates
- externally supplied propensity scores when a stronger model is estimated elsewhere
- Horvitz-Thompson ATE
- normalized Hájek ATE
- unadjusted treated-minus-control mean difference
- explicit propensity clipping with clipping counts
- treated/control empirical common-support ranges
- ATE inverse-probability weights
- weight magnitude diagnostics
- Kish effective sample size
- covariate means and standardized mean differences before weighting
- weighted covariate means and standardized mean differences after weighting
- percentile-bootstrap uncertainty conditional on supplied propensity scores
- clipping sensitivity
- explicit causal review flags

## Estimand

The implemented weighting scheme targets the **average treatment effect (ATE)**.

The repository does not currently implement ATT, ATC, overlap weights, matching estimands, instrumental-variable estimands, mediation effects, or longitudinal treatment regimes.

Define the estimand before inspecting outcomes.

## Identification assumptions

A numerical IPW estimate is not automatically a causal estimate.

A causal interpretation requires assumptions appropriate to the study, including:

- consistency
- conditional exchangeability given measured pre-treatment covariates
- positivity
- no interference
- correct treatment and outcome measurement

The code cannot prove these assumptions from the observed dataset.

For that reason the integrated analysis always includes:

`causal_assumptions_unverified`

as a review flag.

## Propensity model

`fit_propensity_logistic()` implements a small deterministic logistic model on named continuous pre-treatment covariates.

The function:

- validates the treatment and covariates
- standardizes each covariate
- fits an intercept and slopes by iterative Newton updates
- supports optional L2 regularization
- reports convergence, iterations, coefficients, means, and scales
- returns treatment-probability estimates

This baseline exists for transparency and reproducibility. Production causal work should benchmark or replace it with mature statistical software when model complexity, interactions, nonlinearity, missingness, clustering, or regularization require it.

A high predictive score is not the goal of propensity modeling. The practical diagnostic target is whether the chosen design and weights produce credible balance without unacceptable instability.

## Positivity and common support

Scores at exactly 0 or 1 make ordinary ATE inverse-probability weights undefined.

The default estimator rejects those scores.

Clipping is allowed only when the analyst supplies a threshold explicitly. The output records:

- clipping threshold
- number of scores changed
- original score range
- score range used in estimation

Empirical common support is reported as the intersection of the observed treated and control propensity-score ranges, along with the fraction of each group inside that interval.

This is a simple diagnostic, not proof of positivity.

## Weight diagnostics

The repository reports:

- minimum weight
- maximum weight
- mean weight
- overall effective sample size
- treated effective sample size
- control effective sample size

Large weights or sharp effective-sample-size loss are reasons to review the design and propensity specification rather than simply trusting the adjusted estimate.

## Covariate balance

For each named pre-treatment covariate the baseline reports:

- treated mean
- control mean
- standardized mean difference before weighting
- weighted treated mean
- weighted control mean
- weighted standardized mean difference after weighting

Weighted means and variances follow the usual inverse-probability-weighting formulas.

The default absolute SMD review threshold is 0.10. It is treated as a practical review signal rather than a universal pass/fail standard.

If the standardized scale cannot be estimated, the SMD is returned as not estimable instead of zero.

## Uncertainty

The current confidence interval is a seeded percentile bootstrap for the normalized Hájek estimate.

The bootstrap resamples rows and treats the supplied propensity scores as fixed.

Therefore it does **not** propagate uncertainty from propensity-model estimation. Real studies may require methods that account for the full estimation procedure, clustering, repeated observations, or other design structure.

## Sensitivity

`clipping_sensitivity()` compares effect estimates, maximum weight, and effective sample size across several propensity-clipping thresholds.

This is only one form of sensitivity analysis.

The current repository does not yet quantify sensitivity to an unmeasured confounder and does not make an E-value, Rosenbaum bound, or bias-function claim.

## Validation

A credible empirical analysis should:

1. define treatment, outcome, timing, population, and estimand before outcome analysis
2. justify the pre-treatment adjustment set
3. document propensity-model specification
4. inspect propensity distributions by treatment group
5. inspect weight distributions
6. report effective sample size
7. compare measured covariate balance before and after weighting
8. investigate residual imbalance
9. compare alternative reasonable propensity specifications
10. report uncertainty
11. run sensitivity analyses appropriate to the design
12. distinguish identification assumptions from diagnostics that can be checked empirically

## Threats to validity

Major threats include unmeasured confounding, adjustment for post-treatment variables, selection bias, treatment misclassification, outcome measurement error, poor overlap, near-positivity violations, extreme weights, misspecified propensity models, interference, informative missingness, attrition, and selective reporting.

A polished weighted estimate does not repair a weak causal design.
