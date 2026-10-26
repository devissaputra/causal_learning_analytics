# Paper 2 — Final research and author-review package (22 October 2026)

## Release status
Technically reviewed working preprint. **Not** externally peer-reviewed, not proven causal, not uploaded to arXiv, and not accepted. Author approval is required.

## Source of truth
- `Paper2_OULAD_Final_Integrated_20261022.pdf`: final typeset preprint
- `Paper2_Final_arXiv_Source_20261022.zip`: minimal LaTeX source to upload after author review (TeX and two PNG figures only)
- `Paper2_Final_Research_and_Release_QA_20261022.pdf`: completed/missing gate matrix
- `FINAL_QA_RESULTS.json`: reproducible numeric/compilation assertions, 83/83 passed
- `CROSS_PRESENTATION_20261022.json`: current-turn numeric summary of full-refit intervals; canonical aggregate output on GitHub
- `evidence/`: pinned, individually non-identifying aggregate study JSON and tests

## Empirical evidence
Official OULAD UCI 349 https://doi.org/10.24432/C5KK69
Checksum SHA256 f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4
Independent raw-data focal verification https://github.com/devissaputra/causal_learning_analytics/actions/runs/39684326436
Independent additional-presentation analysis https://github.com/devissaputra/causal_learning_analytics/actions/runs/39686498958
Selection and missingness audit https://github.com/devissaputra/causal_learning_analytics/actions/runs/39688599327
New 3x1000 full-refit intervals https://github.com/devissaputra/causal_learning_analytics/actions/runs/39777348662
Evidence code draft PR #1 https://github.com/devissaputra/causal_learning_analytics/pull/1
Finalization follow-up branch https://github.com/devissaputra/causal_learning_analytics/tree/research/paper2-cross-presentation-final-20261022

## Conceptual limitation
The 30-day earlier-submission indicator is not a randomly assigned or well-defined behavioral intervention. No credible causal identification strategy is available in these observational OULAD records; no weighting or additional p-value changes that fact.

## arXiv upload instructions
Upload `Paper2_Final_arXiv_Source_20261022.zip` after confirming the author and reviewing claims. Do not upload the full research ZIP as the TeX source file. arXiv may request account/category endorsement and applies moderation. Verify category and full preview before confirmation.

## Author-review checklist
[ ] Verify you actually performed or supervised and understand the research and accept responsibility for the results.
[ ] Verify name/affiliation/ORCID, source archive and figures, citations and dates.
[ ] Confirm that the paper states associations, not policy effects.
[ ] Review ethical/licensing notices and disclose AI assistance consistently with destination policy.
[ ] Decide whether to merge research PRs; submission through arXiv is author-controlled.