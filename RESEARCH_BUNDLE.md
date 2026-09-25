# Research Bundle Evidence Contract

## Identity
**Area:** AI in Education  
**Study:** observational causal learning analytics  
**Dataset:** Open University Learning Analytics Dataset (OULAD)

## Frozen empirical declaration
- unit: learner registration within one module-presentation;
- exposure: at least one assessment submitted by day 30;
- outcome: Pass/Distinction versus Fail/Withdrawn;
- estimand implemented by the engine: ATE;
- adjustment: measured pre-treatment registration/demographic covariates.

## Evidence required
A valid empirical run reports:
1. cohort code and presentation;
2. sample size and treatment prevalence;
3. treatment/outcome definitions and time cutoff;
4. covariate list and missing-data handling;
5. propensity-score range;
6. common support;
7. weight diagnostics and effective sample size;
8. standardized mean differences before/after weighting;
9. raw, Horvitz-Thompson and Hájek contrasts;
10. uncertainty interval and analysis flags.

## Non-claims
The repository never treats measured balance as proof of exchangeability. It does not claim elimination of unmeasured confounding, randomized-treatment equivalence, or pedagogical effectiveness.
