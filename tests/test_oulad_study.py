import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import run_oulad_study as study


def write_fixture(root: Path):
    info = pd.DataFrame([
        ["AAA", "2014J", 1, "M", "North", "A Level or Equivalent", "50-60%", "0-35", 0, 60, "N", "Pass"],
        ["AAA", "2014J", 2, "F", "North", "A Level or Equivalent", "50-60%", "35-55", 0, 60, "N", "Fail"],
        ["AAA", "2014J", 3, "M", "South", "HE Qualification", "60-70%", "35-55", 0, 60, "N", "Withdrawn"],
        ["AAA", "2014J", 4, "F", "South", "HE Qualification", "60-70%", "0-35", 0, 60, "N", "Withdrawn"],
        ["AAA", "2014J", 5, "F", "North", "Lower Than A Level", "40-50%", "0-35", 1, 60, "Y", "Pass"],
        ["AAA", "2014J", 6, "M", "North", "Lower Than A Level", "40-50%", "0-35", 0, 60, "N", "Fail"],
    ], columns=[
        "code_module", "code_presentation", "id_student", "gender", "region",
        "highest_education", "imd_band", "age_band", "num_of_prev_attempts",
        "studied_credits", "disability", "final_result",
    ])
    reg = pd.DataFrame([
        ["AAA", "2014J", 1, -20, None],
        ["AAA", "2014J", 2, -10, None],
        ["AAA", "2014J", 3, -15, 12],
        ["AAA", "2014J", 4, -15, 55],
        ["AAA", "2014J", 5, 35, None],
        ["AAA", "2014J", 6, 10, None],
    ], columns=["code_module", "code_presentation", "id_student", "date_registration", "date_unregistration"])
    assessments = pd.DataFrame([
        ["AAA", "2014J", 101],
        ["AAA", "2014J", 102],
    ], columns=["code_module", "code_presentation", "id_assessment"])
    student_assessment = pd.DataFrame([
        [101, 1, 10, 0, 75],
        [101, 2, 10, 1, 80],
        [101, 3, 5, 0, 50],
        [101, 4, 20, 0, 60],
        [101, 5, 20, 0, 70],
        [101, 6, 5, 0, 65],
        [102, 6, 20, 0, 70],
    ], columns=["id_assessment", "id_student", "date_submitted", "is_banked", "score"])
    info.to_csv(root / "studentInfo.csv", index=False)
    reg.to_csv(root / "studentRegistration.csv", index=False)
    assessments.to_csv(root / "assessments.csv", index=False)
    student_assessment.to_csv(root / "studentAssessment.csv", index=False)


class OULADStudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_landmark_excludes_early_withdrawal_and_late_registration(self):
        frame, meta = study.build_table(self.root, landmark_day=30)
        eligible = dict(zip(frame["id_student"], frame["landmark_eligible"]))
        self.assertFalse(bool(eligible[3]))
        self.assertTrue(bool(eligible[4]))
        self.assertFalse(bool(eligible[5]))
        self.assertGreaterEqual(meta["unregistered_on_or_before_landmark"], 1)

    def test_banked_submission_does_not_define_exposure(self):
        frame, meta = study.build_table(self.root, landmark_day=30)
        treatment = dict(zip(frame["id_student"], frame["treatment"]))
        self.assertEqual(treatment[1], 1)
        self.assertEqual(treatment[2], 0)
        self.assertGreaterEqual(meta["banked_submissions_excluded"], 1)

    def test_submission_before_registration_is_not_exposure(self):
        assessments = pd.read_csv(self.root / "studentAssessment.csv")
        assessments.loc[len(assessments)] = [102, 6, 5, 0, 70]
        reg = pd.read_csv(self.root / "studentRegistration.csv")
        reg.loc[reg["id_student"] == 6, "date_registration"] = 10
        assessments.to_csv(self.root / "studentAssessment.csv", index=False)
        reg.to_csv(self.root / "studentRegistration.csv", index=False)
        frame, meta = study.build_table(self.root, landmark_day=30)
        row = frame.loc[frame["id_student"] == 6].iloc[0]
        self.assertEqual(int(row["treatment"]), 1)
        self.assertGreaterEqual(meta["submission_before_registration_excluded"], 1)

    def test_choose_cohort_requires_module_and_presentation_together(self):
        frame, _ = study.build_table(self.root, landmark_day=30)
        with self.assertRaises(ValueError):
            study.choose_cohort(frame, module="AAA", presentation=None, min_group=1)

    def test_duplicate_registration_keys_are_rejected(self):
        reg = pd.read_csv(self.root / "studentRegistration.csv")
        reg = pd.concat([reg, reg.iloc[[0]]], ignore_index=True)
        reg.to_csv(self.root / "studentRegistration.csv", index=False)
        with self.assertRaisesRegex(ValueError, "duplicate learner-registration"):
            study.build_table(self.root)

    def test_prepare_analysis_reports_missingness(self):
        frame, _ = study.build_table(self.root)
        cohort = frame.loc[frame["landmark_eligible"]].copy()
        cohort.loc[cohort.index[0], "region"] = "?"
        with self.assertRaises(ValueError):
            study.prepare_analysis(cohort)

    def test_propensity_pipeline_handles_categorical_covariates(self):
        rows = []
        for i in range(80):
            rows.append({
                "code_module": "AAA", "code_presentation": "2014J", "id_student": i,
                "treatment": i % 2, "outcome": (i // 3) % 2,
                "studied_credits": 30 + (i % 4) * 15,
                "num_of_prev_attempts": i % 3,
                "date_registration": -50 + (i % 20),
                "age_band": ["0-35", "35-55"][i % 2],
                "highest_education": ["A Level or Equivalent", "HE Qualification"][i % 2],
                "imd_band": ["40-50%", "50-60%"][i % 2],
                "disability": ["N", "Y"][i % 2],
                "gender": ["M", "F"][i % 2],
                "region": ["North", "South", "East", "West"][i % 4],
            })
        analysis = pd.DataFrame(rows)
        _, propensity = study.fit_propensity(analysis)
        self.assertEqual(len(propensity), 80)
        self.assertTrue(((propensity > 0) & (propensity < 1)).all())

    def test_full_refit_bootstrap_returns_interval(self):
        rows = []
        for i in range(80):
            rows.append({
                "code_module": "AAA", "code_presentation": "2014J", "id_student": i,
                "treatment": i % 2, "outcome": 1 if (i % 4) in (0, 1) else 0,
                "studied_credits": 30 + (i % 5) * 15,
                "num_of_prev_attempts": i % 3,
                "date_registration": -80 + (i % 25),
                "age_band": ["0-35", "35-55"][i % 2],
                "highest_education": ["A Level or Equivalent", "HE Qualification"][i % 2],
                "imd_band": ["40-50%", "50-60%"][i % 2],
                "disability": ["N", "Y"][i % 2],
                "gender": ["M", "F"][i % 2],
                "region": ["North", "South", "East", "West"][i % 4],
            })
        analysis = pd.DataFrame(rows)
        out = study.full_refit_bootstrap_ci(analysis, iterations=200, seed=7)
        self.assertEqual(out["iterations_requested"], 200)
        self.assertLessEqual(out["interval"][0], out["interval"][1])


if __name__ == "__main__":
    unittest.main()
