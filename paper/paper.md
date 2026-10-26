# Paper 2 — Day-30 OULAD Landmark Observational Analysis

**22 October 2026 — current scientific status:** The author-review manuscript is [the nine-page integrated LaTeX source](main_integrated_20261022.tex). The repository's original focal numerical results have been independently reproduced from the source-verified original UCI archive. A new follow-up also calculated 1,000 full-refit student-bootstrap resamples for each of three other presentations. This overview is not a separate competing manuscript.

## Focal empirical results (CCC / 2014J)

- Day-30 eligible 1,983; after missing covariates 1,850; after category support restriction 1,820 (1,624 earlier submissions; 196 no earlier submission).
- Raw favorable-outcome rate difference 0.374296.
- ATE-style normalized Hájek IPW contrast 0.386110, independent full-refit 95% percentile interval [0.324225, 0.444675].
- ATO-style overlap-weighted contrast 0.326066, interval [0.266654, 0.387026]. **This targets a different weighted population.**
- IPW ESS 509.52, comparison-arm ESS 133.81, maximum inverse weight 38.64, maximum absolute weighted SMD 0.1161.
- Missingness and support restrictions exclude 8.22% of initially day-30-eligible cases; the unadjusted outcome rate difference is 0.376763 before exclusions versus 0.374296 in the final sample.

## Independent new uncertainty across other presentations

The three cohorts were previously selected without examining outcomes, by their observed size and supported exposed/unexposed cell counts. The new uncertainty analyses were conducted **post hoc** and therefore are not confirmatory tests.

| Presentation | Analytic n | No earlier submission | IPW association | 95% full-refit bootstrap interval |
|---|---:|---:|---:|---|
| FFF / 2013J | 1,867 | 178 | 0.5032 | [0.4479, 0.5476] |
| BBB / 2013J | 1,804 | 217 | 0.4768 | [0.4126, 0.5368] |
| BBB / 2014J | 1,752 | 96 | 0.5610 | [0.4636, 0.6324] |

[Successful isolated GitHub Actions verification](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39777348662) · [Machine-readable full original results](../results/paper2_cross_presentation_bootstrap_20261022.json) · [Reproducible source](../scripts/independent_cross_presentation_bootstrap.py).

## Critical limitations

**This is not a causal intervention study.** Earlier submission can reflect motivation, assessment availability, learner workload and requirements for passing. Survival/registration to day 30 conditions on an outcome of earlier processes; post-landmark submission also has structural dependence with course completion. The non-earlier group includes 98 later submitters (32 favorable) and 98 with no later recorded submission (zero favorable). Covariate weighting does not eliminate hidden confounding, positivity failures or selection bias, and multiple course presentations do not prove universal transportability.

A prospective design would need assignment of a feasible intervention **before** the exposure window, such as a defined reminder and submission-support policy, with outcomes analyzed by original assignment. The present dataset does not contain such an assignment.

## Source and evidence

- [Original data](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset), SHA-256 `f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4`.
- [Primary official source independent reproduction](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39684326436).
- [Extended propensity and cross-presentation exploratory analysis](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39686498958).
- [Missingness/selection audit](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39688599327).
- [New 3,000-resample cross-presentation uncertainty](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39777348662).
- [Final manuscript](main_integrated_20261022.tex) and [QA proof](FINAL_QA_RESULTS_20261022.json).

## Release boundary

The nine-page LaTeX manuscript compiles cleanly and **83/83 numeric/source/document QA assertions passed** against the archived sources, with a clean-room compilation. The minimal arXiv source ZIP and full research package are stored in the owner's ChatGPT Library folder `/Paper2_Final_20261022`. **Author review, independent human scientific assessment, any arXiv endorsement, and arXiv submission remain pending.** No draft GitHub branch is represented as merged or peer reviewed.
