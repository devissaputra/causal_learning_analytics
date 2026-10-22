#!/usr/bin/env python3
"""Exploratory independent OULAD 2013-14 cross-presentation bootstrap.

Three presentations were previously selected by sample size and exposure support
without inspecting their outcome contrasts. This code does NOT perform causal
identification or reproduce a preregistered trial. Raw individual-level records
are never committed or uploaded.
"""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import numpy as np
from independent_oulad_audit import (
    acquire, raw_tables, build, fit, metrics, bootstrap, EXPECTED_ARCHIVE_SHA,
)
from independent_oulad_secondary import diagnostic

PRESENTATIONS = [
    ("FFF","2013J",1867,178,0.5032),
    ("BBB","2013J",1804,217,0.4768),
    ("BBB","2014J",1752,96,0.5610),
]
N_BOOT=1000
SEED=20261022
def main():
    with tempfile.TemporaryDirectory(prefix="oulad-paper2-final-") as temp:
        source,sha,hashes=acquire(temp)
        if sha!=EXPECTED_ARCHIVE_SHA:
            raise AssertionError("Original UCI archive mismatch")
        tables=raw_tables(source)
        result={
            "status":"complete_independent_exploratory_cross_presentation_bootstrap",
            "source_archive_sha256":sha,
            "design":"After-the-fact selected three largest supported presentations; exploratory",
            "bootstrap_method":"Student-level independent full-refit nonparametric bootstrap; cohort and outcome models rebuilt per resample",
            "bootstrap_draws_requested":N_BOOT,
            "presentation_selection":"The three largest previously identified day-30 populations with >=30 learners in both exposure groups; selected outcome-blind in earlier exploratory audit",
            "warning":"All quantities are historical observational associations, not intervention effects. Bootstrap intervals do not account for hidden confounders or selection bias.",
            "presentations":[],
        }
        for k,(module,term,expected_n,expected_unexposed,expected_ipw) in enumerate(PRESENTATIONS):
            df,flow=build(tables,30,module,term)
            if len(df)!=expected_n or int((df["exposed"]==0).sum())!=expected_unexposed:
                raise AssertionError("Selection cohort changed for %s %s"%(module,term))
            probabilities=fit(df)
            met=metrics(df,probabilities)
            if abs(met["ipw"]-expected_ipw)>=0.0001:
                raise AssertionError("Point estimate no longer matches frozen prior analysis")
            diag=diagnostic(df,probabilities)
            boot=bootstrap(df,n=N_BOOT,seed=SEED+100*k)
            if boot["resamples_valid"]<950:
                raise AssertionError("Insufficient full-refit resamples")
            result["presentations"].append({
                "module":module,"presentation":term,"flow":flow,
                "metrics":met,"diagnostics":diag,"bootstrap":boot,
                "ipw_interval_contains_zero":bool(boot["ipw_95ci"][0]<=0<=boot["ipw_95ci"][1]),
                "overlap_interval_contains_zero":bool(boot["overlap_95ci"][0]<=0<=boot["overlap_95ci"][1]),
                "note":"Within-presentation sampling confidence intervals, NOT causal confidence intervals",
            })
            print(json.dumps({"presentation":module+"/"+term,"n":len(df),"ipw":met["ipw"],"ipw_95ci":boot["ipw_95ci"],"overlap_95ci":boot["overlap_95ci"]}),flush=True)
        Path("results").mkdir(exist_ok=True)
        out=Path("results/paper2_cross_presentation_bootstrap_20261022.json")
        out.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
        print("SAVED",out,flush=True)
if __name__=="__main__": main()
