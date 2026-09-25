# Data Policy

The empirical study retrieves real OULAD source tables at run time. Raw learner data are not committed to this repository.

The day-30 research path uses:
- studentInfo.csv;
- studentRegistration.csv;
- assessments.csv;
- studentAssessment.csv.

The adapter validates unique learner-registration keys, uses date_registration and date_unregistration to establish landmark eligibility, and excludes is_banked assessment transfers from exposure classification.

data/cache/ is gitignored.

See:
- ../DATA.md for provenance and temporal-field definitions;
- ../docs/dataset_card.md for study-unit and validity notes;
- ../docs/causal_dag.md for adjustment rationale;
- ../REPRODUCIBILITY.md for execution instructions.
