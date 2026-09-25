# Empirical Research Protocol

## Research question

Among learners eligible at presentation day 30 in one OULAD module-presentation, what ATE-style adjusted contrast in favorable final course outcome is associated with at least one non-banked assessment submission by day 30?

## Time zero and landmark

The analysis uses **presentation day 30 as the landmark**.

Eligibility, exposure classification and the beginning of outcome follow-up are aligned at that landmark:
- registration must occur on or before day 30;
- learners unregistered on or before day 30 are excluded;
- a learner recorded as Withdrawn must have an observed unregistration date after day 30 to remain eligible;
- exposure uses only non-banked submissions observed after registration and through day 30;
- final course outcome occurs after the landmark for the retained population.

This design prevents the prior implementation from classifying learners using a 30-day exposure window while simultaneously counting withdrawals inside that same window as outcomes.

## Cohort rule

The default run chooses the largest landmark-eligible module-presentation containing at least 30 exposed and 30 unexposed learners.

A requested cohort must specify both module and presentation. Supplying only one is rejected.

## Exposure

Treatment = 1 when the learner submits at least one non-banked assessment:
1. after their recorded registration date; and
2. on or before presentation day 30.

Banked results are transferred from a prior presentation and are excluded from the exposure definition.

## Outcome

1 = Pass or Distinction.  
0 = Fail or withdrawal after the day-30 landmark.

## Adjustment set

Numeric:
- studied_credits;
- num_of_prev_attempts;
- date_registration.

Categorical:
- age_band;
- highest_education;
- imd_band;
- disability;
- gender;
- region.

The adjustment set is frozen before outcome estimation. Assessment scores and post-landmark behavior are excluded.

## Missing data

The primary analysis is complete-case on the frozen adjustment set. The generated result records:
- landmark cohort size before complete-case filtering;
- missing count for every covariate;
- number excluded for any missing adjustment covariate;
- final complete-case sample size.

Complete-case analysis can induce selection bias and is treated as a study limitation.

## Propensity model

The primary model is L2 logistic regression with:
- standardization for numeric covariates;
- one-hot encoding for categorical covariates.

This avoids imposing arbitrary linear spacing on age, education, deprivation, gender, disability and region categories.

## Diagnostics

Before interpreting the contrast, report:
- treated/control propensity ranges;
- empirical common support;
- ATE weight distribution;
- total and group effective sample size;
- covariate SMDs before and after weighting;
- residual balance flags;
- clipping sensitivity;
- common-support restriction sensitivity;
- propensity-specification sensitivity.

## Effect reporting

Keep separate:
- raw treated-minus-control difference;
- Horvitz-Thompson ATE-style estimate;
- normalized Hájek ATE-style estimate;
- fixed-propensity bootstrap interval;
- full-refit bootstrap interval.

The **full-refit bootstrap is primary** because the propensity model is re-estimated inside each resample.

## Uncertainty boundary

The bootstrap quantifies sampling and propensity-model estimation variability conditional on:
- the selected module-presentation;
- the day-30 landmark definition;
- the frozen covariate set;
- the complete-case rule;
- the chosen model family.

It does not quantify uncertainty from alternate landmark days, alternate cohorts, unmeasured confounding or alternative causal structures.

## Identification assumptions

A causal interpretation additionally requires:
- consistency;
- conditional exchangeability given measured pre-landmark covariates;
- positivity;
- no relevant interference;
- correct exposure, outcome and covariate measurement;
- a defensible interpretation of the landmark population.

These assumptions are not verified by achieving good measured balance.

## Main threats

Unmeasured motivation and prior achievement, work/access constraints, informative missingness, conditioning on survival/continued registration to the landmark, model misspecification, overlap problems, measurement error and cohort-specific effects all remain relevant.

The landmark design fixes a temporal misalignment; it does not transform an observational study into a randomized experiment.
