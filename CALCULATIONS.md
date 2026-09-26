# Calculation guide

## Question and evidence

What outcome contrast accompanies early assessment submission?

OULAD CCC 2014J, day-30 landmark; 1,820 complete supported cases.

**Status:** RECORDED EXTERNAL-DATA STUDY | full experiment not rerun in this review.

## Design

Eligibility precedes exposure assignment; propensity weighting, balance/overlap diagnostics, full-refit bootstrap and overlap-weighted sensitivity.

## Calculation and interpretation

`Weighted contrast = sum(wT·Y)/sum(wT) - sum(wC·Y)/sum(wC).`

Treated weights are 1/e and control weights 1/(1-e), where e is estimated exposure propensity. Effective sample size is (sum w)^2/sum(w^2). ATE-style weighting does not itself identify a causal effect; overlap weighting changes the target population.

## Evidence table

Selected recorded values (units and context shown). Full precision below is for traceability, not a claim of measurement precision.

| Quantity | Value | Unit / meaning | JSON path |
|---|---:|---|---|
| Analysis cases | 1820 | count | `sample_size` |
| Raw contrast | 0.3742962702322309 | proportion difference | `raw_mean_difference` |
| Hájek weighted contrast | 0.3861104115308514 | proportion difference | `ipw_ate_hajek` |
| Effective sample size | 509.5228012320698 | weighted count | `weight_diagnostics.overall_ess` |

Source: [results/oulad_metrics.json](results/oulad_metrics.json). Values resolve directly from this file when figures are regenerated.

The recorded Hájek contrast is 0.3861, with a full-refit bootstrap interval of roughly 0.3242 to 0.4447, but the analysis flags extreme weights, limited effective sample size, and residual imbalance. An overlap-weighted sensitivity analysis yields 0.3261 for a different target population. These are observational contrasts; unmeasured confounding and selection remain barriers to claiming that requiring early submission would improve outcomes.

## Verification performed in this review

45 existing unittest checks passed. The complete data/model experiment was not rerun in this review. Stored empirical results were inspected, not independently reproduced from raw data.

The figure-generation check verifies agreement between the selected source values and SVGs. It does not validate the raw dataset, fitted model, identification assumptions, or external generalization.

```bash
python scripts/build_review_figures.py
python scripts/build_review_figures.py --check
```

## Implementation map

Follow these functions to inspect each transformation. Validation helpers and private functions remain visible in the linked modules.

| Function | Purpose / documented behavior |
|---|---|
| [`prepare_data_dir`](scripts/run_oulad_study.py#L54) | Inspect the explicit implementation and its callers. |
| [`build_table`](scripts/run_oulad_study.py#L97) | Inspect the explicit implementation and its callers. |
| [`choose_cohort`](scripts/run_oulad_study.py#L164) | Inspect the explicit implementation and its callers. |
| [`restrict_categorical_support`](scripts/run_oulad_study.py#L192) | Inspect the explicit implementation and its callers. |
| [`prepare_analysis`](scripts/run_oulad_study.py#L223) | Inspect the explicit implementation and its callers. |
| [`make_propensity_pipeline`](scripts/run_oulad_study.py#L246) | Inspect the explicit implementation and its callers. |
| [`fit_propensity`](scripts/run_oulad_study.py#L263) | Inspect the explicit implementation and its callers. |
| [`balance_covariates`](scripts/run_oulad_study.py#L275) | Inspect the explicit implementation and its callers. |
| [`overlap_weights`](scripts/run_oulad_study.py#L284) | Inspect the explicit implementation and its callers. |
| [`weighted_mean_difference`](scripts/run_oulad_study.py#L290) | Inspect the explicit implementation and its callers. |
| [`overlap_weighting_analysis`](scripts/run_oulad_study.py#L299) | Inspect the explicit implementation and its callers. |
| [`full_refit_bootstrap_ci`](scripts/run_oulad_study.py#L319) | Inspect the explicit implementation and its callers. |
| [`common_support_sensitivity`](scripts/run_oulad_study.py#L370) | Inspect the explicit implementation and its callers. |
| [`propensity_specification_sensitivity`](scripts/run_oulad_study.py#L393) | Inspect the explicit implementation and its callers. |
| [`write_figures`](scripts/run_oulad_study.py#L425) | Inspect the explicit implementation and its callers. |
| [`write_summary`](scripts/run_oulad_study.py#L496) | Inspect the explicit implementation and its callers. |
| [`run_study`](scripts/run_oulad_study.py#L561) | Inspect the explicit implementation and its callers. |
| [`main`](scripts/run_oulad_study.py#L621) | Inspect the explicit implementation and its callers. |
| [`ipw_weights`](src/causal_learning_analytics/core.py#L91) | Return ATE inverse-probability weights and clipping diagnostics. |
| [`raw_mean_difference`](src/causal_learning_analytics/core.py#L118) | Return the unadjusted treated-minus-control outcome mean difference. |
| [`ipw_ate`](src/causal_learning_analytics/core.py#L141) | Estimate the ATE using Horvitz-Thompson or normalized (Hajek) IPW. |
| [`fit_propensity_logistic`](src/causal_learning_analytics/core.py#L243) | Fit a transparent logistic propensity baseline on pre-treatment covariates. |
| [`common_support`](src/causal_learning_analytics/core.py#L405) | Summarize empirical treated/control propensity-score common support. |
| [`overlap_fraction`](src/causal_learning_analytics/core.py#L460) | Return the share of all observations inside empirical common support. |
| [`standardized_mean_difference`](src/causal_learning_analytics/core.py#L532) | Return treated-minus-control SMD, or None when scale is not estimable. |
| [`covariate_balance`](src/causal_learning_analytics/core.py#L589) | Return group means and SMDs for named pre-treatment covariates. |
| [`effective_sample_size`](src/causal_learning_analytics/core.py#L639) | Return Kish effective sample size for positive analysis weights. |
| [`weight_diagnostics`](src/causal_learning_analytics/core.py#L647) | Summarize ATE weight magnitude and effective sample size. |
| [`bootstrap_ipw_ci`](src/causal_learning_analytics/core.py#L699) | Percentile bootstrap CI conditional on the supplied propensity scores. |
| [`clipping_sensitivity`](src/causal_learning_analytics/core.py#L762) | Compare ATE estimates and weight stability across clipping choices. |
| [`causal_analysis_record`](src/causal_learning_analytics/core.py#L825) | Create a compact, serializable declaration of the causal analysis. |
| [`analyze_ipw`](src/causal_learning_analytics/core.py#L883) | Run a transparent ATE IPW baseline with diagnostics and review flags. |
| [`fraction_inside`](src/causal_learning_analytics/core.py#L432) | Inspect the explicit implementation and its callers. |

## What remains before a stronger research claim

Treated weights are 1/e and control weights 1/(1-e), where e is estimated exposure propensity. Effective sample size is (sum w)^2/sum(w^2). ATE-style weighting does not itself identify a causal effect; overlap weighting changes the target population. A successful software test is not validation of a scientific construct. New experiments should state their split unit, comparator, outcome, uncertainty procedure and failure criteria before examining final test results.
