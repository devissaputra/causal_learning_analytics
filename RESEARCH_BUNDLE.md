# Research Bundle Evidence Contract

## Identity

**Area:** AI in Education  
**Study:** day-30 landmark observational causal learning analytics  
**Dataset:** Open University Learning Analytics Dataset (OULAD)

## Frozen empirical declaration

- unit: learner registration within one module-presentation;
- landmark: presentation day 30;
- eligibility: registered by day 30 and still registered after day 30;
- exposure: at least one non-banked assessment submission after registration and by day 30;
- outcome: Pass/Distinction versus Fail/withdrawal after the landmark;
- estimand implemented by the engine: ATE-style observational contrast;
- adjustment: frozen measured pre-landmark registration/demographic covariates;
- primary uncertainty: full-refit percentile bootstrap.

## Required executable evidence

A valid empirical run records:

1. UCI source, DOI, archive SHA-256 and source files;
2. source registration count;
3. late/missing registration exclusions;
4. unregistration on/before landmark exclusions;
5. unknown withdrawal-timing exclusions;
6. banked assessment records excluded from exposure;
7. submissions before registration excluded from exposure;
8. selected module-presentation;
9. landmark cohort size;
10. missing count per covariate and complete-case exclusions;
11. categorical baseline levels lacking both exposure groups and the resulting positivity-support exclusions;
12. final sample size and exposure prevalence;
13. numeric/categorical propensity specification;
14. propensity-score range and common support;
15. ATE weight diagnostics and effective sample size;
16. SMDs before and after ATE weighting for expanded categorical indicators;
17. raw, Horvitz-Thompson and Hájek ATE-style contrasts;
18. fixed-propensity bootstrap interval;
19. full-refit ATE bootstrap interval and seed;
20. overlap-weighted ATO sensitivity estimate, interval, ESS and balance;
21. clipping sensitivity;
22. common-support sensitivity;
23. alternative propensity-specification sensitivity;
24. environment versions;
25. empirical figures;
26. analysis flags including causal_assumptions_unverified.

## Authoritative evidence

The machine-readable empirical source is results/oulad_metrics.json.

Generated derivatives:
- results/summary.md;
- paper/results.md;
- results/figures/propensity_overlap.png;
- results/figures/balance_love_plot.png;
- results/figures/weight_distribution.png;
- results/figures/propensity_specification_sensitivity.png.

## Statistical boundary

Measured balance is a diagnostic for the measured adjustment set, not evidence that unmeasured confounding has been eliminated.

The full-refit bootstrap propagates propensity-estimation variability, but it remains conditional on the frozen study design and cannot quantify structural causal uncertainty.

## Non-claims

The bundle does not claim:
- early submission is randomized;
- early submission itself causes course success;
- all confounders are measured;
- one OULAD cohort generalizes to other institutions or periods;
- the landmark population is identical to the full enrolled population;
- the results justify learner-level intervention or pressure.
