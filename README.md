# Causal Learning Analytics

> Transparent causal-analysis scaffold for propensity modeling, ATE weighting, common support, covariate balance, uncertainty, and sensitivity review.

[![CI](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/ci.yml)

![Causal Learning Analytics workflow](assets/architecture.svg)

**Area:** AI in Education (AIEd) · Causal Learning Analytics  
**Status:** working research prototype  
**Author:** Devis Wawan Saputra

## What this project is for

Prediction can tell us which learners are likely to struggle. It does not by itself tell us whether an intervention caused an outcome.

This repository provides a compact, inspectable baseline for a binary-treatment observational causal question. It separates:

- the causal estimand
- the propensity model
- empirical overlap
- inverse-probability weights
- measured covariate balance
- raw and adjusted outcome contrasts
- uncertainty
- sensitivity to clipping
- assumptions that the code cannot verify

The software can calculate an adjusted contrast. It cannot turn a weak study design into a credible causal claim.

## Research questions

1. What average treatment effect is being targeted?
2. How different is the unadjusted contrast from the IPW-adjusted estimate?
3. Do treated and control observations share enough empirical propensity support?
4. Does weighting improve measured pre-treatment covariate balance?
5. Are the weights stable enough to support the intended estimand?
6. How sensitive is the result to clipping and propensity-model choices?

## End-to-end workflow

![Causal Learning Analytics data and reasoning flow](assets/data_flow.svg)

The implemented path is:

1. define the ATE causal analysis record
2. validate binary treatment, outcomes, and pre-treatment covariates
3. estimate propensity scores with the included logistic baseline or supply scores from another model
4. inspect treated/control empirical common support
5. construct ATE inverse-probability weights
6. inspect weight magnitude and effective sample size
7. compare measured covariate balance before and after weighting
8. report the raw outcome contrast
9. estimate Horvitz-Thompson and normalized Hájek ATEs
10. report fixed-propensity bootstrap uncertainty
11. compare clipping specifications
12. surface review flags before causal interpretation

## Causal analysis record

`causal_analysis_record()` makes the study declaration explicit:

- estimand
- treatment
- outcome
- pre-treatment covariates
- propensity-score source
- identifying assumptions

See `docs/causal_analysis_record_example.json`.

The current implementation supports **ATE only**.

## Propensity modeling

`fit_propensity_logistic()` provides a small dependency-free logistic baseline for named continuous pre-treatment covariates.

It:

- standardizes covariates
- fits an intercept and slopes
- supports optional L2 regularization
- reports convergence and iteration count
- returns standardized coefficients
- returns the means/scales used in standardization
- returns treatment-probability estimates

This is deliberately transparent and useful for reproducible demonstrations. It is not presented as a replacement for mature statistical software in complex empirical work.

Externally estimated propensity scores can also be supplied directly.

## Positivity and clipping

Ordinary ATE IPW requires nonzero probability of each treatment level in the relevant covariate strata.

The baseline does **not** silently repair propensity scores at exactly 0 or 1.

Without an explicit clipping choice, endpoint scores raise an error.

When clipping is requested, the output records:

- clipping threshold
- number of changed scores
- original score range
- score range actually used

The analysis adds review flags when positivity problems or clipping are present.

## Empirical common support

`common_support()` compares the observed propensity ranges in the treated and control groups.

It reports:

- treated propensity range
- control propensity range
- their intersection
- treated fraction inside the intersection
- control fraction inside the intersection
- overall fraction inside the intersection

This replaces the earlier fixed 0.1–0.9 score count, which did not actually compare the two treatment groups.

Common support remains a diagnostic, not proof that positivity holds everywhere.

## Weight diagnostics

ATE weights are generated with:

`ipw_weights()`

The repository reports:

- minimum weight
- maximum weight
- mean weight
- overall Kish effective sample size
- treated effective sample size
- control effective sample size

A highly unstable weighted sample is surfaced for review rather than hidden behind the effect estimate.

## Covariate balance

`covariate_balance()` reports treated/control means and standardized mean differences for named pre-treatment covariates.

The same diagnostics can be calculated before and after weighting.

If a standardized difference cannot be estimated because the relevant within-group scale is zero or a group is too small, the function returns `None`.

It does **not** return zero and falsely imply perfect balance.

The default integrated review threshold is absolute SMD > 0.10. That is a practical diagnostic threshold, not proof that all confounding has been eliminated.

## Raw and adjusted effects

The integrated analysis reports three different quantities:

- raw treated-minus-control mean difference
- Horvitz-Thompson IPW ATE
- normalized Hájek IPW ATE

Keeping them separate makes it visible how much the weighting changes the observed contrast.

## Uncertainty

`bootstrap_ipw_ci()` returns a seeded percentile-bootstrap confidence interval for the Hájek estimate.

Important limitation: the current bootstrap treats the supplied propensity scores as fixed.

It therefore does not capture the full uncertainty from estimating the propensity model.

## Clipping sensitivity

`clipping_sensitivity()` compares:

- Horvitz-Thompson ATE
- Hájek ATE
- number of clipped scores
- maximum weight
- effective sample size

across several clipping thresholds.

This tests one design choice. It is **not** a formal sensitivity analysis for an unmeasured confounder.

## Integrated analysis

`analyze_ipw()` combines the current baseline into one result:

- estimand
- sample size and group counts
- raw outcome contrast
- HT ATE
- Hájek ATE
- bootstrap CI
- original and used propensity ranges
- clipping diagnostics
- group-aware common support
- weight diagnostics and ESS
- covariate balance before weighting
- covariate balance after weighting
- clipping sensitivity
- causal review flags

Current review flags can include:

- `causal_assumptions_unverified`
- `small_group`
- `positivity_violation`
- `propensity_clipping_used`
- `poor_common_support`
- `extreme_weights`
- `low_effective_sample_size`
- `post_weight_balance_not_estimable`
- `post_weight_balance_problem`

The first flag is always present because observed-data arithmetic cannot verify the complete causal identification argument.

## Synthetic demo

![Synthetic demo snapshot for Causal Learning Analytics](assets/demo_snapshot.svg)

The bundled example uses 12 synthetic observational records and two pre-treatment covariates.

For the supplied scores, the software demonstrates:

- raw mean difference around 0.245
- Horvitz-Thompson ATE around 0.227
- Hájek ATE around 0.237
- 95% fixed-propensity bootstrap interval around 0.196 to 0.284
- empirical common-support fraction around 0.833
- effective sample size around 11.84 of 12
- maximum weight around 2.38
- one covariate whose weighted SMD remains above the review threshold

The remaining imbalance is deliberately left visible rather than presenting the synthetic example as a clean causal success.

These values are software demonstrations, not evidence that an educational intervention works.

## Data

`data/sample.csv` contains the same 12 synthetic records used to document the schema.

`data/README.md` explains temporal ordering, propensity-score provenance, positivity, common support, balance, missing-data boundaries, and governance expectations.

## Run the demo

```bash
git clone https://github.com/devissaputra/causal_learning_analytics.git
cd causal_learning_analytics
python scripts/run_demo.py
python -m unittest discover -s tests -v
```

The current baseline uses only the Python standard library.

## Core API

`fit_propensity_logistic(...)` estimates a transparent logistic propensity baseline.

`ipw_weights(...)` creates ATE inverse-probability weights and reports explicit clipping.

`raw_mean_difference(...)` returns the unadjusted treated-minus-control outcome difference.

`ipw_ate(..., normalized=False)` returns the Horvitz-Thompson ATE.

`ipw_ate(..., normalized=True)` returns the Hájek ATE.

`common_support(...)` summarizes treated/control empirical propensity overlap.

`standardized_mean_difference(...)` calculates unweighted or weighted balance and returns `None` when the scale is not estimable.

`covariate_balance(...)` reports balance for named pre-treatment covariates.

`weight_diagnostics(...)` reports magnitude and effective sample size.

`bootstrap_ipw_ci(...)` returns fixed-propensity bootstrap uncertainty.

`clipping_sensitivity(...)` compares several clipping choices.

`analyze_ipw(...)` runs the integrated baseline.

## Evaluation view

![Causal Learning Analytics evaluation checklist](assets/evaluation_dashboard.svg)

The graphic shows dimensions a real analysis should inspect. The bars are illustrative and are not empirical validation results.

## Limits and responsible use

This repository cannot establish:

- absence of unmeasured confounding
- correctness of a causal graph
- consistency
- no interference
- appropriate outcome measurement
- whether the adjustment set is sufficient

It does not currently implement doubly robust estimation, matching, overlap weights, ATT/ATC, longitudinal treatment, instrumental variables, difference-in-differences, regression discontinuity, heterogeneous treatment effects, cluster-aware inference, or formal sensitivity analysis for unmeasured confounding.

See `docs/ethics_and_risks.md` before using observational causal estimates to inform educational decisions.

## Repository map

```text
.
├── .github/workflows/ci.yml
├── assets/
│   ├── architecture.svg
│   ├── data_flow.svg
│   ├── demo_snapshot.svg
│   └── evaluation_dashboard.svg
├── data/
│   ├── README.md
│   └── sample.csv
├── docs/
│   ├── causal_analysis_record_example.json
│   ├── ethics_and_risks.md
│   ├── related_work.md
│   └── research_protocol.md
├── reports/model_card.md
├── scripts/run_demo.py
├── src/causal_learning_analytics/core.py
├── tests/test_core.py
├── .gitignore
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── README.md
```

## Research path

A stronger empirical version would:

1. reproduce a public observational education study from raw data to reported estimate
2. compare several justified propensity specifications
3. add distributional balance diagnostics beyond means
4. add doubly robust estimation
5. propagate propensity-model uncertainty
6. add missing-data sensitivity
7. implement a formal unmeasured-confounding sensitivity method
8. benchmark estimates against mature causal-inference libraries

## Related work

`docs/related_work.md` places the implementation alongside established causal-inference guidance and mature causal software while keeping the scope of this dependency-free baseline explicit.

## Citation and license

`CITATION.cff` contains the software citation. Code and original SVG visuals use the MIT License. External datasets retain their own licenses, governance requirements, and ethics constraints.
