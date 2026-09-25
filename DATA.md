# Dataset Card — Open University Learning Analytics Dataset (OULAD)

## Source

Primary dataset: Open University Learning Analytics Dataset (OULAD)  
UCI Machine Learning Repository dataset: 349  
DOI: https://doi.org/10.24432/C5KK69  
Original data paper: Kuzilek, Hlosta, & Zdrahal (2017), Scientific Data 4, 170171  
DOI: https://doi.org/10.1038/sdata.2017.171

The empirical runner downloads the UCI-hosted archive and records its SHA-256. Raw source files are stored only under gitignored data/cache/ and are not committed.

## Tables used

- studentInfo.csv
- studentRegistration.csv
- assessments.csv
- studentAssessment.csv

The current estimand does not require the large VLE interaction table.

## Fields critical to temporal validity

### date_registration
The learner's registration day for the module-presentation. The day-30 landmark cohort requires registration on or before day 30.

### date_unregistration
OULAD records the day of unregistration for learners who withdraw. This field is used to exclude learners who already left on or before the day-30 landmark.

### is_banked
OULAD defines this studentAssessment flag as an assessment result transferred from a previous presentation. Banked records are excluded from the early-submission exposure because they are not fresh submissions in the current presentation.

### date_submitted
Used to classify non-banked submissions through day 30. A submission is counted only when it is not earlier than the learner's recorded registration date.

## Landmark population

The analysis includes learners who:
1. registered by day 30;
2. did not unregister on or before day 30;
3. have observable withdrawal timing when final_result is Withdrawn.

Outcome follow-up is therefore after the end of the exposure-classification window.

## Provenance recorded by the runner

A successful run records:
- UCI dataset ID;
- DOI and reported license;
- canonical download URL;
- archive SHA-256;
- exact source tables;
- source registration count;
- landmark exclusions;
- banked submissions excluded;
- submissions before registration excluded.

## Missingness

The primary analysis uses complete cases for the frozen adjustment set. The generated evidence reports each covariate's missing count, the number excluded for any missing covariate, and the final complete-case sample.

Complete-case analysis can change the target population and may induce selection bias.

## License boundary

The repository's MIT license applies to repository code and original project materials. It does not relicense OULAD. Dataset use remains subject to the source dataset terms.

## Generalizability

OULAD represents historical Open University distance-learning contexts. Results from one landmarked module-presentation are not automatically transferable to other institutions, modalities, countries or present-day learners.
