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
import sklearn
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from causal_learning_analytics.core import analyze_ipw, ipw_ate, ipw_weights, raw_mean_difference, weight_diagnostics

KEY = ["code_module", "code_presentation", "id_student"]
LANDMARK_DAY = 30
NUMERIC_COVARIATES = ["studied_credits", "num_of_prev_attempts", "date_registration"]
CATEGORICAL_COVARIATES = [
    "age_band", "highest_education", "imd_band", "disability", "gender", "region",
]
BOOTSTRAP_SEED = 20260925
UCI_ID = 349

UCI_ID = 349
DATA_URL = "https://archive.ics.uci.edu/static/public/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset.zip"
DATA_DOI = "10.24432/C5KK69"
DATA_LICENSE = "CC BY 4.0"
REQUIRED = ("studentInfo.csv", "studentRegistration.csv", "assessments.csv", "studentAssessment.csv")


def _normalize_missing(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    frame = frame.copy()
    for name in columns:
        frame[name] = frame[name].replace({"?": np.nan, "": np.nan, "nan": np.nan, "None": np.nan})
    return frame

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


def build_table(data_dir: Path, landmark_day: int = LANDMARK_DAY) -> tuple[pd.DataFrame, dict]:
    info = pd.read_csv(data_dir / "studentInfo.csv")
    registration = pd.read_csv(data_dir / "studentRegistration.csv")
    assessment = pd.read_csv(data_dir / "assessments.csv")
    student_assessment = pd.read_csv(data_dir / "studentAssessment.csv")

    if registration.duplicated(KEY).any():
        raise ValueError("studentRegistration contains duplicate learner-registration keys")
    if info.duplicated(KEY).any():
        raise ValueError("studentInfo contains duplicate learner-registration keys")

    registration = registration.copy()
    registration["date_registration"] = pd.to_numeric(registration["date_registration"], errors="coerce")
    registration["date_unregistration"] = pd.to_numeric(registration["date_unregistration"], errors="coerce")

    submissions = student_assessment.merge(
        assessment[["id_assessment", "code_module", "code_presentation"]],
        on="id_assessment", how="left", validate="many_to_one"
    )
    submissions = submissions.merge(
        registration[KEY + ["date_registration"]],
        on=KEY, how="left", validate="many_to_one"
    )
    submissions["date_submitted"] = pd.to_numeric(submissions["date_submitted"], errors="coerce")
    submissions["is_banked"] = pd.to_numeric(submissions["is_banked"], errors="coerce").fillna(0).astype(int)

    non_banked = submissions["is_banked"].eq(0)
    within_landmark = submissions["date_submitted"].notna() & submissions["date_submitted"].le(landmark_day)
    after_registration = (
        submissions["date_registration"].notna()
        & submissions["date_submitted"].ge(submissions["date_registration"])
    )
    early_valid = non_banked & within_landmark & after_registration
    exposed = submissions.loc[early_valid, KEY].drop_duplicates().assign(treatment=1)

    frame = info.merge(
        registration[KEY + ["date_registration", "date_unregistration"]],
        on=KEY, how="left", validate="one_to_one"
    )
    frame = frame.merge(exposed, on=KEY, how="left", validate="one_to_one")
    frame["treatment"] = frame["treatment"].fillna(0).astype(int)
    frame["outcome"] = frame["final_result"].isin(["Pass", "Distinction"]).astype(int)

    registered_by_landmark = frame["date_registration"].notna() & frame["date_registration"].le(landmark_day)
    outcome_timing_known = (
        ((frame["final_result"] != "Withdrawn") & frame["date_unregistration"].isna())
        | frame["date_unregistration"].gt(landmark_day)
    )
    frame["landmark_eligible"] = registered_by_landmark & outcome_timing_known

    metadata = {
        "landmark_day": int(landmark_day),
        "source_registrations": int(len(frame)),
        "registered_after_landmark_or_missing": int((~registered_by_landmark).sum()),
        "unregistered_on_or_before_landmark": int(frame["date_unregistration"].le(landmark_day).fillna(False).sum()),
        "withdrawal_timing_unknown": int(
            ((frame["final_result"] == "Withdrawn") & frame["date_unregistration"].isna()).sum()
        ),
        "landmark_eligible_registrations": int(frame["landmark_eligible"].sum()),
        "banked_submissions_excluded": int(submissions["is_banked"].eq(1).sum()),
        "nonbanked_submissions_through_landmark": int(early_valid.sum()),
        "submission_before_registration_excluded": int(
            (non_banked & within_landmark & ~after_registration).sum()
        ),
    }
    return frame, metadata

def choose_cohort(frame, module=None, presentation=None, min_group: int = 30):
    if (module is None) != (presentation is None):
        raise ValueError("--module and --presentation must be supplied together")
    eligible = frame.loc[frame["landmark_eligible"]].copy()
    if module is not None:
        eligible = eligible[
            (eligible["code_module"] == module)
            & (eligible["code_presentation"] == presentation)
        ]
        counts = eligible["treatment"].value_counts()
        if counts.get(0, 0) < min_group or counts.get(1, 0) < min_group:
            raise ValueError("requested landmark cohort lacks sufficient exposed/control observations")
        return eligible
    counts = eligible.groupby(["code_module", "code_presentation", "treatment"]).size().unstack(fill_value=0)
    if 0 not in counts:
        counts[0] = 0
    if 1 not in counts:
        counts[1] = 0
    qualified = counts[(counts[0] >= min_group) & (counts[1] >= min_group)]
    if qualified.empty:
        raise ValueError("no landmark cohort has sufficient exposed and control observations")
    selected = qualified.sum(axis=1).idxmax()
    return eligible[
        (eligible["code_module"] == selected[0])
        & (eligible["code_presentation"] == selected[1])
    ].copy()


def prepare_analysis(cohort: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = NUMERIC_COVARIATES + CATEGORICAL_COVARIATES
    analysis = cohort[KEY + ["treatment", "outcome"] + required].copy()
    analysis = _normalize_missing(analysis, CATEGORICAL_COVARIATES)
    for name in NUMERIC_COVARIATES:
        analysis[name] = pd.to_numeric(analysis[name], errors="coerce")
    missing_by_covariate = {name: int(analysis[name].isna().sum()) for name in required}
    any_missing = analysis[required].isna().any(axis=1)
    complete = analysis.loc[~any_missing].copy()
    counts = complete["treatment"].value_counts()
    if counts.get(0, 0) < 30 or counts.get(1, 0) < 30:
        raise ValueError("complete-case landmark cohort lacks at least 30 observations in each exposure group")
    return complete, {
        "landmark_cohort_before_complete_case": int(len(analysis)),
        "excluded_for_any_missing_covariate": int(any_missing.sum()),
        "complete_case_n": int(len(complete)),
        "missing_by_covariate": missing_by_covariate,
    }


def make_propensity_pipeline(include_region=True, quadratic_numeric=False, c_value=1.0):
    numeric = list(NUMERIC_COVARIATES)
    categorical = [name for name in CATEGORICAL_COVARIATES if include_region or name != "region"]
    numeric_steps = [("scale", StandardScaler())]
    if quadratic_numeric:
        numeric_steps.append(("quadratic", PolynomialFeatures(degree=2, include_bias=False)))
    pre = ColumnTransformer([
        ("numeric", Pipeline(numeric_steps), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])
    model = Pipeline([
        ("preprocess", pre),
        ("logit", LogisticRegression(max_iter=4000, random_state=42, C=c_value)),
    ])
    return model, numeric, categorical


def fit_propensity(analysis, include_region=True, quadratic_numeric=False, c_value=1.0):
    model, numeric, categorical = make_propensity_pipeline(
        include_region=include_region,
        quadratic_numeric=quadratic_numeric,
        c_value=c_value,
    )
    features = numeric + categorical
    treatment = analysis["treatment"].astype(int).to_numpy()
    model.fit(analysis[features], treatment)
    return model, model.predict_proba(analysis[features])[:, 1]


def balance_covariates(analysis):
    values = {name: analysis[name].astype(float).tolist() for name in NUMERIC_COVARIATES}
    for name in CATEGORICAL_COVARIATES:
        series = analysis[name].astype(str)
        for level in sorted(series.unique()):
            values[f"{name}={level}"] = (series == level).astype(float).tolist()
    return values


def full_refit_bootstrap_ci(analysis, iterations, seed=BOOTSTRAP_SEED, confidence=0.95):
    if iterations < 200:
        raise ValueError("full-refit bootstrap requires at least 200 iterations")
    rng = np.random.default_rng(seed)
    estimates = []
    n = len(analysis)
    for _ in range(iterations):
        sample = analysis.iloc[rng.integers(0, n, size=n)].reset_index(drop=True)
        treatment = sample["treatment"].astype(int).to_numpy()
        if len(np.unique(treatment)) != 2:
            continue
        _, propensity = fit_propensity(sample)
        try:
            estimate = ipw_ate(
                treatment.tolist(),
                sample["outcome"].astype(float).tolist(),
                propensity.tolist(),
                normalized=True,
            )
        except ValueError:
            continue
        estimates.append(float(estimate))
    if len(estimates) < max(100, iterations // 2):
        raise ValueError("too few valid full-refit bootstrap replicates")
    alpha = 1.0 - confidence
    lo, hi = np.quantile(estimates, [alpha / 2, 1 - alpha / 2])
    return {
        "method": "percentile bootstrap with propensity model refit in every resample",
        "iterations_requested": int(iterations),
        "iterations_valid": int(len(estimates)),
        "seed": int(seed),
        "confidence_level": float(confidence),
        "interval": [float(lo), float(hi)],
        "bootstrap_mean": float(np.mean(estimates)),
        "bootstrap_sd": float(np.std(estimates, ddof=1)),
    }


def common_support_sensitivity(treatment, outcome, propensity):
    t = np.asarray(treatment, dtype=int)
    y = np.asarray(outcome, dtype=float)
    p = np.asarray(propensity, dtype=float)
    treated_range = (float(p[t == 1].min()), float(p[t == 1].max()))
    control_range = (float(p[t == 0].min()), float(p[t == 0].max()))
    lower, upper = max(treated_range[0], control_range[0]), min(treated_range[1], control_range[1])
    mask = (p >= lower) & (p <= upper)
    t2, y2, p2 = t[mask], y[mask], p[mask]
    return {
        "common_support": [float(lower), float(upper)],
        "n": int(mask.sum()),
        "excluded": int((~mask).sum()),
        "treated": int(t2.sum()),
        "control": int(len(t2) - t2.sum()),
        "raw_mean_difference": float(raw_mean_difference(t2.tolist(), y2.tolist())),
        "hajek_ate_same_fitted_propensity": float(
            ipw_ate(t2.tolist(), y2.tolist(), p2.tolist(), normalized=True)
        ),
        "interpretation": "Restricted to empirical common support; propensity scores are not refit after restriction.",
    }


def propensity_specification_sensitivity(analysis):
    specs = [
        ("primary", True, False, 1.0),
        ("no_region", False, False, 1.0),
        ("quadratic_numeric", True, True, 1.0),
        ("stronger_l2", True, False, 0.25),
    ]
    treatment = analysis["treatment"].astype(int).tolist()
    outcome = analysis["outcome"].astype(float).tolist()
    rows = []
    for name, include_region, quadratic, c_value in specs:
        _, propensity = fit_propensity(
            analysis,
            include_region=include_region,
            quadratic_numeric=quadratic,
            c_value=c_value,
        )
        weights = ipw_weights(treatment, propensity.tolist())["weights"]
        diagnostics = weight_diagnostics(treatment, weights)
        rows.append({
            "specification": name,
            "include_region": include_region,
            "quadratic_numeric": quadratic,
            "logistic_C": c_value,
            "hajek_ate": float(ipw_ate(treatment, outcome, propensity.tolist(), normalized=True)),
            "propensity_range": [float(propensity.min()), float(propensity.max())],
            "max_weight": float(diagnostics["max_weight"]),
            "overall_ess": float(diagnostics["overall_ess"]),
        })
    return rows


def write_figures(result, treatment, propensity, weights, outdir: Path):
    figdir = outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    t = np.asarray(treatment, dtype=int)
    p = np.asarray(propensity, dtype=float)
    w = np.asarray(weights, dtype=float)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(p[t == 1], bins=24, alpha=0.55, density=True, label="Early submission")
    ax.hist(p[t == 0], bins=24, alpha=0.55, density=True, label="No early submission")
    ax.set_xlabel("Estimated propensity")
    ax.set_ylabel("Density")
    ax.set_title("Propensity overlap in the day-30 landmark cohort")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figdir / "propensity_overlap.png", dpi=170)
    plt.close(fig)

    before, after = result["balance_before"], result["balance_after"]
    names = list(before)
    before_abs = np.asarray([abs(before[n]["smd"]) for n in names], dtype=float)
    after_abs = np.asarray([abs(after[n]["smd"]) for n in names], dtype=float)
    order = np.argsort(np.maximum(before_abs, after_abs))
    fig, ax = plt.subplots(figsize=(8, max(5, 0.28 * len(names))))
    y = np.arange(len(names))
    ax.scatter(before_abs[order], y, label="Before weighting")
    ax.scatter(after_abs[order], y, label="After weighting")
    ax.axvline(0.10, linestyle="--", linewidth=1)
    ax.set_yticks(y, [names[i] for i in order], fontsize=8)
    ax.set_xlabel("Absolute standardized mean difference")
    ax.set_title("Covariate balance")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figdir / "balance_love_plot.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(w, bins=30)
    ax.set_xlabel("ATE inverse-probability weight")
    ax.set_ylabel("Observations")
    ax.set_title("IPW weight distribution")
    fig.tight_layout()
    fig.savefig(figdir / "weight_distribution.png", dpi=170)
    plt.close(fig)

    sensitivity = result["propensity_specification_sensitivity"]
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = [row["specification"] for row in sensitivity]
    estimates = [row["hajek_ate"] for row in sensitivity]
    ax.plot(range(len(labels)), estimates, marker="o")
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    ax.set_ylabel("Hajek ATE-style contrast")
    ax.set_title("Propensity-specification sensitivity")
    fig.tight_layout()
    fig.savefig(figdir / "propensity_specification_sensitivity.png", dpi=170)
    plt.close(fig)

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
    full_ci = result["full_refit_bootstrap"]["interval"]
    missing = result["flow"]["missing_data"]
    lines = [
        "# Empirical Results Summary",
        "",
        "Generated by scripts/run_oulad_study.py; numerical values should not be hand-edited.",
        "",
        "## Frozen landmark design",
        "",
        f"- Landmark day: {result['landmark_day']}",
        f"- Dataset: OULAD / UCI {UCI_ID}",
        f"- Cohort: {cohort['code_module']} {cohort['code_presentation']}",
        f"- Landmark-eligible cohort before complete-case filtering: {missing['landmark_cohort_before_complete_case']}",
        f"- Complete-case n: {cohort['n']} ({cohort['treated']} exposed; {cohort['control']} control)",
        f"- Exposure: {result['treatment_definition']}",
        f"- Outcome: {result['outcome_definition']}",
        f"- Archive SHA-256: {result['dataset_provenance'].get('archive_sha256')}",
        "",
        "## Effect estimates",
        "",
        f"- Raw treated-minus-control difference: {_fmt(result.get('raw_mean_difference'))}",
        f"- Horvitz-Thompson ATE-style estimate: {_fmt(result.get('ipw_ate_ht'))}",
        f"- Hajek ATE-style estimate: {_fmt(result.get('ipw_ate_hajek'))}",
        f"- Full-refit bootstrap 95% interval: {_fmt(full_ci)}",
        f"- Fixed-propensity bootstrap 95% interval: {_fmt(result.get('hajek_ate_ci'))}",
        "",
        "## Diagnostics",
        "",
        f"- Fraction in empirical common support: {_fmt(support.get('overall_fraction_in_support'))}",
        f"- Overall effective sample size: {_fmt(wd.get('overall_ess'))}",
        f"- Maximum weight: {_fmt(wd.get('max_weight'))}",
        f"- Common-support restricted Hajek contrast: {_fmt(result['common_support_sensitivity']['hajek_ate_same_fitted_propensity'])}",
        f"- Analysis flags: {', '.join(result.get('analysis_flags', [])) or 'none'}",
        "",
        "## Missing-data accounting",
        "",
        f"- Excluded for any frozen adjustment covariate: {missing['excluded_for_any_missing_covariate']}",
    ]
    for name, count in missing["missing_by_covariate"].items():
        lines.append(f"- Missing {name}: {count}")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "These are observational weighted contrasts in a day-30 landmark population. A causal interpretation additionally requires untestable identification assumptions, especially conditional exchangeability. The study does not establish that requiring early submission would cause improved course outcomes.",
        "",
    ]
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    paper = ROOT / "paper"
    paper.mkdir(exist_ok=True)
    (paper / "results.md").write_text("# Results\n\n" + "\n".join(lines[2:]), encoding="utf-8")


def run_study(data_dir: Path, provenance: dict, module=None, presentation=None, bootstrap_iterations=1000):
    frame, build_meta = build_table(data_dir, LANDMARK_DAY)
    cohort = choose_cohort(frame, module, presentation)
    analysis, missing_meta = prepare_analysis(cohort)

    _, propensity = fit_propensity(analysis)
    treatment = analysis["treatment"].astype(int).tolist()
    outcome = analysis["outcome"].astype(float).tolist()
    covariates = balance_covariates(analysis)

    result = analyze_ipw(
        treatment, outcome, propensity.tolist(),
        covariates=covariates,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=BOOTSTRAP_SEED,
    )
    weights = ipw_weights(treatment, propensity.tolist())["weights"]
    result["research_bundle"] = True
    result["status"] = "complete"
    result["dataset"] = "OULAD"
    result["dataset_provenance"] = provenance
    result["landmark_day"] = LANDMARK_DAY
    result["cohort"] = {
        "code_module": str(analysis["code_module"].iloc[0]),
        "code_presentation": str(analysis["code_presentation"].iloc[0]),
        "n": int(len(analysis)),
        "treated": int(sum(treatment)),
        "control": int(len(treatment) - sum(treatment)),
    }
    result["treatment_definition"] = "at least one non-banked assessment submitted after registration and on or before presentation day 30"
    result["outcome_definition"] = "Pass or Distinction versus Fail or withdrawal after the day-30 landmark"
    result["eligibility_definition"] = "registered on or before day 30 and not unregistered on or before day 30; withdrawal timing must be observable for withdrawn learners"
    result["numeric_covariates"] = list(NUMERIC_COVARIATES)
    result["categorical_covariates"] = list(CATEGORICAL_COVARIATES)
    result["missing_data_rule"] = "complete-case analysis on the frozen day-30 baseline adjustment set"
    result["propensity_model"] = "standardized numeric covariates plus one-hot categorical covariates in L2 logistic regression"
    result["flow"] = {"landmark_construction": build_meta, "missing_data": missing_meta}
    result["full_refit_bootstrap"] = full_refit_bootstrap_ci(
        analysis, bootstrap_iterations, seed=BOOTSTRAP_SEED
    )
    result["common_support_sensitivity"] = common_support_sensitivity(treatment, outcome, propensity)
    result["propensity_specification_sensitivity"] = propensity_specification_sensitivity(analysis)
    result["environment"] = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
    }
    result["bootstrap_note"] = "hajek_ate_ci is conditional on the originally fitted propensity scores; full_refit_bootstrap is the primary interval because it refits the propensity model."

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "oulad_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_figures(result, treatment, propensity, weights, out)
    write_summary(result)
    return result

def main():
    parser = argparse.ArgumentParser(description="Run the OULAD day-30 landmark causal learning-analytics study")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data" / "cache")
    parser.add_argument("--module")
    parser.add_argument("--presentation")
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()

    if (args.module is None) != (args.presentation is None):
        parser.error("--module and --presentation must be supplied together")

    data_dir, provenance = prepare_data_dir(args.data_dir, args.cache_dir)
    result = run_study(
        data_dir, provenance,
        module=args.module,
        presentation=args.presentation,
        bootstrap_iterations=args.bootstrap,
    )
    print(json.dumps({
        "status": result["status"],
        "cohort": result["cohort"],
        "hajek_ate": result["ipw_ate_hajek"],
        "full_refit_ci": result["full_refit_bootstrap"]["interval"],
    }, indent=2))

if __name__ == "__main__":
    main()
