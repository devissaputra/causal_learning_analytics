from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from causal_learning_analytics.core import analyze_ipw

KEY = ["code_module", "code_presentation", "id_student"]
AGE = {"0-35": 0.0, "35-55": 1.0, "55<=": 2.0}
EDU = {
    "No Formal quals": 0.0,
    "Lower Than A Level": 1.0,
    "A Level or Equivalent": 2.0,
    "HE Qualification": 3.0,
    "Post Graduate Qualification": 4.0,
}
UCI_ID = 349
DATA_URL = "https://archive.ics.uci.edu/static/public/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset.zip"
DATA_DOI = "10.24432/C5KK69"
DATA_LICENSE = "CC BY 4.0"
REQUIRED = ("studentInfo.csv", "studentRegistration.csv", "assessments.csv", "studentAssessment.csv")


def imd_midpoint(value):
    if pd.isna(value):
        return np.nan
    text = str(value).replace("%", "")
    if "-" in text:
        lo, hi = text.split("-", 1)
        try:
            return (float(lo) + float(hi)) / 2.0
        except ValueError:
            return np.nan
    return np.nan


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_data_dir(data_dir: Path | None, cache_dir: Path) -> tuple[Path, dict]:
    if data_dir is not None:
        data_dir = data_dir.resolve()
        missing = [name for name in REQUIRED if not (data_dir / name).exists()]
        if missing:
            raise FileNotFoundError(f"missing OULAD files in {data_dir}: {missing}")
        return data_dir, {
            "source": f"local:{data_dir}",
            "uci_id": UCI_ID,
            "doi": DATA_DOI,
            "license": DATA_LICENSE,
            "archive_sha256": None,
            "files": list(REQUIRED),
        }

    cache_dir.mkdir(parents=True, exist_ok=True)
    archive = cache_dir / "oulad-uci349.zip"
    extracted = cache_dir / "oulad-uci349"
    if not archive.exists():
        with urllib.request.urlopen(DATA_URL, timeout=180) as response:
            archive.write_bytes(response.read())

    extracted.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        by_basename = {Path(name).name: name for name in zf.namelist() if not name.endswith("/")}
        missing = [name for name in REQUIRED if name not in by_basename]
        if missing:
            raise FileNotFoundError(f"required files absent from UCI archive: {missing}")
        for name in REQUIRED:
            target = extracted / name
            if not target.exists():
                target.write_bytes(zf.read(by_basename[name]))

    return extracted, {
        "source": DATA_URL,
        "uci_id": UCI_ID,
        "doi": DATA_DOI,
        "license": DATA_LICENSE,
        "archive_sha256": _sha256(archive),
        "files": list(REQUIRED),
    }


def build_table(data_dir: Path):
    info = pd.read_csv(data_dir / "studentInfo.csv")
    registration = pd.read_csv(data_dir / "studentRegistration.csv")
    assessment = pd.read_csv(data_dir / "assessments.csv")
    student_assessment = pd.read_csv(data_dir / "studentAssessment.csv")

    submissions = student_assessment.merge(
        assessment[["id_assessment", "code_module", "code_presentation"]],
        on="id_assessment", how="left", validate="many_to_one"
    )
    early = submissions["date_submitted"] <= 30
    exposed = submissions.loc[early, KEY].drop_duplicates().assign(treatment=1)

    frame = info.merge(registration[KEY + ["date_registration"]], on=KEY, how="left")
    frame = frame.merge(exposed, on=KEY, how="left")
    frame["treatment"] = frame["treatment"].fillna(0).astype(int)
    frame["outcome"] = frame["final_result"].isin(["Pass", "Distinction"]).astype(int)
    frame["age_ord"] = frame["age_band"].map(AGE)
    frame["education_ord"] = frame["highest_education"].map(EDU)
    frame["imd_mid"] = frame["imd_band"].map(imd_midpoint)
    frame["disability_bin"] = (frame["disability"] == "Y").astype(float)
    frame["gender_female"] = (frame["gender"] == "F").astype(float)
    return frame


def choose_cohort(frame, module=None, presentation=None):
    if module is not None:
        frame = frame[frame["code_module"] == module]
    if presentation is not None:
        frame = frame[frame["code_presentation"] == presentation]
    if module is not None or presentation is not None:
        return frame.copy()
    counts = frame.groupby(["code_module", "code_presentation", "treatment"]).size().unstack(fill_value=0)
    eligible = counts[(counts.get(0, 0) >= 30) & (counts.get(1, 0) >= 30)]
    if eligible.empty:
        raise ValueError("no cohort has at least 30 exposed and 30 unexposed records")
    selected = eligible.sum(axis=1).idxmax()
    return frame[
        (frame["code_module"] == selected[0]) &
        (frame["code_presentation"] == selected[1])
    ].copy()


def _fmt(value):
    if value is None:
        return "not estimable"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.4f}"
    return str(value)


def write_summary(result: dict):
    cohort = result["cohort"]
    wd = result.get("weight_diagnostics", {})
    support = result.get("common_support", {})
    lines = [
        "# Empirical Results Summary",
        "",
        "This file is generated by `scripts/run_oulad_study.py`. Numerical values should not be hand-edited.",
        "",
        "## Dataset and cohort",
        "",
        f"- Dataset: OULAD / UCI {UCI_ID}",
        f"- DOI: {DATA_DOI}",
        f"- Cohort: {cohort['code_module']} {cohort['code_presentation']}",
        f"- Complete-case n: {cohort['n']} ({cohort['treated']} exposed; {cohort['control']} control)",
        f"- Archive SHA-256: `{result['dataset_provenance'].get('archive_sha256')}`",
        "",
        "## Effect estimates",
        "",
        f"- Raw treated-minus-control difference: {_fmt(result.get('raw_mean_difference'))}",
        f"- Horvitz-Thompson ATE estimate: {_fmt(result.get('ipw_ate_ht'))}",
        f"- Hájek ATE estimate: {_fmt(result.get('ipw_ate_hajek'))}",
        f"- Bootstrap interval: {_fmt(result.get('bootstrap_ci'))}",
        "",
        "## Diagnostics",
        "",
        f"- Fraction in empirical common support: {_fmt(support.get('overall_fraction_in_support'))}",
        f"- Overall effective sample size: {_fmt(wd.get('overall_ess'))}",
        f"- Maximum weight: {_fmt(wd.get('max_weight'))}",
        f"- Analysis flags: {', '.join(result.get('analysis_flags', [])) or 'none'}",
        "",
        "## Interpretation boundary",
        "",
        "These are observational weighted contrasts. A causal interpretation additionally requires untestable identification assumptions, including conditional exchangeability. The study does not establish that early submission itself causes course success.",
        "",
    ]
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    paper = ROOT / "paper"
    paper.mkdir(exist_ok=True)
    (paper / "results.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache")
    parser.add_argument("--module")
    parser.add_argument("--presentation")
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()

    data_dir, provenance = prepare_data_dir(args.data_dir, args.cache_dir)
    frame = choose_cohort(build_table(data_dir), args.module, args.presentation)
    covariate_names = [
        "studied_credits", "num_of_prev_attempts", "date_registration",
        "age_ord", "education_ord", "imd_mid", "disability_bin", "gender_female",
    ]
    analysis = frame[KEY + ["treatment", "outcome"] + covariate_names].copy()
    # OULAD/UCI may encode missing values as literal "?" strings. Coerce the
    # frozen numeric adjustment set first, then apply the declared complete-case rule.
    for name in covariate_names:
        analysis[name] = pd.to_numeric(analysis[name], errors="coerce")
    analysis = analysis.dropna(subset=covariate_names).copy()
    if analysis["treatment"].nunique() != 2:
        raise ValueError("selected cohort does not contain both exposure groups")

    X = analysis[covariate_names].astype(float)
    treatment = analysis["treatment"].astype(int).tolist()
    outcome = analysis["outcome"].astype(float).tolist()

    propensity_model = Pipeline([
        ("scale", StandardScaler()),
        ("logit", LogisticRegression(max_iter=4000, random_state=42)),
    ])
    propensity_model.fit(X, treatment)
    propensity = propensity_model.predict_proba(X)[:, 1].tolist()
    covariates = {name: X[name].tolist() for name in covariate_names}

    result = analyze_ipw(
        treatment, outcome, propensity, covariates=covariates,
        bootstrap_iterations=args.bootstrap,
    )
    result["research_bundle"] = True
    result["dataset"] = "OULAD"
    result["dataset_provenance"] = provenance
    result["cohort"] = {
        "code_module": str(analysis["code_module"].iloc[0]),
        "code_presentation": str(analysis["code_presentation"].iloc[0]),
        "n": int(len(analysis)),
        "treated": int(sum(treatment)),
        "control": int(len(treatment) - sum(treatment)),
    }
    result["treatment_definition"] = "at least one assessment submitted on or before day 30"
    result["outcome_definition"] = "Pass or Distinction"
    result["covariates"] = covariate_names
    result["missing_data_rule"] = "complete-case analysis on the frozen adjustment set"
    result["propensity_model"] = "standardized logistic regression; same-cohort complete-case analysis"

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "oulad_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_summary(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
