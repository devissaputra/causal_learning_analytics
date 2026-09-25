# Ethics and Causal-Interpretation Boundary

This repository is an observational learning-analytics study. The adjusted contrast is not automatically a causal effect.

A causal interpretation would require, among other assumptions, adequate measurement of confounders, conditional exchangeability, positivity, consistency, no material interference, and correct exposure/outcome definitions. The available OULAD covariates cannot verify those assumptions.

## Educational risks

Early submission can reflect prior preparation, work schedules, access, disability, motivation, assessment structure, or other factors that are not fully measured. Treating the exposure as an intervention without further evidence could lead to inappropriate pressure or inequitable policies.

## Safeguards

The bundle makes the exposure window explicit, excludes post-exposure scores from adjustment, reports overlap and weight diagnostics, reports balance before and after weighting, retains raw and adjusted estimates, and always preserves a `causal_assumptions_unverified` flag.

No result should be used to label individual learners or mandate interventions without separate prospective validation and governance review.
