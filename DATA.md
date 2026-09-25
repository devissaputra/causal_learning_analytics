# Dataset Card — Open University Learning Analytics Dataset (OULAD)

## Source

Primary dataset: Open University Learning Analytics Dataset (OULAD)  
UCI Machine Learning Repository dataset: 349  
DOI: https://doi.org/10.24432/C5KK69  
License reported by UCI: CC BY 4.0  
Original project: https://analyse.kmi.open.ac.uk/open_dataset

The empirical runner downloads the UCI-hosted archive. Raw source data are cached locally under `data/cache/` and are not committed.

## Tables used

The frozen study uses only:

- `studentInfo.csv`
- `studentRegistration.csv`
- `assessments.csv`
- `studentAssessment.csv`

The large VLE interaction table is not required for the current estimand.

## Provenance

A successful external-data run records:

- UCI dataset ID;
- DOI and license;
- canonical download URL;
- SHA-256 of the downloaded archive;
- exact table names used.

## Temporal boundary

Exposure is defined as at least one assessment submission on or before presentation day 30. The adjustment set is restricted to registration/background information. Assessment score and later learning behavior are excluded from the propensity model.

## Missingness

The current frozen adapter uses complete-case analysis on the predefined adjustment covariates. This can change the study population and is therefore recorded as a design limitation, not silently treated as harmless.

## Limitations

OULAD represents historical Open University distance-learning contexts. The selected module-presentation and complete-case cohort are not automatically representative of other courses, institutions, countries, or present-day learners.
