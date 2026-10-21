#!/usr/bin/env python3
"""Audit selection missingness on original OULAD; aggregate-only output."""
import json, tempfile
import numpy as np,pandas as pd
from independent_oulad_audit import acquire,raw_tables,KEY,CAT,NUM,fit,metrics,build
def group_summ(df):
    out={"n":int(len(df)),"exposed":int(df.exposed.sum()),"non_early":int((1-df.exposed).sum()),"favorable":int(df.good.sum())}
    for flag,label in [(1,"early"),(0,"not_early")]:
        arm=df[df.exposed==flag]
        out[label]={"n":int(len(arm)),"favorable":int(arm.good.sum()),
                    "rate":float(arm.good.mean()) if len(arm) else None}
    return out
def main():
 with tempfile.TemporaryDirectory() as folder:
    loc,digest,_=acquire(folder)
    tb=raw_tables(loc)
    si=tb["studentInfo.csv"]
    sr=tb["studentRegistration.csv"].copy()
    sa=tb["studentAssessment.csv"].copy()
    a=tb["assessments.csv"]
    sr["date_registration"]=pd.to_numeric(sr["date_registration"],errors="coerce")
    sr["date_unregistration"]=pd.to_numeric(sr["date_unregistration"],errors="coerce")
    sa=sa.merge(a[["id_assessment","code_module","code_presentation"]],on="id_assessment",validate="many_to_one")
    sa=sa.merge(sr[KEY+["date_registration"]],on=KEY,validate="many_to_one")
    submitted=pd.to_numeric(sa["date_submitted"],errors="coerce")
    valid=(pd.to_numeric(sa["is_banked"],errors="coerce").fillna(0)==0)&(submitted<=30)&(submitted>=sa["date_registration"])&sa.date_registration.notna()
    early=sa.loc[valid,KEY].drop_duplicates().assign(exposed=1)
    joined=si.merge(sr[KEY+["date_registration","date_unregistration"]],on=KEY,how="left",validate="one_to_one").merge(early,on=KEY,how="left")
    joined["exposed"]=joined.exposed.fillna(0).astype(int)
    joined["good"]=joined.final_result.isin(["Pass","Distinction"]).astype(int)
    active=joined.date_registration.notna() & (joined.date_registration<=30) & (((joined.final_result!="Withdrawn") & joined.date_unregistration.isna()) | (joined.date_unregistration>30))
    cohort=joined.loc[active & (joined.code_module=="CCC") & (joined.code_presentation=="2014J")].copy()
    for c in CAT:cohort[c]=cohort[c].replace({"?":np.nan,"":np.nan,"nan":np.nan,"None":np.nan})
    for c in NUM:cohort[c]=pd.to_numeric(cohort[c],errors="coerce")
    missing=cohort[CAT+NUM].isna().any(axis=1)
    cc=cohort.loc[~missing].copy()
    supported,flow=build(tb,30)
    keep_keys=pd.MultiIndex.from_frame(supported[KEY])
    support_index=pd.MultiIndex.from_frame(cc[KEY])
    unsupported=cc.loc[~support_index.isin(keep_keys)].copy()
    comp={"original_archive_sha256":digest,
          "focal_eligible":group_summ(cohort),
          "missing_covariate_exclusions":group_summ(cohort.loc[missing]),
          "complete_case":group_summ(cc),
          "empirical_support_exclusions":group_summ(unsupported),
          "final_analysis":group_summ(supported)}
    assert len(cohort)==1983 and int(missing.sum())==133 and len(unsupported)==30 and len(supported)==1820
    assert group_summ(supported)["exposed"]==1624
    pathlib.Path("independent_exclusions.json").write_text(json.dumps(comp,indent=2))
    print("EXCLUSIONS_AUDIT",json.dumps(comp,indent=2))
if __name__=="__main__":
 import pathlib
 main()
