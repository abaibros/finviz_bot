import unittest

from gate2_recovery_profile import (
    ACTIVE_NEGATIVE,
    CLEAR_VERIFIED,
    COVERAGE_UNKNOWN,
    FAIL,
    INSUFFICIENT_DATA,
    MANUAL_REVIEW,
    MATERIALITY_UNKNOWN,
    PASS,
    PASS_FULL,
    PASS_RECOVERY_PROFILE,
)
from tier_classification import (
    MANUAL_REVIEW_2G_ELIGIBLE,
    MID,
    STRONG,
    evaluate_manual_review_2g_eligible,
    is_tier1_eligible,
    is_tier2_eligible,
)


def manual_review_2g_input(**overrides):
    values = {
        "market_cap_usd_b": 50.0,
        "debt_to_equity_pct": 300.0,
        "non_gaap_profit_turnaround_recent_2q": True,
        "moving_toward_profitability": False,
    }
    values.update(overrides)
    return values


def tier1_input(**overrides):
    values = {
        "gate1_status": PASS,
        "gate2_status": PASS_FULL,
        "gate3_status": PASS,
        "gate4_status": PASS,
        "fatal_trap_count": 0,
        "f3_strength": STRONG,
        "entry_block": False,
    }
    values.update(overrides)
    return values


def tier2_input(**overrides):
    values = {
        "gate1_status": MANUAL_REVIEW_2G_ELIGIBLE,
        "gate2_status": PASS_RECOVERY_PROFILE,
        "gate3_status": PASS,
        "gate4_status": PASS,
        "filter_f1": PASS,
        "filter_f2": PASS,
        "filter_f3": PASS,
        "filter_f4": PASS,
        "filter_f5": PASS,
        "negative_status": CLEAR_VERIFIED,
        "fatal_trap_count": 0,
        "entry_block": False,
    }
    values.update(overrides)
    return values


class TierClassificationTests(unittest.TestCase):
    def evaluate_manual_review_2g(self, **overrides):
        return evaluate_manual_review_2g_eligible(**manual_review_2g_input(**overrides))

    def evaluate_tier1(self, **overrides):
        return is_tier1_eligible(**tier1_input(**overrides))

    def evaluate_tier2(self, **overrides):
        return is_tier2_eligible(**tier2_input(**overrides))

    def test_manual_review_2g_eligible_happy_path_non_gaap(self):
        result = self.evaluate_manual_review_2g(
            market_cap_usd_b=50.0,
            debt_to_equity_pct=300.0,
            non_gaap_profit_turnaround_recent_2q=True,
            moving_toward_profitability=False,
        )

        self.assertEqual(MANUAL_REVIEW_2G_ELIGIBLE, result)

    def test_manual_review_2g_eligible_happy_path_moving_toward_profitability(self):
        result = self.evaluate_manual_review_2g(
            non_gaap_profit_turnaround_recent_2q=False,
            moving_toward_profitability=True,
        )

        self.assertEqual(MANUAL_REVIEW_2G_ELIGIBLE, result)

    def test_manual_review_2g_eligible_happy_path_both_profitability_flags(self):
        result = self.evaluate_manual_review_2g(
            non_gaap_profit_turnaround_recent_2q=True,
            moving_toward_profitability=True,
        )

        self.assertEqual(MANUAL_REVIEW_2G_ELIGIBLE, result)

    def test_manual_review_2g_rejects_no_profitability_progress(self):
        result = self.evaluate_manual_review_2g(
            non_gaap_profit_turnaround_recent_2q=False,
            moving_toward_profitability=False,
        )

        self.assertEqual(FAIL, result)

    def test_manual_review_2g_rejects_small_market_cap(self):
        result = self.evaluate_manual_review_2g(market_cap_usd_b=49.9)

        self.assertEqual(FAIL, result)

    def test_manual_review_2g_rejects_high_debt(self):
        result = self.evaluate_manual_review_2g(debt_to_equity_pct=300.1)

        self.assertEqual(FAIL, result)

    def test_manual_review_2g_rejects_invalid_numeric_inputs(self):
        invalid_cases = (
            {"market_cap_usd_b": "50.0"},
            {"market_cap_usd_b": True},
            {"debt_to_equity_pct": "300.0"},
            {"debt_to_equity_pct": False},
        )

        for overrides in invalid_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    self.evaluate_manual_review_2g(**overrides)

    def test_manual_review_2g_rejects_invalid_profitability_flags(self):
        invalid_cases = (
            {"non_gaap_profit_turnaround_recent_2q": "true"},
            {"non_gaap_profit_turnaround_recent_2q": 1},
            {"moving_toward_profitability": "false"},
            {"moving_toward_profitability": 0},
        )

        for overrides in invalid_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    self.evaluate_manual_review_2g(**overrides)

    def test_tier1_happy_path(self):
        result = self.evaluate_tier1()

        self.assertTrue(result)

    def test_tier1_rejects_recovery_profile(self):
        result = self.evaluate_tier1(gate2_status=PASS_RECOVERY_PROFILE)

        self.assertFalse(result)

    def test_tier1_rejects_manual_review_2g_eligible_input(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier1(gate1_status=MANUAL_REVIEW_2G_ELIGIBLE)

    def test_tier1_rejects_entry_block(self):
        result = self.evaluate_tier1(entry_block=True)

        self.assertFalse(result)

    def test_tier1_rejects_fatal_trap(self):
        result = self.evaluate_tier1(fatal_trap_count=1)

        self.assertFalse(result)

    def test_tier1_rejects_two_fatal_traps(self):
        result = self.evaluate_tier1(fatal_trap_count=2)

        self.assertFalse(result)

    def test_tier1_rejects_negative_fatal_trap_count(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier1(fatal_trap_count=-1)

    def test_tier1_requires_f3_strong(self):
        result = self.evaluate_tier1(f3_strength=MID)

        self.assertFalse(result)

    def test_tier1_requires_all_gates_pass(self):
        for overrides in (
            {"gate1_status": MANUAL_REVIEW},
            {"gate3_status": MANUAL_REVIEW},
            {"gate4_status": MANUAL_REVIEW},
        ):
            with self.subTest(overrides=overrides):
                result = self.evaluate_tier1(**overrides)

                self.assertFalse(result)

    def test_tier1_rejects_when_multiple_conditions_fail(self):
        result = self.evaluate_tier1(
            gate2_status=PASS_RECOVERY_PROFILE,
            entry_block=True,
            fatal_trap_count=2,
        )

        self.assertFalse(result)

    def test_tier2_happy_path_with_pass_recovery_profile(self):
        result = self.evaluate_tier2(
            gate1_status=MANUAL_REVIEW_2G_ELIGIBLE,
            gate2_status=PASS_RECOVERY_PROFILE,
        )

        self.assertTrue(result)

    def test_tier2_allows_pass_full(self):
        result = self.evaluate_tier2(gate2_status=PASS_FULL)

        self.assertTrue(result)

    def test_tier2_rejects_gate1_fail(self):
        result = self.evaluate_tier2(gate1_status=FAIL)

        self.assertFalse(result)

    def test_tier2_rejects_generic_manual_review_gate1(self):
        result = self.evaluate_tier2(gate1_status=MANUAL_REVIEW)

        self.assertFalse(result)

    def test_tier2_rejects_gate3_not_pass(self):
        result = self.evaluate_tier2(gate3_status=MANUAL_REVIEW)

        self.assertFalse(result)

    def test_tier2_allows_gate4_manual_review(self):
        result = self.evaluate_tier2(gate4_status=MANUAL_REVIEW)

        self.assertTrue(result)

    def test_tier2_rejects_filter_fail(self):
        filter_overrides = (
            {"filter_f1": FAIL},
            {"filter_f2": FAIL},
            {"filter_f3": FAIL},
            {"filter_f4": FAIL},
            {"filter_f5": FAIL},
        )

        for overrides in filter_overrides:
            with self.subTest(overrides=overrides):
                result = self.evaluate_tier2(**overrides)

                self.assertFalse(result)

    def test_tier2_rejects_active_negative(self):
        result = self.evaluate_tier2(
            gate2_status=PASS_FULL,
            negative_status=ACTIVE_NEGATIVE,
        )

        self.assertFalse(result)

    def test_tier2_rejects_entry_block(self):
        result = self.evaluate_tier2(entry_block=True)

        self.assertFalse(result)

    def test_tier2_rejects_fatal_trap(self):
        result = self.evaluate_tier2(fatal_trap_count=1)

        self.assertFalse(result)

    def test_tier2_rejects_negative_fatal_trap_count(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(fatal_trap_count=-1)

    def test_tier2_rejects_when_active_negative_overrides_pass(self):
        result = self.evaluate_tier2(
            gate2_status=PASS_FULL,
            negative_status=ACTIVE_NEGATIVE,
        )

        self.assertFalse(result)

    def test_tier2_rejects_when_multiple_conditions_fail(self):
        result = self.evaluate_tier2(
            gate1_status=FAIL,
            filter_f3=FAIL,
            entry_block=True,
            fatal_trap_count=1,
        )

        self.assertFalse(result)

    def test_invalid_enum_value_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(negative_status="NOT_A_NEGATIVE_STATUS")

    def test_tier1_rejects_bool_fatal_trap_count(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier1(fatal_trap_count=True)

    def test_tier2_rejects_bool_entry_block(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(entry_block=0)

    def test_tier2_pass_full_allows_materiality_unknown_negative(self):
        result = self.evaluate_tier2(
            gate2_status=PASS_FULL,
            negative_status=MATERIALITY_UNKNOWN,
        )

        self.assertTrue(result)

    def test_tier2_pass_full_allows_coverage_unknown_negative(self):
        result = self.evaluate_tier2(
            gate2_status=PASS_FULL,
            negative_status=COVERAGE_UNKNOWN,
        )

        self.assertTrue(result)

    def test_tier2_recovery_profile_with_materiality_unknown_raises(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(
                gate2_status=PASS_RECOVERY_PROFILE,
                negative_status=MATERIALITY_UNKNOWN,
            )

    def test_tier2_recovery_profile_with_coverage_unknown_raises(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(
                gate2_status=PASS_RECOVERY_PROFILE,
                negative_status=COVERAGE_UNKNOWN,
            )

    def test_tier2_recovery_profile_with_active_negative_raises(self):
        with self.assertRaises(ValueError):
            self.evaluate_tier2(
                gate2_status=PASS_RECOVERY_PROFILE,
                negative_status=ACTIVE_NEGATIVE,
            )

    def test_tier2_rejects_insufficient_data_filter(self):
        result = self.evaluate_tier2(filter_f4=INSUFFICIENT_DATA)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
