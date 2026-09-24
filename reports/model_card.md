# Analytic system card

## System

Causal Learning Analytics

## Purpose

Compact causal analysis baseline for inverse probability weighting, overlap checks, and covariate balance diagnostics.

## Current maturity

Working research prototype. The bundled example checks the software path with synthetic inputs. It does not establish validity for real learners, instructors, courses, or workplaces.

## Inputs

See `../data/README.md` for the current synthetic schema and the documentation expected before real data are connected.

## Outputs

The current code produces an inverse probability weighted average treatment effect plus overlap and balance diagnostics. These outputs are research signals and should be interpreted with the educational context that produced them.

## Evidence needed before real use

Pre register the treatment, outcome, covariates, estimand, and adjustment strategy. Report overlap, effective sample size, weight distribution, covariate balance, and sensitivity to clipping or model specification.

## Main limitation

Inverse probability weighting only supports a causal interpretation when the identification assumptions are credible. This repository demonstrates mechanics and diagnostics, not proof that an intervention caused an outcome.

## Human oversight

A person must review any output before it can affect a learner, instructor, applicant, or employee.
