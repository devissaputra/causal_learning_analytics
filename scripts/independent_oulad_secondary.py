#!/usr/bin/env python3
"""Independent, exploratory OULAD robustness audits; no individual-level exports.

Uses verified OULAD parser/cohort definitions from independent_oulad_audit.py
but computes new comparison groups, per-arm diagnostics and sensitivity.
"""
import json, sys, tempfile, pathlib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from independent_oulad_audit import acquire, raw_tables, build, fit, metrics, NUM, CAT, KEY

def diagnostic(df,p):
    t=df["exposed"].to_numpy().astype(bool)
    iw=np.where(t,1/p,1/(1-p))
    ow=np.where(t,1-p,p)
    out={}
    for key,w in (("ipw",iw),("overlap",ow)):
        group={}
        for lab,mask in (("early",t),("non_early",~t)):
            a=w[mask]
            group[lab]={"n":int(mask.sum()),"ess":float(a.sum()**2/(a*a).sum()),
                        "weight_max":float(a.max()),"weight_top5_share":float(np.sort(a)[-5:].sum()/a.sum())}
        out[key]=group
    def smds(weights):
        indicators=[]
        for col in NUM:
            indicators.append((col,df[col].to_numpy(dtype=float)))
        for col in CAT:
            dummies=pd.get_dummies(df[col],prefix=col)
            for lvl in dummies.columns:
                indicators.append((str(lvl),dummies[lvl].to_numpy(dtype=float)))
        answers={}
        for name,x in indicators:
            mean=[]
            variances=[]
            for mask in (t,~t):
                xx=x[mask]; ww=weights[mask]
                mu=np.average(xx,weights=ww)
                var=np.average((xx-mu)**2,weights=ww)
                mean.append(mu);variances.append(var)
            denom=np.sqrt((variances[0]+variances[1])/2)
            answers[name]=float((mean[0]-mean[1])/denom) if denom>1e-12 else None
        defined=[abs(v) for v in answers.values() if v is not None]
        return {"maximum_absolute_smd":max(defined) if defined else None,
                "n_above_0_1":sum(v is not None and abs(v)>0.1 for v in answers.values()),
                "undefined":sum(v is None for v in answers.values()),
                "n_covariate_indicators":len(answers)}
    out["balance"]={"unweighted":smds(np.ones(len(df))),
                    "ipw":smds(iw),"overlap":smds(ow)}
    return out

def alternate(df,C=1,region=True):
    cats=CAT if region else [x for x in CAT if x!="region"]
    mod=Pipeline([("prep",ColumnTransformer([
        ("num",StandardScaler(),NUM),("cat",OneHotEncoder(handle_unknown="ignore"),cats)])),
        ("logit",LogisticRegression(C=C,max_iter=4000,random_state=42))])
    t=df["exposed"].to_numpy()
    mod.fit(df[NUM+cats],t)
    p=mod.predict_proba(df[NUM+cats])[:,1]
    return {"metrics":metrics(df,p),"balance":diagnostic(df,p)["balance"]["ipw"]}

def late_never(df,tables,day=30):
    sub=tables["studentAssessment.csv"]
    a=tables["assessments.csv"]
    reg=tables["studentRegistration.csv"]
    sb=sub.merge(a[["id_assessment","code_module","code_presentation"]],
        on="id_assessment",validate="many_to_one")
    sb=sb.merge(reg[KEY+["date_registration","date_unregistration"]],
        on=KEY,validate="many_to_one")
    sd=pd.to_numeric(sb["date_submitted"],errors="coerce")
    rd=pd.to_numeric(sb["date_registration"],errors="coerce")
    ud=pd.to_numeric(sb["date_unregistration"],errors="coerce")
    bank=pd.to_numeric(sb["is_banked"],errors="coerce").fillna(0)
    valid=(bank==0)&(sd>day)&(sd>=rd)&(ud.isna() | (sd<=ud))
    later=sb.loc[valid,KEY].drop_duplicates().assign(later=1)
    unexposed=df.loc[df["exposed"]==0,KEY+["good"]].merge(later,on=KEY,how="left")
    unexposed["later"]=unexposed["later"].fillna(0)
    res={}
    for value,label in ((0,"no_recorded_later_submission"),(1,"recorded_later_submission")):
        f=unexposed.loc[unexposed["later"]==value]
        res[label]={"count":len(f),"favorable_n":int(f["good"].sum()),
                    "favorable_rate":float(f["good"].mean()) if len(f) else None}
    return {"warning":"Groups defined by FUTURE events after day 30; descriptive outcome stratification only, not covariates nor causal comparisons.",
            "groups":res}

def main():
    with tempfile.TemporaryDirectory(prefix="oulad-independent-extension-") as t:
        directory,digest,files=acquire(t)
        tables=raw_tables(directory)
        frame,flow=build(tables,30)
        p=fit(frame)
        combined={"source_archive_sha256":digest,"focal":{"flow":flow,"metrics":metrics(frame,p),
                    "diagnostics":diagnostic(frame,p),
                    "alternate_models":{
                        "strong_regularization_C_0_25":alternate(frame,C=.25),
                        "weak_regularization_C_4":alternate(frame,C=4),
                        "exclude_region_C_1":alternate(frame,region=False)},
                    "late_versus_never_description":late_never(frame,tables)}}
        # Evaluate support independently for each candidate; select by sample size, NOT outcome
        candidates=[]
        presentations=tables["studentInfo.csv"][["code_module","code_presentation"]].drop_duplicates()
        for _,row in presentations.iterrows():
            module=str(row["code_module"]);pres=str(row["code_presentation"])
            if module=="CCC" and pres=="2014J": continue
            f,selection=build(tables,30,module,pres)
            groups=f["exposed"].value_counts()
            if groups.get(0,0)>=30 and groups.get(1,0)>=30:
                candidates.append((len(f),module,pres,f,selection))
        candidates.sort(key=lambda x:(-x[0],x[1],x[2]))
        combined["other_presentation_selection"]={"rule":"three largest supported day-30 complete-case populations selected by counts and arm support, without looking at outcomes",
           "supported_candidates":len(candidates)}
        combined["other_presentations"]=[]
        for n,module,pres,f,selection in candidates[:3]:
            ps=fit(f)
            combined["other_presentations"].append({"module":module,"presentation":pres,"flow":selection,
                   "metrics":metrics(f,ps),"diagnostics":diagnostic(f,ps)})
        pathlib.Path("independent_secondary.json").write_text(json.dumps(combined,indent=2))
        print("INDEPENDENT_SECONDARY_SUMMARY",json.dumps({
            "day30_focal":combined["focal"]["metrics"],
            "day30_focal_diagnostics":combined["focal"]["diagnostics"],
            "alternate_model_estimates":{k:v["metrics"]["ipw"] for k,v in combined["focal"]["alternate_models"].items()},
            "descriptive_future_activity":combined["focal"]["late_versus_never_description"],
            "other_presentations":[{"module":i["module"],"presentation":i["presentation"],
                "n":i["metrics"]["n"],"control":i["metrics"]["control"],"ipw":i["metrics"]["ipw"],"overlap":i["metrics"]["overlap"],
                "ipw_ess":i["metrics"]["ipw_ess"]} for i in combined["other_presentations"]]
        },indent=2))
if __name__=="__main__": main()
