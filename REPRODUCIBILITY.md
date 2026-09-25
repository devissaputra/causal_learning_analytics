# Reproducibility Protocol

## Development environment

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python scripts/run_oulad_study.py

## Professor-facing reproduction environment

Use Python 3.11 and the checked-in top-level pins:

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-repro.txt
    python -m unittest discover -s tests -v
    python scripts/run_oulad_study.py

The empirical GitHub Actions workflow runs the test suite before the real-data study.

## Frozen data path

The runner retrieves UCI OULAD dataset 349, stores the archive in gitignored data/cache/, records the archive SHA-256, and extracts only:

- studentInfo.csv;
- studentRegistration.csv;
- assessments.csv;
- studentAssessment.csv.

Raw learner data are not committed.

## Frozen design path

The runner:
1. validates unique learner-registration keys;
2. excludes banked assessment results from exposure construction;
3. excludes submissions predating registration;
4. establishes day-30 landmark eligibility;
5. selects exactly one module-presentation;
6. records complete-case exclusions;
7. fits the frozen propensity specification;
8. generates diagnostics, effect estimates, full-refit bootstrap uncertainty and sensitivity analyses.

## Repeated computation

The primary bootstrap seed is stored in generated metrics. Propensity-model fitting uses a fixed random state. The archive bytes, environment versions and generated results are recorded.

## Generated evidence

- results/oulad_metrics.json;
- results/summary.md;
- paper/results.md;
- results/figures/.

## Reproduction boundary

Exact floating-point output can vary with Python, numerical libraries, operating system and low-level linear algebra. requirements-repro.txt pins the top-level empirical packages used by the research workflow, while generated metrics record the actual runtime versions.

Reproduction of the numbers does not independently validate the causal identification assumptions.
