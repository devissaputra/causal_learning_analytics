# Ethics and Causal-Interpretation Boundary

This repository is an observational learning-analytics study. The adjusted contrast is not automatically a causal effect.

## Temporal safeguard

The study uses a day-30 landmark so learners who already unregistered during the exposure-assignment window are not retrospectively classified as unexposed failures. Banked assessment results transferred from prior presentations are also excluded from the exposure.

These safeguards reduce specific timing and exposure-definition biases; they do not remove confounding.

## Causal assumptions

A causal interpretation would require, among other assumptions:
- adequate measurement of confounders;
- conditional exchangeability;
- positivity;
- consistency;
- no material interference;
- correct exposure/outcome measurement;
- a defensible interpretation of conditioning on continued registration to day 30.

The available OULAD variables cannot verify these assumptions.

## Sensitive baseline attributes

Gender, disability, deprivation band and region are used only as baseline adjustment variables in an aggregate causal analysis. Their inclusion does not imply they should be used to score or rank individual learners.

Subgroup fairness claims require a separately designed analysis; the current study does not claim fairness from aggregate balance.

## Educational risks

Early submission may reflect prior preparation, work schedules, disability, access, assessment design, motivation or course-specific constraints. Treating the observed association as an intervention effect could lead to inappropriate pressure on learners or inequitable policy.

## Privacy

OULAD is anonymized public research data. Do not attempt re-identification or link student identifiers to external identities.

## Deployment boundary

No result should be used to:
- label individual ability or motivation;
- mandate submission behavior;
- automate learner sanctions;
- allocate high-stakes opportunities;
- justify intervention without prospective validation and governance review.

A real intervention would require separate impact evaluation, accessibility review, learner/educator oversight and rollback criteria.
