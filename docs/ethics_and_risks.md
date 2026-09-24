# Ethics, safety, and misuse risks

## Intended use

Causal Learning Analytics is a research scaffold for studying whether an educational intervention may have changed an outcome under explicitly stated assumptions.

It should not be used to turn observational correlations into authoritative causal claims.

## Main risk: causal overclaiming

Inverse-probability weighting can produce a precise-looking number even when the identifying assumptions are not credible.

Measured covariate balance, propensity overlap, stable weights, and a narrow confidence interval do not establish that all important confounders were measured.

Every empirical report should distinguish:

- what the software calculated
- what assumptions are required for a causal interpretation
- which assumptions were empirically diagnosed
- which assumptions remain fundamentally unverified

## Adjustment-set risk

Including post-treatment variables can induce bias.

Do not add a variable to the propensity model simply because it predicts treatment or outcome well.

The adjustment set should be justified from the temporal and causal structure of the study.

## Intervention decisions

Do not use a single observational estimate to automatically decide who should receive educational support, who should be denied support, which teacher should be sanctioned, or which program should be removed.

Consequential decisions should consider design quality, uncertainty, replication, distributional effects, implementation constraints, and the possibility of unmeasured confounding.

## Fairness and heterogeneity

An average treatment effect can hide different effects across learner groups and contexts.

The current repository does not estimate heterogeneous treatment effects and should not be interpreted as showing that an intervention works equally well for everyone.

Subgroup analysis also creates privacy and multiplicity risks and requires adequate sample size and pre-specified reasoning.

## Privacy

Causal analyses can encourage collection of extensive background variables in the name of confounding control.

Collect only information that is defensible for the study question. Protect educational records, demographic information, disability data, behavioral traces, and other sensitive fields.

Do not expand surveillance simply to improve a propensity model.

## Positivity and exclusion

Trimming or clipping difficult observations can change the population represented by the estimate.

Any exclusion, trimming, or clipping choice should be reported transparently with counts and rationale.

Do not remove observations merely because they make the result less favorable.

## Uses excluded from this prototype

Do not use this repository alone for:

- high-stakes learner placement or exclusion
- admissions, grading, discipline, or employment decisions
- teacher or employee punishment
- covert experimentation
- claims that an observational intervention is proven effective
- automated subgroup targeting without ethical and methodological review

## Before real use

Document the causal question, target population, treatment, outcome timing, estimand, adjustment set, propensity-model provenance, missing-data plan, overlap, weight diagnostics, balance, uncertainty, sensitivity analysis, privacy protections, and who is responsible for reviewing causal claims before they influence practice.
