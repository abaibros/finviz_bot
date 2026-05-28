from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_universe_quality_v0_3.py"
CSV_PATH = ROOT / "reports" / "universe_quality_audit_v0_3.csv"

spec = importlib.util.spec_from_file_location("audit_universe_quality_v0_3", SCRIPT_PATH)
audit_v03 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = audit_v03
spec.loader.exec_module(audit_v03)


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_by_ticker(ticker: str) -> dict[str, str]:
    for row in read_rows():
        if row["ticker"] == ticker:
            return row
    raise AssertionError(f"missing ticker {ticker}")


class AuditUniverseQualityV03Tests(unittest.TestCase):
    def test_turnaround_flag_does_not_auto_map_to_high_risk_review(self):
        row = {
            "ticker": "TURN",
            "name": "Turnaround Large Cap",
            "market": "US",
            "sector": "Industrials",
            "sub_industry": "Aerospace & Defense",
            "market_cap_usd_b": "100",
            "source": "SP500",
            "company_type": "",
            "adr_flag": "N",
            "turnaround_flag": "Y",
        }
        decision = audit_v03.classify_metadata_v03(row, set(), set())
        self.assertEqual("CORE", decision.role)

    def test_turnaround_core_validation_is_allowed(self):
        row = {field: "" for field in audit_v03.OUTPUT_FIELDS}
        row.update(
            {
                "ticker": "TURN",
                "turnaround_flag": "Y",
                "v0_3_universe_role": "CORE",
                "gate3_recovery_status": "PASS",
                "gate3_continuation_status": "FAIL",
                "gate3_final_status": "PASS",
                "as_of_date": audit_v03.AS_OF_DATE,
            }
        )
        failures = audit_v03.validate_v03_rows([row])
        self.assertFalse(any("turnaround CORE violation" in failure for failure in failures))

    def test_v0_1_files_are_not_output_targets(self):
        self.assertNotEqual(audit_v03.LEGACY_AUDIT_CSV, audit_v03.V03_AUDIT_CSV)
        self.assertNotEqual(
            ROOT / "reports" / "universe_quality_audit_summary_v0_1.md",
            audit_v03.V03_SUMMARY_MD,
        )

    def test_v0_3_output_file_names_are_v0_3(self):
        self.assertIn("v0_3", audit_v03.V03_AUDIT_CSV.name)
        self.assertIn("v0_3", audit_v03.V03_SUMMARY_MD.name)

    def test_required_columns_exist(self):
        with CSV_PATH.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertIsNotNone(reader.fieldnames)
            self.assertTrue(set(audit_v03.OUTPUT_FIELDS).issubset(set(reader.fieldnames or [])))

    def test_gate3_status_values_are_allowed(self):
        rows = read_rows()
        for row in rows:
            for field in ["gate3_recovery_status", "gate3_continuation_status", "gate3_final_status"]:
                self.assertIn(row[field], audit_v03.GATE3_STATUS_VALUES)

    def test_operating_files_are_not_modified(self):
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--",
                "scorer.py",
                "telegram_reporter.py",
                ".github/workflows/main.yml",
                "run_daily_report.py",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual("", result.stdout.strip())

    def test_v0_1_outputs_are_not_modified(self):
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--",
                "reports/universe_quality_audit_v0_1.csv",
                "reports/universe_quality_audit_summary_v0_1.md",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual("", result.stdout.strip())

    def test_as_of_date_is_fixed(self):
        self.assertEqual("2026-05-27", audit_v03.AS_OF_DATE)
        for row in read_rows():
            self.assertEqual("2026-05-27", row["as_of_date"])

    def test_yfinance_collection_period_is_fixed(self):
        self.assertEqual("2025-03-01", audit_v03.PRICE_START_DATE)
        self.assertEqual("2026-05-27", audit_v03.PRICE_END_DATE)

    def test_non_turnaround_roles_are_unchanged(self):
        rows = read_rows()
        changed = [
            row
            for row in rows
            if row["turnaround_flag"] != "Y"
            and row["legacy_v0_1_universe_role"] != row["v0_3_universe_role"]
        ]
        self.assertEqual([], changed)

    def test_bax_preserves_legacy_exclude(self):
        bax = row_by_ticker("BAX")
        self.assertEqual("EXCLUDE_CANDIDATE", bax["v0_3_universe_role"])
        self.assertEqual("EXCLUSION_REVIEW", bax["v0_3_action"])

    def test_bax_reason_mentions_non_turnaround_exclusion_preservation(self):
        bax = row_by_ticker("BAX")
        self.assertIn(
            "legacy EXCLUDE preserved due to non-turnaround exclusion reasons",
            bax["v0_3_reason"],
        )

    def test_gate3_fail_turnaround_maps_to_fail_review(self):
        decision = audit_v03.decide_v03_role(
            {"turnaround_flag": "Y"},
            {"universe_role": "HIGH_RISK_REVIEW", "recommended_next_action": "REVIEW_BEFORE_SCORING"},
            audit_v03.RoleDecision("CORE", "KEEP_CORE", "metadata"),
            {
                "gate3_final_status": "FAIL",
                "gate3_recovery_status": "FAIL",
                "gate3_continuation_status": "FAIL",
            },
        )
        self.assertEqual("GATE3_FAIL_REVIEW", decision.role)
        self.assertEqual("REVIEW_BEFORE_SCORING", decision.action)

    def test_gate3_manual_review_stays_manual_review(self):
        decision = audit_v03.decide_v03_role(
            {"turnaround_flag": "Y"},
            {"universe_role": "HIGH_RISK_REVIEW", "recommended_next_action": "REVIEW_BEFORE_SCORING"},
            audit_v03.RoleDecision("CORE", "KEEP_CORE", "metadata"),
            {
                "gate3_final_status": "MANUAL_REVIEW",
                "gate3_recovery_status": "FAIL",
                "gate3_continuation_status": "INSUFFICIENT_DATA",
            },
        )
        self.assertEqual("MANUAL_REVIEW", decision.role)
        self.assertEqual("MANUAL_REVIEW", decision.action)

    def test_gate3_pass_without_gate2_does_not_auto_core(self):
        decision = audit_v03.decide_v03_role(
            {"turnaround_flag": "Y"},
            {"universe_role": "HIGH_RISK_REVIEW", "recommended_next_action": "REVIEW_BEFORE_SCORING"},
            audit_v03.RoleDecision("CORE", "KEEP_CORE", "metadata"),
            {
                "gate3_final_status": "PASS",
                "gate3_recovery_status": "PASS",
                "gate3_continuation_status": "FAIL",
            },
        )
        self.assertEqual("MANUAL_REVIEW", decision.role)
        self.assertNotEqual("CORE", decision.role)


if __name__ == "__main__":
    unittest.main()
