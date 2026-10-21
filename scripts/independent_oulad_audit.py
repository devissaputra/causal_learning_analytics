#!/usr/bin/env python3
"""Independent OULAD audit: original UCI bytes -> independently constructed cohort and estimates.

This program intentionally does not import the project's analysis modules.
No student-level raw records are checked into git or included in artifacts.
"""
import argparse, hashlib, json, os, platform, sys, tempfile, urllib.request, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

URL = "https://archive.ics.uci.edu/static/public/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset.zip"
EXPECTED_ARCHIVE_SHA = "f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4"
REQUIRED = ["studentInfo.csv", "studentRegistration.csv", "assessments.csv", "studentAssessment.csv"]
KEY = ["code_module", "code_presentation", "id_student"]
NUM = ["studied_credits", "num_of_prev_attempts", "date_registration"]
CAT = ["age_band", "highest_education", "imd_band", "disability", "gender", "region"]
FROZEN = {"n":1820,"exposed":1624,"control":196, "raw":0.3743,
          "ipw":0.38611041153085035, "overlap":0.3260659651759402}
def sha256(p):
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def acquire(folder):
    archive = Path(folder)/"oulad-original.zip"
    if not archive.exists():
        with urllib.request.urlopen(URL,timeout=300) as u,open(archive,"wb") as f:
            while True:
                b=u.read(1<<20)
                if not b: break
                f.write(b)
    digest=sha256(archive)
    if digest!=EXPECTED_ARCHIVE_SHA:
        raise RuntimeError("SOURCE CHECKSUM FAILURE: "+digest)
    out=Path(folder)/"csv"
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        names={Path(n).name:n for n in z.namelist() if not n.endswith("/")}
        for p in REQUIRED:
            if p not in names: raise RuntimeError("Missing original CSV "+p)
            (out/p).write_bytes(z.read(names[p]))
    return out, digest, {n:sha256(out/n) for n in REQUIRED}

def raw_tables(folder):
    return {p:pd.read_csv(folder/p) for p in REQUIRED}

def build(tables,day):
    inf=tables["studentInfo.csv"].copy()
    reg=tables["studentRegistration.csv"].copy()
    assess=tables["assessments.csv"]
    submission=tables["studentAssessment.csv"].copy()
    assert not inf.duplicated(KEY).any() and not reg.duplicated(KEY).any()
    assert not assess["id_assessment"].duplicated().any()
    reg["date_registration"]=pd.to_numeric(reg["date_registration"],errors="coerce")
    reg["date_unregistration"]=pd.to_numeric(reg["date_unregistration"],errors="coerce")
    submission=submission.merge(assess[["id_assessment","code_module","code_presentation"]],on="id_assessment",how="left",validate="many_to_one")
    submission=submission.merge(reg[KEY+["date_registration"]],on=KEY,how="left",validate="many_to_one")
    times=pd.to_numeric(submission["date_submitted"],errors="coerce")
    bank=pd.to_numeric(submission["is_banked"],errors="coerce").fillna(0)
    valid=(bank==0)&(times<=day)&(times>=submission["date_registration"])&submission["date_registration"].notna()
    e=submission.loc[valid,KEY].drop_duplicates().assign(exposed=1)
    joined=inf.merge(reg[KEY+["date_registration","date_unregistration"]],on=KEY,how="left",validate="one_to_one")
    joined=joined.merge(e,on=KEY,how="left",validate="one_to_one")
    joined["exposed"]=joined["exposed"].fillna(0).astype(int)
    joined["good"]=joined["final_result"].isin(["Pass","Distinction"]).astype(int)
    active=(joined["date_registration"].notna() & (joined["date_registration"]<=day) &
        (((joined["final_result"]!="Withdrawn")&joined["date_unregistration"].isna()) |
            (joined["date_unregistration"]>day)))
    eligible=joined.loc[active & (joined["code_module"]=="CCC") & (joined["code_presentation"]=="2014J")].copy()
    step={"enrolled_any_module":len(joined),"eligible_any_module":int(active.sum()),
         "focal_before_complete_case":len(eligible)}
    for c in CAT: eligible[c]=eligible[c].replace({"?":np.nan,"":np.nan,"nan":np.nan,"None":np.nan})
    for c in NUM: eligible[c]=pd.to_numeric(eligible[c],errors="coerce")
    cc=eligible.loc[~eligible[CAT+NUM].isna().any(axis=1)].copy()
    step["after_complete_case"]=len(cc)
    bad_rows=0
    while True:
        drop=pd.Series(False,index=cc.index)
        for c in CAT:
            tab=pd.crosstab(cc[c],cc["exposed"])
            bad=[level for level,row in tab.iterrows() if row.get(0,0)==0 or row.get(1,0)==0]
            drop|=cc[c].isin(bad)
        if not drop.any(): break
        bad_rows+=int(drop.sum())
        cc=cc.loc[~drop].copy()
    step["unsupported_exclusions"]=bad_rows
    step["final_n"]=len(cc)
    return cc,step

def fit(df):
    pre=ColumnTransformer([
        ("num",Pipeline([("scale",StandardScaler())]),NUM),
        ("cat",OneHotEncoder(handle_unknown="ignore"),CAT)
    ])
    model=Pipeline([("preprocess",pre),("logit",LogisticRegression(max_iter=4000,random_state=42,C=1.0))])
    t=df["exposed"].astype(int).to_numpy()
    model.fit(df[NUM+CAT],t)
    return np.asarray(model.predict_proba(df[NUM+CAT])[:,1],float)

def metrics(df,p):
    t=df["exposed"].astype(int).to_numpy()
    y=df["good"].astype(float).to_numpy()
    if min(t.sum(),len(t)-t.sum())<2: raise ValueError("No control")
    iw=np.where(t==1,1/p,1/(1-p))
    ow=np.where(t==1,1-p,p)
    def delta(w):
        a=np.sum(w[t==1]*y[t==1])/np.sum(w[t==1])
        b=np.sum(w[t==0]*y[t==0])/np.sum(w[t==0])
        return float(a-b)
    def ess(w): return float(np.sum(w)**2/np.sum(w*w))
    return {"n":len(df),"exposed":int(t.sum()),"control":int((1-t).sum()),
        "raw":float(y[t==1].mean()-y[t==0].mean()),
        "ipw":delta(iw),"overlap":delta(ow),
        "exposed_outcome_mean":float(y[t==1].mean()),
        "control_outcome_mean":float(y[t==0].mean()),
        "ipw_max_weight":float(iw.max()),"ipw_ess":ess(iw),
        "overlap_ess":ess(ow),"propensity_min":float(p.min()),"propensity_max":float(p.max())}

def bootstrap(df,n=250,seed=20260925):
    rng=np.random.default_rng(seed)
    ipw=[];overlap=[]
    for i in range(n):
        draw=df.iloc[rng.integers(0,len(df),len(df))].reset_index(drop=True)
        if draw["exposed"].nunique()<2:continue
        try:
            out=metrics(draw,fit(draw))
            ipw.append(out["ipw"]);overlap.append(out["overlap"])
        except Exception:continue
    if len(ipw)<n*0.9:raise RuntimeError("Insufficient bootstrap replicates")
    return {"resamples_requested":n,"resamples_valid":len(ipw),
        "ipw_95ci":np.quantile(ipw,[0.025,0.975]).tolist(),
        "overlap_95ci":np.quantile(overlap,[0.025,0.975]).tolist()}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",default=None)
    parser.add_argument("--out",default="independent_verification.json")
    parser.add_argument("--boots",type=int,default=1000)
    a=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="oulad-audit-") as temp:
        if a.data_dir:
            data_dir=Path(a.data_dir); archive_sha=None
            csv_sha={n:sha256(data_dir/n) for n in REQUIRED}
        else:data_dir,archive_sha,csv_sha=acquire(temp)
        tables=raw_tables(data_dir)
        result={"source":URL,"archive_sha256":archive_sha,"archive_hash_matches_expected":archive_sha==EXPECTED_ARCHIVE_SHA if archive_sha else None,
            "csv_sha256":csv_sha, "software":{"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__},
            "days":{},"original_numerical_reconciliation":{}}
        for day in [14,30,45]:
            df,step=build(tables,day)
            current={"flow":step}
            if min(df["exposed"].sum(),len(df)-df["exposed"].sum())>=30:
                current["metrics"]=metrics(df,fit(df))
                if day==30:current["bootstrap"]=bootstrap(df,a.boots)
            else:current["status"]="INSUFFICIENT_EXPOSURE_SUPPORT"
            result["days"][str(day)]=current
        observed=result["days"]["30"].get("metrics",{})
        for k,expected in FROZEN.items():
            actual=observed.get(k)
            tolerance=0 if isinstance(expected,int) else (1e-4 if k=="raw" else 1e-5)
            result["original_numerical_reconciliation"][k]={"expected":expected,
                "actual":actual,"absolute_error":abs(actual-expected) if actual is not None else None,
                "match":actual is not None and abs(actual-expected)<=tolerance}
        result["independent_replication_passed"]=all(x["match"] for x in result["original_numerical_reconciliation"].values())
        Path(a.out).write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
        print("INDEPENDENT_AUDIT_OUTPUT",json.dumps({"archive_sha256":archive_sha,
             "reconciles":result["independent_replication_passed"],
             "focal":observed,"verification":result["original_numerical_reconciliation"]},indent=2))
        if not result["independent_replication_passed"]:sys.exit(3)
if __name__=="__main__":main()
