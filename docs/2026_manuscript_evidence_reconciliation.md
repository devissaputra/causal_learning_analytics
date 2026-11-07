## Authoritative uploaded PDF fingerprint

- Supplied manuscript edition: **6 November 2026**, 9 pages.
- PDF SHA-256: `dd942859428140bc2fbe59428a39d5b130b6f887a02800815b969271d7a31281`.
- This fingerprint identifies the uploaded reviewer-facing PDF, which is **not stored as an exact binary file in this repository**. It does not certify a matching LaTeX source or arXiv ZIP.

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

## Literature verification completed for the two 2026 Wu citations

The 6 November PDF's two OULAD references are **two distinct published studies**, not a duplicated or corrupted author list:

- Wu, S., Duan, J., and Luo, M. (2026). *Calibrated early-warning models with fairness auditing and selective prediction for course withdrawal risk: Evidence from OULAD*. PLOS ONE 21(7), e0352867. DOI: 10.1371/journal.pone.0352867. Published 15 July 2026. The publisher also issued a correction about a supplemental figure on 7 August 2026 (DOI 10.1371/journal.pone.0355736).
- Wu, M., Jia, J., and Pham, T. T. (2026). *Early warning of academic risk from the first four weeks of online learning activity and assessment performance: a leakage-controlled, demographic-data-minimizing study on the OULAD benchmark*. Frontiers in Education 11, 1917092. DOI: 10.3389/feduc.2026.1917092. Published 8 October 2026.

Both entries appear in the supplied 6 November PDF's bibliography. Publisher metadata and the manuscript's author/title/DOI fields agree at the level checked. This resolves the earlier apparent author inconsistency. It does not constitute exhaustive verification of all citations.

## Scientific interpretation

All contrasts remain observational. Landmark selection, unavailable individual assessment opportunities and deadlines, unmeasured motivation/preparation, extreme weights and residual imbalance prevent causal claims. An apparent positive interval cannot establish effects of forcing or encouraging earlier submission.

## Outstanding tasks

1. Version the exact 6 November manuscript source, figures, and bibliography; reconcile each table and reference.
2. Independently rerun the pinned complete analysis where source data access permits, including verification of data SHA-256 and the 1,000 full-refit bootstraps.
3. Verify citations against publisher records and complete an author review.
4. Do not change numerical values without new, independently checked evidence.
