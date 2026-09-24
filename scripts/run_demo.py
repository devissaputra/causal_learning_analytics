import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_learning_analytics.core import (
    analyze_ipw,
    causal_analysis_record,
)


treatment = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
outcome = [0.82, 0.55, 0.78, 0.60, 0.84, 0.52, 0.76, 0.61, 0.90, 0.56, 0.80, 0.59]
propensity = [0.58, 0.42, 0.46, 0.56, 0.50, 0.44, 0.44, 0.58, 0.60, 0.46, 0.48, 0.52]

covariates = {
    "baseline_score": [0.72, 0.65, 0.68, 0.71, 0.70, 0.64, 0.66, 0.72, 0.74, 0.67, 0.69, 0.70],
    "prior_engagement": [0.60, 0.54, 0.56, 0.61, 0.58, 0.52, 0.55, 0.62, 0.64, 0.56, 0.57, 0.59],
}

record = causal_analysis_record(
    treatment="received adaptive feedback intervention",
    outcome="normalized post-test score",
    covariates=["baseline_score", "prior_engagement"],
    propensity_source="synthetic externally supplied pre-treatment scores",
)

result = analyze_ipw(
    treatment,
    outcome,
    propensity,
    covariates=covariates,
)

print("Estimand:", record["estimand"])
print("Sample size:", result["sample_size"])
print("Treated / control:", result["treated_count"], "/", result["control_count"])
print(f"Raw mean difference: {result['raw_mean_difference']:.3f}")
print(f"IPW ATE (Horvitz-Thompson): {result['ipw_ate_ht']:.3f}")
print(f"IPW ATE (Hajek): {result['ipw_ate_hajek']:.3f}")
print(
    "95% bootstrap CI for Hajek ATE:",
    tuple(round(value, 3) for value in result["hajek_ate_ci"]),
)
print("Empirical common support:", result["common_support"]["common_support"])
print(
    "Fraction in common support:",
    round(result["common_support"]["overall_fraction_in_support"], 3),
)
print(
    "Weight ESS:",
    round(result["weight_diagnostics"]["overall_ess"], 3),
    "of",
    result["sample_size"],
)
print(
    "Maximum weight:",
    round(result["weight_diagnostics"]["max_weight"], 3),
)
print("Balance before / after weighting:")
for name in covariates:
    before = result["balance_before"][name]["smd"]
    after = result["balance_after"][name]["smd"]
    print(
        f"  - {name}: "
        f"{before:.3f} -> {after:.3f}"
    )
print("Analysis flags:", result["analysis_flags"])
print("Clipping sensitivity:")
for row in result["clipping_sensitivity"]:
    if row["status"] == "ok":
        print(
            f"  - clip={row['clip']}: "
            f"Hajek={row['ipw_ate_hajek']:.3f}, "
            f"max_weight={row['max_weight']:.3f}, "
            f"ESS={row['overall_ess']:.3f}"
        )
    else:
        print(f"  - clip={row['clip']}: {row['status']}")
print(
    "Note: these are synthetic observational data. "
    "The code does not verify exchangeability, consistency, positivity, "
    "no interference, or correct model specification."
)
