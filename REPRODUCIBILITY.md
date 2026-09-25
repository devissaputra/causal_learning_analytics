# Reproducibility Protocol

## Install and test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Full external-data run

```bash
python scripts/run_oulad_study.py
```

The default run retrieves UCI OULAD dataset 349, records the archive SHA-256, extracts only the required tables, selects the largest eligible module-presentation cohort, fits the frozen propensity model, runs IPW diagnostics, and writes generated evidence.

A local source can be supplied with `--data-dir`. A particular cohort can be frozen with `--module` and `--presentation`.

## Generated evidence

- `results/oulad_metrics.json`
- `results/summary.md`
- `paper/results.md`

## Reproduction notes

The source archive hash is the primary data-integrity check. Exact floating-point values can vary slightly across numerical-library versions. The design choices and random seeds are kept in code and should be changed only as an explicit protocol revision.
