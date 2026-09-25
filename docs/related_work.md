# Related Work and Methodological Context

This repository is a compact, inspectable causal-learning-analytics research bundle. It is not a replacement for mature causal-inference software.

## OULAD

Kuzilek, Hlosta, and Zdrahal introduced OULAD as a linked public educational dataset covering demographics, registration, assessment and VLE interactions.

- Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). *Open University Learning Analytics dataset*. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171

The source documentation defines date_unregistration as the learner's module unregistration day and is_banked as a transferred assessment result. Those fields are central to the landmark exposure design.

## Target-trial timing and landmark logic

Hernán, Sauer, Hernández-Díaz, Platt, and Shrier describe how observational analyses can introduce immortal-time and related design biases when eligibility, treatment assignment and time zero are misaligned.

- Hernán, M. A., Sauer, B. C., Hernández-Díaz, S., Platt, R., & Shrier, I. (2016). *Specifying a target trial prevents immortal time bias and other self-inflicted injuries in observational analyses*. Journal of Clinical Epidemiology, 79, 70–75. https://doi.org/10.1016/j.jclinepi.2016.04.014

The day-30 landmark in this repository is motivated by that design principle: treatment classification is completed by the landmark, eligibility is established at the landmark, and later outcome is evaluated afterward.

The study is not presented as a full target-trial emulation because treatment strategies are not randomized and the measured adjustment set is incomplete.

## Causal identification and IP weighting

Hernán and Robins' *Causal Inference: What If* describes inverse-probability weighting in the potential-outcomes framework and emphasizes exchangeability, positivity and consistency.

- Hernán, M. A., & Robins, J. M. *Causal Inference: What If*. Chapman & Hall/CRC. https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/

## Weighting and balance diagnostics

Austin and Stuart emphasize inspection of inverse-probability weights and weighted covariate balance.

- Austin, P. C., & Stuart, E. A. (2015). *Moving towards best practice when using inverse probability of treatment weighting (IPTW) using the propensity score to estimate causal treatment effects in observational studies*. Statistics in Medicine, 34, 3661–3679. https://doi.org/10.1002/sim.6607

The bundle reports overlap, weight distributions, effective sample size and standardized mean differences before and after weighting.

## Software comparison context

Useful mature tools include:
- cobalt for balance diagnostics: https://ngreifer.github.io/cobalt/
- DoWhy for explicit causal graphs/workflows: https://www.pywhy.org/dowhy/
- EconML for heterogeneous treatment effects: https://www.pywhy.org/EconML/

This repository remains intentionally smaller so every transformation and diagnostic can be inspected.

## Current scope

Implemented:
- day-30 landmark eligibility;
- banked-assessment exclusion;
- one module-presentation at a time;
- mixed numeric/categorical propensity model;
- ATE IP weighting;
- HT and Hájek contrasts;
- empirical common support;
- ESS and weight diagnostics;
- expanded before/after balance;
- fixed-propensity bootstrap;
- full-refit bootstrap;
- clipping sensitivity;
- common-support sensitivity;
- alternative propensity specifications.

Not implemented:
- doubly robust outcome modeling;
- multiple imputation;
- time-varying treatment methods;
- instrumental variables;
- difference-in-differences;
- causal forests;
- formal quantitative sensitivity bounds for unmeasured confounding.

Those are appropriate extensions rather than hidden claims.
