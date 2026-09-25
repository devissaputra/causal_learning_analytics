# Analysis Card — OULAD Day-30 Causal Learning Analytics

## Purpose

Transparent observational comparison of early non-banked assessment submission and later course outcome within a day-30 OULAD landmark cohort.

## Eligibility

A learner must be registered on or before day 30 and must not have unregistered on or before day 30. Withdrawn learners require a recorded unregistration date after the landmark.

## Exposure

At least one non-banked assessment submitted after registration and on or before day 30.

## Outcome

Pass/Distinction versus Fail or withdrawal occurring after the landmark.

## Propensity model

L2 logistic regression using standardized numeric baseline covariates and one-hot categorical baseline covariates.

## Design safeguards

- aligned landmark, eligibility and exposure window;
- transferred banked assessments excluded;
- submissions before registration excluded;
- exactly one module-presentation per analysis;
- post-landmark assessment scores/behavior excluded from adjustment;
- complete-case losses reported;
- overlap, weights, ESS and before/after balance reported;
- full-refit bootstrap used as primary uncertainty interval;
- common-support and propensity-specification sensitivity analyses;
- causal assumptions remain explicitly unverified.

## Intended use

Methodological inspection, AI in Education research, causal-learning-analytics prototyping and reproducibility review.

## Not intended for

Learner ranking, mandatory intervention, grading, admissions, disciplinary action or claims that submitting early will necessarily improve an individual learner's outcome.

## Central limitation

The study remains observational. Motivation, prior achievement, work constraints, access and other causes of both submission timing and course outcome are incompletely measured. Good measured balance does not establish exchangeability.
