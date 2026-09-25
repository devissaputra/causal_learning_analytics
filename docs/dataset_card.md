# Dataset Card — OULAD Landmark Study

## Source

Open University Learning Analytics Dataset (OULAD)  
Reference: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). *Open University Learning Analytics dataset*. Scientific Data, 4, 170171. https://doi.org/10.1038/sdata.2017.171

The empirical adapter retrieves the UCI representation (dataset 349) and records the exact downloaded archive SHA-256.

## Scale and structure

OULAD contains 32,593 student registrations across 22 module presentations, linked demographics, registration timing, assessment records and VLE activity.

## Tables used

- studentInfo: baseline learner/context fields and final result;
- studentRegistration: registration and unregistration timing;
- assessments: maps assessment identifiers to module-presentations;
- studentAssessment: submission dates, banked-transfer flag and scores.

Scores are not used in the treatment, adjustment set or outcome.

## Study unit

One learner-registration triplet:
(code_module, code_presentation, id_student).

The runner rejects duplicate learner-registration keys in studentInfo or studentRegistration.

## Landmark eligibility

Presentation day 30 is the analysis landmark. Learners must be registered by that day and must not have unregistered on or before that day.

For learners whose final_result is Withdrawn, withdrawal timing must be observed and after the landmark.

## Exposure

At least one non-banked assessment submitted after registration and by day 30.

The is_banked flag is explicitly checked because transferred results from prior presentations are not treated as current-presentation early submissions.

## Outcome

Pass/Distinction versus Fail or withdrawal after day 30.

## Baseline variables

Numeric:
- studied credits;
- previous attempts;
- registration date.

Categorical:
- age band;
- highest education;
- deprivation band;
- disability;
- gender;
- region.

These are encoded without turning nominal categories into arbitrary numeric distances.

## Privacy

OULAD is anonymized public educational research data. Do not attempt re-identification or join student IDs to external identities.

## Validity boundary

Landmarking solves a specific temporal alignment problem but changes the target population to learners who remain registered to day 30. That selection is part of the estimand and must not be hidden.

The dataset does not fully measure motivation, prior achievement, employment constraints, access or all course-context causes of both submission timing and outcome.
