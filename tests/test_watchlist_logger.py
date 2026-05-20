import csv
import copy
import os
import shutil
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd

import telegram_reporter
import watchlist_logger
from watchlist_logger import (
    WATCHLIST_LOG_FIELDS,
    append_watchlist_rows,
    assert_no_forbidden_words,
    assert_no_forbidden_words_in_row,
    build_run_id,
    build_watchlist_log_row,
    format_created_at_utc,
    normalize_areas,
    validate_watchlist_log_header,
)


LEGACY_WATCHLIST_LOG_LINES = [
    "alert_date,source_time_kst,alert_version,ticker,score,grade,price,market_cap,sector,year_change_pct,roe_pct,revenue_growth_pct,analyst_rating,analyst_score,analyst_count,vix,sp500_from_52w_high_pct",
    "2026-05-20,2026-05-20 09:30:00,v1.1.1,NVO,58.65,약한 후보,47.0,208343990272,Healthcare,-24.66,71.4,24.0,buy,2.36,12,20.5,-3.2",
]


class WatchlistLoggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = os.path.join(os.getcwd(), f"test_watchlist_tmp_{uuid.uuid4().hex}")
        os.makedirs(self.tmp_dir)
        self.path = os.path.join(self.tmp_dir, "watchlist_log.csv")
        self.created_at_utc = "2026-05-22T23:08:00.123Z"
        self.run_id = "20260522T230800123Z"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def candidate(self, ticker="NVO", total_score=69.7, areas=None):
        return {
            "ticker": ticker,
            "areas": ["D", "A", "C", "A"] if areas is None else areas,
            "total_score": total_score,
            "score_roe": 15.0,
            "score_de": 7.5,
            "score_revenue_growth": 19.0,
            "score_drawdown": 13.2,
            "score_volume": 10.0,
            "score_beta": 7.0,
            "score_multi_area": 5.0,
            "return_1y_pct": -31.7,
            "return_5d_pct": -12.4,
            "roe": 71.4,
            "revenue_growth": 24.0,
            "debt_to_equity": 38.2,
            "trailing_pe": 28.5,
            "volume": 12000000,
            "beta": 0.83,
        }

    def read_rows(self, path=None):
        with open(path or self.path, "r", encoding="utf-8-sig", newline="") as csvfile:
            return list(csv.DictReader(csvfile))

    def read_lines(self, path=None):
        with open(path or self.path, "r", encoding="utf-8-sig", newline="") as csvfile:
            return csvfile.read().splitlines()

    def write_legacy_watchlist_log(self):
        with open(self.path, "w", encoding="utf-8-sig", newline="") as csvfile:
            csvfile.write("\n".join(LEGACY_WATCHLIST_LOG_LINES) + "\n")

    def test_candidate_selection_score_rank_and_input_are_unchanged_after_append(self):
        df = pd.DataFrame([
            self.candidate("LOW", total_score=55.0, areas="D, A"),
            self.candidate("HIGH", total_score=72.0, areas="C"),
        ])
        before_candidates = telegram_reporter.build_watchlist_candidates(df)
        before_candidates_copy = copy.deepcopy(before_candidates)
        df_before = df.copy(deep=True)

        append_count = append_watchlist_rows(
            before_candidates,
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        after_candidates = telegram_reporter.build_watchlist_candidates(df)

        self.assertEqual(2, append_count)
        pd.testing.assert_frame_equal(df, df_before)
        self.assertEqual(before_candidates_copy, before_candidates)
        self.assertEqual(before_candidates, after_candidates)
        rows = self.read_rows()
        self.assertEqual(["HIGH", "LOW"], [row["ticker"] for row in rows])
        self.assertEqual(["1", "2"], [row["rank"] for row in rows])
        self.assertEqual("72.0", rows[0]["total_score"])

    def test_telegram_message_builder_byte_level_golden(self):
        class FixedDatetime:
            @classmethod
            def now(cls, tz=None):
                return datetime(2026, 5, 22, 9, 30, tzinfo=tz)

        df = pd.DataFrame([
            {
                **self.candidate("AAA", total_score=71.2, areas="A,C"),
                "current_price": 47.0,
                "market_cap": 208343990272,
                "week52_low": 40.0,
                "recommendation": "buy",
                "analyst_recommendation_mean": 2.36,
                "analyst_opinion_count": 12,
            },
            {
                **self.candidate("BBB", total_score=56.5, areas="D"),
                "current_price": 106.01,
                "market_cap": 4939336192,
                "week52_low": 90.0,
                "recommendation": "hold",
                "analyst_recommendation_mean": 2.83,
                "analyst_opinion_count": 17,
            },
        ])
        env = {"vix": 20.5, "sp_drawdown_pct": -3.2, "regime": "평시 환경"}
        cols = telegram_reporter.resolve_columns(df)

        expected = "\n".join([
            "🔎 관찰 후보 발견 (2026-05-22) - 후보 1",
            "",
            "[시장 환경]",
            "VIX: 20.5 → 평시 환경",
            "S&P 500: 52주 고점 -3.2%",
            "",
            "[데이터 출처]",
            "yfinance / Finviz",
            "(미장 종가 기준, KST 2026-05-22 09:30 조회)",
            "",
            "━━━━━━━━━━━━━━━━",
            "📊 강한 관찰 후보 (70+)",
            "━━━━━━━━━━━━━━━━",
            "",
            "1. AAA - 71.2점 (A,C)\n"
            "   1년 -31.7% / ROE 71.4% / 매출 +24.0%\n"
            "   시총 $208.3B / 현재가 $47.00\n"
            "   52주 저점 $40.00 / 애널 buy / 2.36점 / 12명",
            "",
            "━━━━━━━━━━━━━━━━",
            "📊 관찰 후보 (55~69)",
            "━━━━━━━━━━━━━━━━",
            "",
            "2. BBB - 56.5점 (D)\n"
            "   1년 -31.7% / ROE 71.4% / 매출 +24.0%\n"
            "   시총 $4.9B / 현재가 $106.01\n"
            "   52주 저점 $90.00 / 애널 hold / 2.83점 / 17명",
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

    def test_logger_does_not_special_case_apls_or_manual_exclusions(self):
        append_count = append_watchlist_rows(
            [self.candidate("APLS")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        rows = self.read_rows()
        self.assertEqual(1, append_count)
        self.assertEqual("APLS", rows[0]["ticker"])

    def test_csv_append_only_preserves_existing_row(self):
        append_watchlist_rows(
            [self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        original_first_row = self.read_lines()[1]

        append_watchlist_rows(
            [self.candidate("DUOL")],
            "20260522T230801123Z",
            "v1.1.1",
            "US",
            "USD",
            "2026-05-22T23:08:01.123Z",
            path=self.path,
        )

        lines = self.read_lines()
        self.assertEqual(original_first_row, lines[1])
        self.assertEqual(3, len(lines))

    def test_forbidden_words_fail_for_message_and_row_after_area_normalization(self):
        for forbidden in ["매수 신호", "매수 후보", "분할 매수"]:
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(ValueError):
                    assert_no_forbidden_words(f"이 문자열에는 {forbidden} 포함")

        row = build_watchlist_log_row(
            self.candidate(areas=["a", " 매수 후보 "]),
            1,
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            0,
        )
        self.assertEqual("A,매수 후보", row["areas"])
        with self.assertRaises(ValueError):
            assert_no_forbidden_words_in_row(row)

    def test_telegram_send_failure_does_not_create_or_append_log(self):
        with patch.object(
            telegram_reporter,
            "send_telegram",
            side_effect=RuntimeError("send failed"),
        ), patch.object(telegram_reporter, "append_watchlist_rows") as append_mock:
            with self.assertRaises(RuntimeError):
                telegram_reporter.send_telegram_and_append_watchlist_log(
                    "token",
                    "chat",
                    "message",
                    [self.candidate("NVO")],
                    self.run_id,
                    self.created_at_utc,
                    path=self.path,
                )

        append_mock.assert_not_called()
        self.assertFalse(os.path.exists(self.path))

        with patch.object(telegram_reporter, "send_telegram", return_value=False), patch.object(
            telegram_reporter, "append_watchlist_rows"
        ) as append_mock:
            success, append_count = telegram_reporter.send_telegram_and_append_watchlist_log(
                "token",
                "chat",
                "message",
                [self.candidate("NVO")],
                self.run_id,
                self.created_at_utc,
                path=self.path,
            )

        self.assertFalse(success)
        self.assertEqual(0, append_count)
        append_mock.assert_not_called()
        self.assertFalse(os.path.exists(self.path))

    def test_same_run_duplicate_skipped_and_other_run_allowed(self):
        first_count = append_watchlist_rows(
            [self.candidate("NVO"), self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        duplicate_count = append_watchlist_rows(
            [self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        other_run_count = append_watchlist_rows(
            [self.candidate("NVO")],
            "20260522T230801123Z",
            "v1.1.1",
            "US",
            "USD",
            "2026-05-22T23:08:01.123Z",
            path=self.path,
        )

        rows = self.read_rows()
        self.assertEqual(1, first_count)
        self.assertEqual(0, duplicate_count)
        self.assertEqual(1, other_run_count)
        self.assertEqual(2, len(rows))

    def test_header_written_once_and_schema_order(self):
        append_watchlist_rows(
            [self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        append_watchlist_rows(
            [self.candidate("DUOL")],
            "20260522T230801123Z",
            "v1.1.1",
            "US",
            "USD",
            "2026-05-22T23:08:01.123Z",
            path=self.path,
        )

        lines = self.read_lines()
        self.assertEqual(WATCHLIST_LOG_FIELDS, lines[0].split(","))
        self.assertEqual(27, len(lines[0].split(",")))
        self.assertEqual(1, sum(1 for line in lines if line == lines[0]))

    def test_excluded_columns_absent(self):
        excluded = {
            "reason",
            "exchange",
            "signal_type",
            "observation_type",
            "risk_flags",
            "verdict",
        }

        self.assertTrue(excluded.isdisjoint(WATCHLIST_LOG_FIELDS))

    def test_missing_fetch_timestamps_are_blank(self):
        append_watchlist_rows(
            [self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        row = self.read_rows()[0]
        self.assertEqual("", row["price_fetched_at"])
        self.assertEqual("", row["fundamentals_fetched_at"])
        self.assertNotEqual(self.created_at_utc, row["price_fetched_at"])
        self.assertNotEqual(self.created_at_utc, row["fundamentals_fetched_at"])

    def test_market_currency_default_us_usd_are_recorded(self):
        append_watchlist_rows(
            [self.candidate("NVO")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        row = self.read_rows()[0]
        self.assertEqual("US", row["market"])
        self.assertEqual("USD", row["currency"])

    def test_created_at_and_run_id_are_consistent_for_one_call(self):
        run_timestamp_utc = datetime(2026, 5, 22, 23, 8, 0, 123456, tzinfo=timezone.utc)
        created_at_utc = format_created_at_utc(run_timestamp_utc)
        run_id = build_run_id(run_timestamp_utc)

        append_watchlist_rows(
            [self.candidate("NVO"), self.candidate("DUOL")],
            run_id,
            "v1.1.1",
            "US",
            "USD",
            created_at_utc,
            path=self.path,
        )

        rows = self.read_rows()
        self.assertEqual("2026-05-22T23:08:00.123Z", created_at_utc)
        self.assertEqual("20260522T230800123Z", run_id)
        self.assertEqual({created_at_utc}, {row["created_at_utc"] for row in rows})
        self.assertEqual({run_id}, {row["run_id"] for row in rows})

    def test_prior_observation_count_uses_one_existing_snapshot(self):
        append_watchlist_rows(
            [self.candidate("NVO")],
            "20260521T230800123Z",
            "v1.1.1",
            "US",
            "USD",
            "2026-05-21T23:08:00.123Z",
            path=self.path,
        )

        with patch.object(
            watchlist_logger,
            "load_existing_observation_counts",
            wraps=watchlist_logger.load_existing_observation_counts,
        ) as load_mock:
            append_count = append_watchlist_rows(
                [self.candidate("NVO"), self.candidate("DUOL")],
                self.run_id,
                "v1.1.1",
                "US",
                "USD",
                self.created_at_utc,
                path=self.path,
            )

        rows = self.read_rows()
        self.assertEqual(2, append_count)
        self.assertEqual(1, load_mock.call_count)
        self.assertEqual("1", rows[1]["prior_observation_count"])
        self.assertEqual("0", rows[2]["prior_observation_count"])

    def test_empty_candidates_create_header_only_and_return_zero(self):
        append_count = append_watchlist_rows(
            [],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        original_lines = self.read_lines()
        second_count = append_watchlist_rows(
            [],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        self.assertEqual(0, append_count)
        self.assertEqual(0, second_count)
        self.assertEqual([",".join(WATCHLIST_LOG_FIELDS)], original_lines)
        self.assertEqual(original_lines, self.read_lines())

    def test_areas_normalization_values_and_nan_handling(self):
        self.assertEqual("A,C,D", normalize_areas(["D", "A", "C", "A"]))
        self.assertEqual("A,C,D", normalize_areas("D, A,C"))
        self.assertEqual("", normalize_areas(None))
        self.assertEqual("", normalize_areas(float("nan")))

        append_watchlist_rows(
            [
                self.candidate("LIST", areas=["D", "A", "C", "A"]),
                self.candidate("TEXT", areas="D, A,C"),
                self.candidate("NONE", areas=float("nan")),
            ],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        rows = self.read_rows()
        self.assertEqual(["A,C,D", "A,C,D", ""], [row["areas"] for row in rows])

    def test_zero_candidate_success_flow_can_call_append_empty(self):
        with patch.object(telegram_reporter, "send_telegram", return_value=True):
            success, append_count = telegram_reporter.send_telegram_and_append_watchlist_log(
                "token",
                "chat",
                "관찰 후보 없음",
                [],
                self.run_id,
                self.created_at_utc,
                path=self.path,
            )

        self.assertTrue(success)
        self.assertEqual(0, append_count)
        self.assertEqual([",".join(WATCHLIST_LOG_FIELDS)], self.read_lines())

    def test_append_watchlist_rows_return_values(self):
        new_count = append_watchlist_rows(
            [self.candidate("NVO"), self.candidate("DUOL")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        empty_count = append_watchlist_rows(
            [],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        all_duplicate_count = append_watchlist_rows(
            [self.candidate("NVO"), self.candidate("DUOL")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )
        partial_count = append_watchlist_rows(
            [self.candidate("NVO"), self.candidate("NOW")],
            self.run_id,
            "v1.1.1",
            "US",
            "USD",
            self.created_at_utc,
            path=self.path,
        )

        self.assertEqual(2, new_count)
        self.assertEqual(0, empty_count)
        self.assertEqual(0, all_duplicate_count)
        self.assertEqual(1, partial_count)

    def test_schema_preflight_rejects_legacy_header_without_modifying_file(self):
        self.write_legacy_watchlist_log()
        before = self.read_lines()

        with self.assertRaises(ValueError):
            validate_watchlist_log_header(self.path)

        self.assertEqual(before, self.read_lines())

    def test_append_watchlist_rows_rejects_legacy_header_without_modifying_file(self):
        self.write_legacy_watchlist_log()
        before = self.read_lines()

        with self.assertRaises(ValueError):
            append_watchlist_rows(
                [self.candidate("NVO")],
                self.run_id,
                "v1.1.1",
                "US",
                "USD",
                self.created_at_utc,
                path=self.path,
            )

        self.assertEqual(before, self.read_lines())

    def test_legacy_header_preflight_blocks_telegram_send_and_preserves_file(self):
        self.write_legacy_watchlist_log()
        before = self.read_lines()

        with patch.object(telegram_reporter, "send_telegram") as send_mock:
            with self.assertRaises(ValueError):
                telegram_reporter.send_telegram_and_append_watchlist_log(
                    "token",
                    "chat",
                    "message",
                    [self.candidate("NVO")],
                    self.run_id,
                    self.created_at_utc,
                    path=self.path,
                )

        send_mock.assert_not_called()
        self.assertEqual(before, self.read_lines())

    def test_append_exception_after_successful_send_is_not_hidden(self):
        with patch.object(telegram_reporter, "send_telegram", return_value=True) as send_mock:
            with patch.object(
                telegram_reporter,
                "append_watchlist_rows",
                side_effect=RuntimeError("append failed"),
            ):
                with self.assertRaises(RuntimeError):
                    telegram_reporter.send_telegram_and_append_watchlist_log(
                        "token",
                        "chat",
                        "message",
                        [self.candidate("NVO")],
                        self.run_id,
                        self.created_at_utc,
                        path=self.path,
                    )

        send_mock.assert_called_once()

if __name__ == "__main__":
    unittest.main()
