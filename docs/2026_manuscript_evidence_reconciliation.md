# Manuscript and numerical provenance reconciliation (7 November 2026)

This file explains how the 6 November 2026 OULAD PDF relates to the repository's stored numerical outputs. It is an audit note, not peer review or proof of causal identification.

## Primary full-refit interval versus secondary fixed-propensity interval

For CCC/2014J day-30, 1,820 analytic students (1,624 early submitters and 196 others), the Hájek IPW-style observational contrast is 0.38611041153085035.

The **primary uncertainty analysis** refits the propensity model inside each of 1,000 learner bootstrap samples. Its 95% interval is **[0.3242251977371366, 0.4446753992869758]**, stored at:
`results/oulad_metrics.json -> full_refit_bootstrap.interval`.

A **secondary conditional bootstrap** retains the original fitted propensity scores. Its 95% interval is **[0.32670279667872204, 0.44460955965156906]**, stored at:
`results/oulad_metrics.json -> hajek_ate_ci`.

These are two distinct procedures, not contradictory estimates of the same numerical calculation. The 6 November manuscript reports the primary full-refit interval (rounded 0.3242 to 0.4447). The main JSON key name `hajek_ate_ci` is easy to misunderstand when viewed without `bootstrap_note`; use the explicit provenance paths above. Do **not** overwrite either result to force agreement.

The overlap-weighted observational contrast is 0.3260659651759402, with **full-refit** interval [0.26665393325650577, 0.38702555498848756]. It targets the propensity-overlap population rather than the IPW-style target.

See also `results/summary.md`, which correctly reports both intervals and labels the primary bootstrap.

## Manuscript and repository edition

The supplied PDF is dated 6 November 2026 and contains additional cross-presentation studies and references. The default-branch `paper/paper.md` and README are earlier overview materials, not a proven line-by-line match for the final PDF. Their earlier statement that "the complete experiment was not rerun in this review" describes that review's scope; it must not be mistaken for a denial of later independent GitHub Actions reproduction.

A previous independent verification run for the primary cohort is recorded in [Actions run 39684326436](https://github.com/devissaputra/causal_learning_analytics/actions/runs/39684326436) and completed successfully. The manuscript cites later supplementary runs; those artifact and commit links require their own version-by-version confirmation. The latest arXiv-ready source package is not established by the default-branch `paper/paper.md`.

## Known manuscript review issue

The 6 November manuscript's related-work discussion refers to 2026 OULAD prediction studies by "Wu, Jia and Pham" and "Wu, Duan and Luo". Verify that each corresponds to a separate real bibliographic entry and that citations, author lists, year, and claims agree with the final reference list. Do not silently merge these references or invent metadata.

## Scientific interpretation

All contrasts remain observational. Landmark selection, unavailable individual assessment opportunities and deadlines, unmeasured motivation/preparation, extreme weights and residual imbalance prevent causal claims. An apparent positive interval cannot establish effects of forcing or encouraging earlier submission.

## Outstanding tasks

1. Version the exact 6 November manuscript source, figures, and bibliography; reconcile each table and reference.
2. Independently rerun the pinned complete analysis where source data access permits, including verification of data SHA-256 and the 1,000 full-refit bootstraps.
3. Verify citations against publisher records and complete an author review.
4. Do not change numerical values without new, independently checked evidence.
