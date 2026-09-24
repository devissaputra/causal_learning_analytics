import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from causal_learning_analytics.core import ipw_ate, overlap_fraction

treatment = [1, 0, 1, 0]
outcome = [1.0, 0.2, 0.8, 0.1]
propensity = [0.6, 0.4, 0.7, 0.3]
print(f"IPW treatment effect estimate: {ipw_ate(treatment, outcome, propensity):.3f}")
print(f"Propensity overlap fraction: {overlap_fraction(propensity):.2f}")
