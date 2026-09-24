# Research protocol

## Project

Causal Learning Analytics

## Questions

1. Which observed learning behaviors are associated with outcomes after adjustment?
2. How sensitive are estimates to propensity overlap and confounding assumptions?
3. Can intervention decisions be separated from purely predictive correlations?

## Baseline methods

- inverse probability weighting
- average treatment effect estimation
- propensity overlap checks
- standardized mean differences
- weight clipping

## Evidence to collect

Start from the current transparent baseline and record every transformation needed to produce an inverse probability weighted average treatment effect plus overlap and balance diagnostics. Keep a clear boundary between synthetic demonstration data and any future empirical dataset.

## Validation

Pre register the treatment, outcome, covariates, estimand, and adjustment strategy. Report overlap, effective sample size, weight distribution, covariate balance, and sensitivity to clipping or model specification.

## What counts as a useful result

A serious version should estimate propensity scores from pre treatment covariates, define the causal estimand before analysis, examine weight instability, and run sensitivity analyses for unmeasured confounding.

## Threats to validity

Unmeasured confounding, poor overlap, post treatment adjustment, unstable weights, and incorrect propensity models can invalidate the estimate.
