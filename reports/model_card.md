# Analytic system card

## System

Causal Learning Analytics

## Purpose

A transparent ATE inverse-probability-weighting scaffold for observational learning-intervention analysis.

## Current maturity

Working research prototype.

The bundled example is synthetic and demonstrates the software path only. It does not establish that an educational intervention caused an outcome.

## Inputs

The integrated analysis accepts:

- binary observed treatment
- finite numeric outcome
- propensity scores
- optional named pre-treatment covariates

Propensity scores may be supplied externally or estimated with the included small logistic baseline.

## Propensity baseline

`fit_propensity_logistic()` standardizes continuous pre-treatment covariates and fits a deterministic logistic model.

It reports convergence, iterations, coefficients, means, scales, regularization, and predicted treatment probabilities.

It is intended for demonstrations and transparent benchmarking. Complex production analyses should use mature statistical software appropriate to the design.

## Outputs

`analyze_ipw()` returns:

- target estimand
- sample and group counts
- raw treated-minus-control mean difference
- Horvitz-Thompson ATE
- normalized Hájek ATE
- fixed-propensity bootstrap confidence interval for the Hájek estimate
- original and analysis propensity ranges
- clipping choice and clipping count
- treated/control empirical common support
- fraction of each group in common support
- minimum, maximum, and mean weight
- overall and group effective sample sizes
- covariate balance before weighting
- covariate balance after weighting
- clipping-sensitivity results
- analysis review flags

## Review flags

Current flags can identify:

- causal assumptions remain unverified
- small treatment group
- propensity at 0 or 1
- propensity clipping used
- poor empirical common support
- extreme weights
- low effective sample size
- post-weight balance not estimable
- residual post-weight balance problem

Flags are prompts for analyst review, not automatic validity judgments.

## Identification boundary

The software can check numerical properties of observed data and weights.

It cannot verify:

- absence of unmeasured confounding
- consistency
- no interference
- correctness of treatment definition
- correctness of outcome measurement
- correctness of the causal graph
- whether the adjustment set is sufficient

A causal conclusion remains a study-design judgment.

## Main limitations

The current baseline supports only binary treatment and the ATE.

It does not yet implement doubly robust estimation, matching, overlap weights, longitudinal treatment, cluster-aware inference, missing-data models, heterogeneous effects, or formal unmeasured-confounding sensitivity analysis.

The bootstrap interval conditions on the supplied propensity scores and therefore understates total uncertainty when those scores were themselves estimated.

## Human oversight

Researchers remain responsible for the causal question, temporal ordering, adjustment set, estimand, propensity specification, missing-data strategy, sensitivity analyses, interpretation, and any decision made from the result.
