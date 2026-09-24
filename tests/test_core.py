import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from causal_learning_analytics import core


TREATMENT = [1, 0, 1, 0, 1, 0, 1, 0]
OUTCOME = [0.82, 0.55, 0.78, 0.52, 0.91, 0.61, 0.85, 0.58]
PROPENSITY = [0.62, 0.38, 0.58, 0.42, 0.66, 0.35, 0.55, 0.45]
COVARIATES = {
    "baseline_score": [0.72, 0.68, 0.70, 0.65, 0.74, 0.67, 0.69, 0.66],
    "prior_engagement": [0.60, 0.55, 0.58, 0.52, 0.63, 0.54, 0.57, 0.53],
}


class CoreTests(unittest.TestCase):
    def test_raw_mean_difference(self):
        result = core.raw_mean_difference(TREATMENT, OUTCOME)
        self.assertGreater(result, 0)

    def test_ht_ipw_matches_manual_formula(self):
        expected = sum(
            (t * y / p) - ((1 - t) * y / (1 - p))
            for t, y, p in zip(TREATMENT, OUTCOME, PROPENSITY)
        ) / len(TREATMENT)
        self.assertAlmostEqual(
            core.ipw_ate(TREATMENT, OUTCOME, PROPENSITY),
            expected,
        )

    def test_hajek_ipw_is_finite(self):
        result = core.ipw_ate(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            normalized=True,
        )
        self.assertTrue(math.isfinite(result))

    def test_treatment_boolean_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, False], [1.0, 0.0], [0.6, 0.4])

    def test_non_binary_treatment_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 0.2], [1.0, 0.0], [0.6, 0.4])

    def test_missing_treatment_group_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 1], [1.0, 0.8], [0.6, 0.7])

    def test_non_finite_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 0], [1.0, math.nan], [0.6, 0.4])

    def test_propensity_outside_unit_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 0], [1.0, 0.0], [1.2, 0.4])

    def test_endpoint_propensity_requires_explicit_clipping(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 0], [1.0, 0.0], [1.0, 0.0])

    def test_explicit_clipping_is_reported(self):
        info = core.ipw_weights(
            [1, 0],
            [1.0, 0.0],
            clip=0.05,
        )
        self.assertEqual(info["clipped_count"], 2)
        self.assertEqual(info["propensity_used"], [0.95, 0.05])

    def test_common_support_uses_both_groups(self):
        result = core.common_support(
            [1, 1, 0, 0],
            [0.4, 0.8, 0.2, 0.6],
        )
        self.assertEqual(result["treated_range"], (0.4, 0.8))
        self.assertEqual(result["control_range"], (0.2, 0.6))
        self.assertEqual(result["common_support"], (0.4, 0.6))

    def test_common_support_detects_no_overlap(self):
        result = core.common_support(
            [1, 1, 0, 0],
            [0.8, 0.9, 0.1, 0.2],
        )
        self.assertIsNone(result["common_support"])
        self.assertEqual(result["overall_fraction_in_support"], 0.0)

    def test_overlap_fraction_uses_empirical_common_support(self):
        result = core.overlap_fraction(
            [1, 1, 0, 0],
            [0.4, 0.8, 0.2, 0.6],
        )
        self.assertEqual(result, 0.5)

    def test_unweighted_smd_is_positive(self):
        result = core.standardized_mean_difference(
            TREATMENT,
            COVARIATES["baseline_score"],
        )
        self.assertIsNotNone(result)

    def test_zero_variance_smd_is_not_estimable(self):
        result = core.standardized_mean_difference(
            [1, 1, 0, 0],
            [10.0, 10.0, 5.0, 5.0],
        )
        self.assertIsNone(result)

    def test_smd_requires_two_observations_per_group_for_scale(self):
        result = core.standardized_mean_difference(
            [1, 0, 0],
            [1.0, 0.0, 0.5],
        )
        self.assertIsNone(result)

    def test_weighted_smd_accepts_positive_weights(self):
        weights = core.ipw_weights(TREATMENT, PROPENSITY)["weights"]
        result = core.standardized_mean_difference(
            TREATMENT,
            COVARIATES["baseline_score"],
            weights=weights,
        )
        self.assertIsNotNone(result)

    def test_covariate_balance_reports_each_covariate(self):
        result = core.covariate_balance(TREATMENT, COVARIATES)
        self.assertEqual(
            set(result),
            {"baseline_score", "prior_engagement"},
        )

    def test_effective_sample_size_is_bounded_by_n(self):
        weights = [1.0, 2.0, 1.0, 2.0]
        ess = core.effective_sample_size(weights)
        self.assertLessEqual(ess, len(weights))
        self.assertGreater(ess, 0)

    def test_weight_diagnostics_include_group_ess(self):
        weights = core.ipw_weights(TREATMENT, PROPENSITY)["weights"]
        result = core.weight_diagnostics(TREATMENT, weights)
        self.assertGreater(result["treated_ess"], 0)
        self.assertGreater(result["control_ess"], 0)
        self.assertGreaterEqual(result["max_weight"], result["min_weight"])

    def test_bootstrap_ci_is_reproducible(self):
        first = core.bootstrap_ipw_ci(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            iterations=400,
            seed=7,
        )
        second = core.bootstrap_ipw_ci(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            iterations=400,
            seed=7,
        )
        self.assertEqual(first, second)

    def test_bootstrap_ci_orders_bounds(self):
        low, high = core.bootstrap_ipw_ci(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            iterations=400,
            seed=7,
        )
        self.assertLessEqual(low, high)

    def test_causal_analysis_record_declares_ate(self):
        record = core.causal_analysis_record(
            treatment="received adaptive feedback",
            outcome="post-test score",
            covariates=["baseline score", "prior engagement"],
            propensity_source="pre-treatment logistic model",
        )
        self.assertEqual(record["estimand"], "ATE")
        self.assertIn("positivity", record["assumptions"])

    def test_causal_analysis_record_rejects_other_estimands(self):
        with self.assertRaises(ValueError):
            core.causal_analysis_record(
                estimand="ATT",
                treatment="treatment",
                outcome="outcome",
                covariates=["baseline"],
                propensity_source="model",
            )

    def test_integrated_analysis_returns_raw_and_adjusted_effects(self):
        result = core.analyze_ipw(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            covariates=COVARIATES,
            bootstrap_iterations=400,
        )
        self.assertIn("raw_mean_difference", result)
        self.assertIn("ipw_ate_ht", result)
        self.assertIn("ipw_ate_hajek", result)
        self.assertEqual(result["estimand"], "ATE")

    def test_integrated_analysis_reports_before_after_balance(self):
        result = core.analyze_ipw(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            covariates=COVARIATES,
            bootstrap_iterations=400,
        )
        self.assertIn("baseline_score", result["balance_before"])
        self.assertIn("baseline_score", result["balance_after"])

    def test_integrated_analysis_reports_ess_and_support(self):
        result = core.analyze_ipw(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            covariates=COVARIATES,
            bootstrap_iterations=400,
        )
        self.assertIn("overall_ess", result["weight_diagnostics"])
        self.assertIn(
            "overall_fraction_in_support",
            result["common_support"],
        )

    def test_integrated_analysis_always_flags_unverified_assumptions(self):
        result = core.analyze_ipw(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
            covariates=COVARIATES,
            bootstrap_iterations=400,
        )
        self.assertIn(
            "causal_assumptions_unverified",
            result["analysis_flags"],
        )

    def test_integrated_analysis_flags_poor_common_support(self):
        result = core.analyze_ipw(
            [1, 1, 0, 0],
            [1.0, 0.9, 0.2, 0.1],
            [0.9, 0.8, 0.2, 0.1],
            covariates={"baseline": [0.7, 0.6, 0.3, 0.2]},
            bootstrap_iterations=400,
        )
        self.assertIn("poor_common_support", result["analysis_flags"])

    def test_integrated_analysis_flags_clipping_when_used(self):
        result = core.analyze_ipw(
            [1, 1, 0, 0],
            [1.0, 0.9, 0.2, 0.1],
            [1.0, 0.8, 0.2, 0.0],
            covariates={"baseline": [0.7, 0.6, 0.3, 0.2]},
            clip=0.05,
            bootstrap_iterations=400,
        )
        self.assertIn("positivity_violation", result["analysis_flags"])
        self.assertIn("propensity_clipping_used", result["analysis_flags"])

    def test_integrated_analysis_flags_post_weight_balance_problem(self):
        result = core.analyze_ipw(
            [1, 1, 0, 0],
            [1.0, 0.9, 0.4, 0.3],
            [0.6, 0.65, 0.4, 0.35],
            covariates={"baseline": [10.0, 11.0, 0.0, 1.0]},
            balance_threshold=0.1,
            bootstrap_iterations=400,
        )
        self.assertIn(
            "post_weight_balance_problem",
            result["analysis_flags"],
        )

    def test_clipping_sensitivity_reports_multiple_specifications(self):
        result = core.clipping_sensitivity(
            TREATMENT,
            OUTCOME,
            PROPENSITY,
        )
        self.assertEqual(len(result), 5)
        self.assertTrue(all("status" in row for row in result))
        self.assertTrue(any(row["clip"] == 0.05 for row in result))

    def test_clipping_sensitivity_exposes_endpoint_failure_without_clip(self):
        result = core.clipping_sensitivity(
            [1, 1, 0, 0],
            [1.0, 0.9, 0.2, 0.1],
            [1.0, 0.8, 0.2, 0.0],
        )
        untrimmed = next(row for row in result if row["clip"] is None)
        self.assertEqual(untrimmed["status"], "not_estimable")

    def test_fit_propensity_logistic_returns_scores(self):
        result = core.fit_propensity_logistic(
            TREATMENT,
            COVARIATES,
            l2=0.1,
        )
        self.assertEqual(len(result["scores"]), len(TREATMENT))
        self.assertTrue(all(0 < value < 1 for value in result["scores"]))
        self.assertIn("baseline_score", result["standardized_coefficients"])

    def test_fit_propensity_logistic_rejects_zero_variance_covariate(self):
        with self.assertRaises(ValueError):
            core.fit_propensity_logistic(
                TREATMENT,
                {"constant": [1.0] * len(TREATMENT)},
            )

    def test_fit_propensity_logistic_is_deterministic(self):
        first = core.fit_propensity_logistic(
            TREATMENT,
            COVARIATES,
            l2=0.1,
        )
        second = core.fit_propensity_logistic(
            TREATMENT,
            COVARIATES,
            l2=0.1,
        )
        self.assertEqual(first["scores"], second["scores"])


if __name__ == "__main__":
    unittest.main()
