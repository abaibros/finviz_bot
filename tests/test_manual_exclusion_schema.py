import csv
import inspect
import os
import shutil
import unittest
import uuid
from datetime import datetime
from unittest.mock import patch

import pandas as pd

import manual_exclusion_schema
import scorer
import telegram_reporter
import watchlist_logger
from manual_exclusion_schema import (
    ALLOWED_REASON_CODES,
    MANUAL_EXCLUSION_FIELDS,
    validate_manual_exclusion_csv,
)
from watchlist_logger import append_watchlist_rows


class ManualExclusionSchemaTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = os.path.join(os.getcwd(), f"test_manual_exclusion_tmp_{uuid.uuid4().hex}")
        os.makedirs(self.tmp_dir)
        self.path = os.path.join(self.tmp_dir, "manual_exclusion_list.csv")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def write_rows(self, fieldnames, rows):
        with open(self.path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def apply_exclusions(self, rows, fieldnames=None):
        self.write_rows(fieldnames or MANUAL_EXCLUSION_FIELDS, rows)
        df = pd.DataFrame([
            {"ticker": "APLS", "total_score": 90.0},
            {"ticker": "NVO", "total_score": 80.0},
        ])
        with patch.object(scorer, "MANUAL_EXCLUSION_CSV", self.path):
            return scorer.apply_manual_exclusions(df)

    def test_existing_apls_exclusion_is_preserved(self):
        result = self.apply_exclusions([
            {
                "ticker": "APLS",
                "action": "exclude_permanent",
                "reason_code": "M_AND_A_COMPLETED",
                "reason_note": "M&A/event-completed type; not a normal watchlist candidate",
                "exclusion_type": "permanent",
                "source_note": "M&A/event-completed; details to be verified manually",
                "added_date": "2026-05-24",
            }
        ])

        self.assertEqual(["NVO"], result["ticker"].tolist())

    def test_new_schema_still_uses_action_for_exclusion(self):
        result = self.apply_exclusions([
            {
                "ticker": "APLS",
                "action": "watch_only",
                "reason_code": "M_AND_A_COMPLETED",
                "reason_note": "not excluded because action is not exclude_permanent",
                "exclusion_type": "permanent",
                "source_note": "manual",
                "added_date": "2026-05-24",
            }
        ])

        self.assertEqual(["APLS", "NVO"], result["ticker"].tolist())

    def test_legacy_schema_without_new_fields_still_excludes_by_action(self):
        result = self.apply_exclusions(
            [{"ticker": "APLS", "action": "exclude_permanent"}],
            fieldnames=["ticker", "action"],
        )

        self.assertEqual(["NVO"], result["ticker"].tolist())

    def test_invalid_reason_code_raises_validation_error(self):
        self.write_rows(MANUAL_EXCLUSION_FIELDS, [
            {
                "ticker": "BAD",
                "action": "exclude_permanent",
                "reason_code": "BAD_CODE",
                "reason_note": "invalid",
                "exclusion_type": "permanent",
                "source_note": "manual",
                "added_date": "2026-05-24",
            }
        ])

        with self.assertRaises(ValueError):
            validate_manual_exclusion_csv(self.path)

    def test_empty_reason_code_is_allowed_for_legacy_compatibility(self):
        self.write_rows(MANUAL_EXCLUSION_FIELDS, [
            {
                "ticker": "LEGACY",
                "action": "exclude_permanent",
                "reason_code": "",
                "reason_note": "",
                "exclusion_type": "",
                "source_note": "",
                "added_date": "",
            }
        ])

        validate_manual_exclusion_csv(self.path)

    def test_repo_manual_exclusion_list_csv_is_valid(self):
        validate_manual_exclusion_csv("manual_exclusion_list.csv")

    def test_allowed_reason_codes_are_fixed_in_one_constant(self):
        self.assertEqual(
            {
                "M_AND_A_COMPLETED",
                "TENDER_OFFER",
                "CASH_ACQUISITION",
                "DELISTING_SCHEDULED",
                "MANUAL_BLACKLIST",
            },
            ALLOWED_REASON_CODES,
        )

    def test_telegram_message_builder_is_unchanged_by_manual_exclusion_schema(self):
        class FixedDatetime:
            @classmethod
            def now(cls, tz=None):
                return datetime(2026, 5, 24, 9, 30, tzinfo=tz)

        df = pd.DataFrame([
            {
                "ticker": "NVO",
                "areas": "A,C",
                "total_score": 56.5,
                "return_1y_pct": -31.7,
                "roe": 71.4,
                "revenue_growth": 24.0,
                "market_cap": 208343990272,
                "current_price": 47.0,
                "week52_low": 40.0,
                "recommendation": "buy",
                "analyst_recommendation_mean": 2.36,
                "analyst_opinion_count": 12,
            }
        ])
        env = {"vix": 20.5, "sp_drawdown_pct": -3.2, "regime": "평시 환경"}
        cols = telegram_reporter.resolve_columns(df)

        expected = "\n".join([
            "🔎 관찰 후보 발견 (2026-05-24) - 후보 1",
            "",
            "[시장 환경]",
            "VIX: 20.5 → 평시 환경",
            "S&P 500: 52주 고점 -3.2%",
            "",
            "[데이터 출처]",
            "yfinance / Finviz",
            "(미장 종가 기준, KST 2026-05-24 09:30 조회)",
            "",
            "━━━━━━━━━━━━━━━━",
            "📊 관찰 후보 (55~69)",
            "━━━━━━━━━━━━━━━━",
            "",
            "1. NVO - 56.5점 (A,C)\n"
            "   1년 -31.7% / ROE 71.4% / 매출 +24.0%\n"
            "   시총 $208.3B / 현재가 $47.00\n"
            "   52주 저점 $40.00 / 애널 buy / 2.36점 / 12명",
            "",
            "━━━━━━━━━━━━━━━━",
            "",
            "📌 본인 프로필",
            "- 인내력 -20%",
            "- 한 종목 10~15%",
            "- 모멘텀 충동 → 분할 관찰",
            "",
            "⚠️ 본 알림은 영역 A/C/D/E 커버",
            "영역 B (신 CEO)는 본인 수동 관리",
            "",
            "✅ Claude Pro에 그대로 붙여넣고",
            '"확인해줘" 입력',
            "→ 정밀 검토 실행",
        ])

        with patch.object(telegram_reporter, "datetime", FixedDatetime):
            actual = telegram_reporter.build_signal_message(df, env, cols)

        self.assertEqual(expected.encode("utf-8"), actual.encode("utf-8"))

    def test_scorer_formula_snapshot_is_unchanged(self):
        score = scorer.calculate_score(
            pd.Series({
                "areas": "C,D",
                "roe": 45.0,
                "debt_to_equity": 100.0,
                "revenue_growth": 25.0,
                "return_1y_pct": -40.0,
                "return_5d_pct": -12.0,
                "volume": 11_000_000,
                "beta": 1.0,
            }),
            vix=30.0,
        )

        self.assertEqual(15.0, score["score_roe"])
        self.assertEqual(5.0, score["score_de"])
        self.assertEqual(20.0, score["score_revenue_growth"])
        self.assertEqual(25.0, score["score_drawdown"])
        self.assertEqual(10.0, score["score_volume"])
        self.assertEqual(5.0, score["score_beta"])
        self.assertEqual(5.0, score["score_multi_area"])
        self.assertEqual(85.0, score["total_score"])

    def test_watchlist_logger_does_not_reference_manual_exclusion_list(self):
        source = inspect.getsource(watchlist_logger)
        self.assertNotIn("manual_exclusion", source)
        self.assertNotIn("manual_exclusion_list.csv", source)

    def test_watchlist_logger_append_still_works_with_manual_exclusion_schema_module(self):
        log_path = os.path.join(self.tmp_dir, "watchlist_log.csv")

        append_count = append_watchlist_rows(
            [{"ticker": "APLS", "areas": "A,C", "total_score": 70.0}],
            "20260524T000000000Z",
            "v1.1.1",
            "US",
            "USD",
            "2026-05-24T00:00:00.000Z",
            path=log_path,
        )

        self.assertEqual(1, append_count)

    def test_validation_module_does_not_create_disallowed_artifacts(self):
        self.assertFalse(os.path.exists("result_tracker.py"))
        self.assertNotIn("risk_flags", inspect.getsource(manual_exclusion_schema))


if __name__ == "__main__":
    unittest.main()
