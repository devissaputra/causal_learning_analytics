# Related work and methodological context

Causal Learning Analytics is an original compact implementation intended to make a small inverse-probability-weighting workflow inspectable.

It is not a replacement for mature causal-inference software.

## Causal identification and inverse-probability weighting

Hernán and Robins' open text *Causal Inference: What If* presents inverse-probability weighting in the potential-outcomes framework and emphasizes the role of identification assumptions such as positivity.

- Book: https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/

The repository follows the same basic principle: weighting arithmetic is meaningful only in the context of a clearly defined causal question and defensible assumptions.

## Propensity weighting and balance diagnostics

Austin and Stuart describe best-practice diagnostics for inverse-probability-of-treatment weighting, including inspection of weight distributions and weighted standardized differences for measured baseline covariates.

- Austin PC, Stuart EA. *Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies.* Statistics in Medicine. 2015.
- DOI: https://doi.org/10.1002/sim.6607
- Open article: https://pmc.ncbi.nlm.nih.gov/articles/PMC4626409/

The current implementation mirrors that emphasis by reporting both weight diagnostics and before/after covariate balance.

## Standardized mean differences

The baseline computes continuous-covariate standardized mean differences from treated/control means and pooled group variances.

When weights are supplied, the group means and sample variances are replaced by their weighted counterparts.

A commonly used practical review threshold is an absolute standardized difference around 0.10, but this repository treats that value as a review signal rather than proof that confounding has been eliminated.

## Relationship to mature software

Useful comparison targets include:

- **cobalt** for covariate-balance assessment and visualization: https://ngreifer.github.io/cobalt/
- **DoWhy** for explicit causal-model workflows: https://www.pywhy.org/dowhy/
- **EconML** for heterogeneous treatment-effect estimation: https://www.pywhy.org/EconML/

The repository deliberately remains smaller. Its role is to expose the mechanics and diagnostics clearly enough that each result can be inspected and tested.

## Scope of the current implementation

Implemented:

- simple logistic propensity estimation for continuous pre-treatment covariates
- externally supplied propensity scores
- ATE weighting
- Horvitz-Thompson and Hájek estimates
- empirical common support
- weight diagnostics and effective sample size
- before/after balance
- fixed-propensity bootstrap uncertainty
- clipping sensitivity

Not implemented:

- doubly robust estimators
- matching
- overlap weights
- ATT/ATC
- generalized treatments
- time-varying treatment
- instrumental variables
- regression discontinuity
- difference-in-differences
- causal forests
- formal sensitivity analysis for unmeasured confounding
