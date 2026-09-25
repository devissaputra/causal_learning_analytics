import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from causal_learning_analytics.core import analyze_ipw

print("Synthetic software fixture only; not an empirical result.")
treatment=[1,1,1,0,0,0]
outcome=[.9,.8,.7,.4,.3,.2]
propensity=[.6,.7,.65,.35,.3,.4]
covariates={"baseline":[.7,.8,.75,.3,.2,.35]}
print(json.dumps(analyze_ipw(treatment,outcome,propensity,covariates=covariates,bootstrap_iterations=200),indent=2))
