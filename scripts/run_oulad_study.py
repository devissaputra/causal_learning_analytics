import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from causal_learning_analytics.core import analyze_ipw

KEY=["code_module","code_presentation","id_student"]
AGE={"0-35":0.0,"35-55":1.0,"55<=":2.0}
EDU={"No Formal quals":0.0,"Lower Than A Level":1.0,"A Level or Equivalent":2.0,
     "HE Qualification":3.0,"Post Graduate Qualification":4.0}

def imd_midpoint(value):
    if pd.isna(value):
        return np.nan
    text=str(value).replace("%","")
    if "-" in text:
        lo,hi=text.split("-",1)
        try:
            return (float(lo)+float(hi))/2.0
        except ValueError:
            return np.nan
    return np.nan

def build_table(data_dir: Path):
    info=pd.read_csv(data_dir/"studentInfo.csv")
    registration=pd.read_csv(data_dir/"studentRegistration.csv")
    assessment=pd.read_csv(data_dir/"assessments.csv")
    student_assessment=pd.read_csv(data_dir/"studentAssessment.csv")

    submissions=student_assessment.merge(
        assessment[["id_assessment","code_module","code_presentation"]],
        on="id_assessment",how="left",validate="many_to_one"
    )
    early=(submissions["date_submitted"]<=30)
    exposed=(submissions.loc[early,KEY].drop_duplicates().assign(treatment=1))

    frame=info.merge(registration[KEY+["date_registration"]],on=KEY,how="left")
    frame=frame.merge(exposed,on=KEY,how="left")
    frame["treatment"]=frame["treatment"].fillna(0).astype(int)
    frame["outcome"]=frame["final_result"].isin(["Pass","Distinction"]).astype(int)
    frame["age_ord"]=frame["age_band"].map(AGE)
    frame["education_ord"]=frame["highest_education"].map(EDU)
    frame["imd_mid"]=frame["imd_band"].map(imd_midpoint)
    frame["disability_bin"]=(frame["disability"]=="Y").astype(float)
    frame["gender_female"]=(frame["gender"]=="F").astype(float)
    return frame

def choose_cohort(frame,module=None,presentation=None):
    if module is not None:
        frame=frame[frame["code_module"]==module]
    if presentation is not None:
        frame=frame[frame["code_presentation"]==presentation]
    if module is not None or presentation is not None:
        return frame.copy()
    counts=(frame.groupby(["code_module","code_presentation","treatment"])
            .size().unstack(fill_value=0))
    eligible=counts[(counts.get(0,0)>=30)&(counts.get(1,0)>=30)]
    if eligible.empty:
        raise ValueError("no cohort has at least 30 exposed and 30 unexposed records")
    selected=eligible.sum(axis=1).idxmax()
    return frame[(frame["code_module"]==selected[0])&
                 (frame["code_presentation"]==selected[1])].copy()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",required=True,type=Path)
    parser.add_argument("--module")
    parser.add_argument("--presentation")
    parser.add_argument("--bootstrap",type=int,default=1000)
    args=parser.parse_args()

    frame=choose_cohort(build_table(args.data_dir),args.module,args.presentation)
    covariate_names=["studied_credits","num_of_prev_attempts","date_registration",
                     "age_ord","education_ord","imd_mid","disability_bin","gender_female"]
    analysis=frame[KEY+["treatment","outcome"]+covariate_names].dropna().copy()
    if analysis["treatment"].nunique()!=2:
        raise ValueError("selected cohort does not contain both exposure groups")

    X=analysis[covariate_names].astype(float)
    treatment=analysis["treatment"].astype(int).tolist()
    outcome=analysis["outcome"].astype(float).tolist()

    propensity_model=Pipeline([
        ("scale",StandardScaler()),
        ("logit",LogisticRegression(max_iter=4000,random_state=42))
    ])
    propensity_model.fit(X,treatment)
    propensity=propensity_model.predict_proba(X)[:,1].tolist()
    covariates={name:X[name].tolist() for name in covariate_names}

    result=analyze_ipw(
        treatment,outcome,propensity,covariates=covariates,
        bootstrap_iterations=args.bootstrap
    )
    result["research_bundle"]=True
    result["dataset"]="OULAD"
    result["cohort"]={
        "code_module":str(analysis["code_module"].iloc[0]),
        "code_presentation":str(analysis["code_presentation"].iloc[0]),
        "n":int(len(analysis)),
        "treated":int(sum(treatment)),
        "control":int(len(treatment)-sum(treatment)),
    }
    result["treatment_definition"]="at least one assessment submitted on or before day 30"
    result["outcome_definition"]="Pass or Distinction"
    result["covariates"]=covariate_names
    result["propensity_model"]="standardized logistic regression; same-cohort complete-case analysis"

    out=ROOT/"results"; out.mkdir(exist_ok=True)
    (out/"oulad_metrics.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
