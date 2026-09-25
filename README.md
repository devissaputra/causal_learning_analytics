# Causal Learning Analytics — Research Bundle

[![CI](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/ci.yml)
[![Empirical Study](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/empirical.yml/badge.svg)](https://github.com/devissaputra/causal_learning_analytics/actions/workflows/empirical.yml)

**Research Bundle · AI in Education · observational causal inference and diagnostics**

This repository combines a transparent inverse-probability-weighting engine with an empirical adapter for the **Open University Learning Analytics Dataset (OULAD)**. The old 12-row synthetic example is retained only as a software smoke test; it is no longer the research evidence.

## Empirical question

> Within one OULAD module-presentation cohort, what is the adjusted association between submitting at least one assessment by day 30 and a favorable final course result after weighting on measured pre-treatment characteristics?

The wording is intentionally cautious. The analysis estimates an ATE-style weighted contrast under explicit identification assumptions. It does **not** establish that early submission causes success.

## Real dataset

OULAD is an anonymized public learning-analytics dataset from The Open University.

The research adapter uses:

- `studentInfo.csv`
- `studentRegistration.csv`
- `assessments.csv`
- `studentAssessment.csv`

The original release contains 32,593 student registrations across 22 module presentations and is linked to the Scientific Data paper by Kuzilek, Hlosta & Zdrahal (2017), DOI 10.1038/sdata.2017.171.

The empirical runner retrieves the UCI-hosted OULAD archive (dataset 349), records the archive SHA-256, and extracts only the four required CSV files into a gitignored cache. UCI reports DOI `10.24432/C5KK69` and CC BY 4.0. Raw files are **not** committed. See [DATA.md](DATA.md) and [docs/dataset_card.md](docs/dataset_card.md).

## Target-trial-style declaration

### Population
One module-presentation cohort selected before outcome estimation. By default, the runner chooses the largest cohort with sufficient treated and control observations.

### Exposure
`treatment = 1` when the learner submitted at least one recorded assessment on or before presentation day 30.

### Outcome
`1` for `Pass` or `Distinction`; `0` for `Fail` or `Withdrawn`.

### Measured pre-treatment covariates
The default adapter encodes only information available at registration or before the exposure window:

- studied credits;
- number of previous attempts;
- registration timing;
- age band;
- highest prior education;
- deprivation-band midpoint when available;
- disability indicator;
- gender indicator.

No assessment score or post-day-30 behavior is included in the propensity model.

## Analysis path

1. Load original OULAD CSV files.
2. Build learner-module-presentation records.
3. Freeze the cohort and exposure definition.
4. Encode pre-treatment covariates.
5. Estimate logistic propensity scores.
6. Inspect empirical common support.
7. Compute ATE inverse-probability weights.
8. Compare raw and weighted outcome contrasts.
9. Inspect covariate balance before and after weighting.
10. Report effective sample size and extreme weights.
11. Bootstrap the Hájek estimate conditional on fitted propensity scores.
12. Preserve `causal_assumptions_unverified` and any additional review flags.

## Run the real study

The default command downloads the external UCI archive automatically:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_oulad_study.py
```

A local OULAD extraction can still be supplied with `--data-dir /path/to/oulad`. To freeze a particular cohort, add `--module BBB --presentation 2013J`.

## What makes this a Research Bundle

- real educational data;
- explicit estimand/exposure/outcome timing;
- pre-treatment adjustment boundary;
- propensity provenance;
- overlap and weight diagnostics;
- before/after balance;
- raw versus adjusted estimates;
- uncertainty and clipping-sensitivity support;
- explicit causal assumptions and non-claims;
- tests/CI and paper-ready research protocol.

## Critical interpretation boundary

An IPW estimate is not automatically causal. Unmeasured motivation, prior achievement, course-specific factors, access constraints and other confounders may affect both early submission and final result. This bundle is designed to make those assumptions visible rather than bury them behind one effect number.
