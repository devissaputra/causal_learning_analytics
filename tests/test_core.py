import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from causal_learning_analytics import core


class CoreTests(unittest.TestCase):
    def test_ipw_and_overlap(self):
        treatment = [1, 0, 1, 0]
        outcome = [1.0, 0.2, 0.8, 0.1]
        propensity = [0.6, 0.4, 0.7, 0.3]
        self.assertAlmostEqual(core.ipw_ate(treatment, outcome, propensity), 0.5833333333)
        self.assertEqual(core.overlap_fraction([0.2, 0.5, 0.95]), 2 / 3)

    def test_non_binary_treatment_is_rejected(self):
        with self.assertRaises(ValueError):
            core.ipw_ate([1, 0.2], [1, 0], [0.6, 0.4])


if __name__ == "__main__":
    unittest.main()
