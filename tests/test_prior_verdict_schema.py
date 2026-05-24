import csv
import inspect
import os
import shutil
import unittest
import uuid

from prior_verdict_schema import (
    ALLOWED_SOURCES,
    ALLOWED_VERDICTS,
    PRIOR_VERDICT_FIELDS,
    append_prior_verdict_rows,
    validate_created_at_utc,
    validate_date_yyyy_mm_dd,
    validate_prior_verdict_csv,
    validate_source,
    validate_verdict,
)


class PriorVerdictSchemaTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = os.path.join(os.getcwd(), f"test_prior_verdict_tmp_{uuid.uuid4().hex}")
        os.makedirs(self.tmp_dir)
        self.path = os.path.join(self.tmp_dir, "prior_verdict_log.csv")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def sample_row(self, ticker="TEST", verdict="HOLD", run_id="run-1"):
        return {
            "created_at_utc": "2026-05-25T03:00:00.000Z",
            "verdict_date": "2026-05-25",
            "run_id": run_id,
            "ticker": ticker,
            "verdict": verdict,
            "prior_score": "67.5",
            "alert_count": "2",
            "source": "manual",
            "reviewer": "user",
            "note": "fixture row",
            "review_after": "",
        }

    def read_lines(self, path=None):
        with open(path or self.path, "r", encoding="utf-8", newline="") as csvfile:
            return csvfile.read().splitlines()

    def read_rows(self, path=None):
        with open(path or self.path, "r", encoding="utf-8", newline="") as csvfile:
            return list(csv.DictReader(csvfile))

    def test_fields_order_matches_repo_csv_header(self):
        with open("prior_verdict_log.csv", "r", encoding="utf-8", newline="") as csvfile:
            header = next(csv.reader(csvfile))

        self.assertEqual(PRIOR_VERDICT_FIELDS, header)

    def test_repo_prior_verdict_log_is_header_only_with_zero_rows(self):
        rows = self.read_rows("prior_verdict_log.csv")

        self.assertEqual([], rows)

    def test_repo_prior_verdict_log_csv_is_valid(self):
        validate_prior_verdict_csv("prior_verdict_log.csv")

    def test_allowed_verdicts_are_fixed_to_four_values(self):
        self.assertEqual({"HOLD", "OBSERVE", "WATCHFUL", "RESUMED"}, ALLOWED_VERDICTS)

    def test_event_completed_excluded_deprecated_are_not_allowed_verdicts(self):
        self.assertNotIn("EVENT_COMPLETED", ALLOWED_VERDICTS)
        self.assertNotIn("EXCLUDED", ALLOWED_VERDICTS)
        self.assertNotIn("DEPRECATED", ALLOWED_VERDICTS)

    def test_invalid_verdict_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_verdict("EVENT_COMPLETED")

    def test_empty_verdict_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_verdict("")

    def test_allowed_sources_pass_validation(self):
        for source in ["manual", "system", "auto"]:
            with self.subTest(source=source):
                validate_source(source)

    def test_empty_source_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_source("")

    def test_invalid_source_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_source("analyst")

    def test_valid_verdict_date_passes(self):
        validate_date_yyyy_mm_dd("2026-05-25", "verdict_date")

    def test_empty_verdict_date_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_date_yyyy_mm_dd("", "verdict_date")

    def test_invalid_verdict_date_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_date_yyyy_mm_dd("2026/05/25", "verdict_date")

    def test_valid_created_at_utc_passes(self):
        validate_created_at_utc("2026-05-25T03:00:00.000Z")

    def test_empty_created_at_utc_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_created_at_utc("")

    def test_invalid_created_at_utc_format_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_created_at_utc("2026-05-25 03:00:00")

    def test_empty_review_after_passes_row_validation(self):
        append_count = append_prior_verdict_rows([self.sample_row()], path=self.path)

        self.assertEqual(1, append_count)

    def test_valid_review_after_passes_row_validation(self):
        row = self.sample_row()
        row["review_after"] = "2026-06-25"

        append_count = append_prior_verdict_rows([row], path=self.path)

        self.assertEqual(1, append_count)

    def test_invalid_review_after_raises_value_error(self):
        row = self.sample_row()
        row["review_after"] = "2026/06/25"

        with self.assertRaises(ValueError):
            append_prior_verdict_rows([row], path=self.path)

    def test_header_only_csv_validation_succeeds(self):
        append_count = append_prior_verdict_rows([], path=self.path)

        self.assertEqual(0, append_count)
        validate_prior_verdict_csv(self.path)

    def test_append_prior_verdict_rows_returns_new_append_count_int(self):
        append_count = append_prior_verdict_rows(
            [self.sample_row("AAA"), self.sample_row("BBB")],
            path=self.path,
        )

        self.assertIsInstance(append_count, int)
        self.assertEqual(2, append_count)

    def test_duplicate_key_is_skipped(self):
        first_count = append_prior_verdict_rows(
            [self.sample_row("AAA"), self.sample_row("AAA")],
            path=self.path,
        )
        second_count = append_prior_verdict_rows(
            [self.sample_row("AAA")],
            path=self.path,
        )

        self.assertEqual(1, first_count)
        self.assertEqual(0, second_count)
        self.assertEqual(1, len(self.read_rows()))

    def test_empty_rows_creates_header_only_and_returns_zero(self):
        append_count = append_prior_verdict_rows([], path=self.path)

        self.assertEqual(0, append_count)
        self.assertEqual([",".join(PRIOR_VERDICT_FIELDS)], self.read_lines())

    def test_append_only_preserves_existing_rows(self):
        append_prior_verdict_rows([self.sample_row("AAA")], path=self.path)
        existing_line = self.read_lines()[1]

        append_count = append_prior_verdict_rows(
            [self.sample_row("BBB", run_id="run-2")],
            path=self.path,
        )

        self.assertEqual(1, append_count)
        self.assertEqual(existing_line, self.read_lines()[1])
        self.assertEqual(2, len(self.read_rows()))

    def test_append_helper_uses_append_open_mode(self):
        import prior_verdict_schema

        source = inspect.getsource(prior_verdict_schema.append_prior_verdict_rows)
        self.assertIn('open(path, "a", encoding="utf-8", newline="")', source)

    def test_repo_prior_verdict_log_has_no_initial_grnd_nvo_intu_rows(self):
        rows = self.read_rows("prior_verdict_log.csv")

        self.assertFalse({"GRND", "NVO", "INTU"} & {row.get("ticker", "") for row in rows})

    def test_append_prior_verdict_rows_rejects_bad_row_before_writing(self):
        row = self.sample_row()
        row["source"] = ""

        with self.assertRaises(ValueError):
            append_prior_verdict_rows([row], path=self.path)

        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
