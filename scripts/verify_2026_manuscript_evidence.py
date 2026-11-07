#!/usr/bin/env python3
"""Read-only check of OULAD manuscript metrics and distinct bootstrap procedures.
Not a rerun of the propensity model, data pipeline or independent replication.
"""
import json
from pathlib import Path
r = json.loads((Path(__file__).resolve().parents[1] / "results/oulad_metrics.json").read_text())
assert r["sample_size"] == 1820
assert r["treated_count"] == 1624
assert r["control_count"] == 196
assert r["landmark_day"] == 30
def close(actual, expected, tolerance=0.00006):
    assert abs(actual - expected) <= tolerance, (actual, expected)
close(r["raw_mean_difference"], 0.3743)
close(r["ipw_ate_hajek"], 0.3861)
primary = r["full_refit_bootstrap"]
assert primary["iterations_valid"] == 1000
assert "refit" in primary["method"].lower()
for actual, expected in zip(primary["interval"], [0.3242,0.4447]):
    close(actual, expected)
for actual, expected in zip(r["hajek_ate_ci"], [0.3267,0.4446]):
    close(actual, expected)
assert primary["interval"] != r["hajek_ate_ci"]
close(r["overlap_weighting_sensitivity"]["estimate"], 0.3261)
for actual, expected in zip(primary["overlap_weighting_interval"], [0.2667,0.3870]):
    close(actual, expected)
print("PASS: 2026 manuscript's primary full-refit and secondary fixed-propensity intervals are correctly distinguished.")
print("LIMITATION: this does not independently reproduce raw-data computations or causal identification.")
