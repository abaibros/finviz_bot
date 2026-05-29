import unittest

from gate2_recovery_profile import (
    ACTIVE_NEGATIVE,
    CLEAR_VERIFIED,
    COVERAGE_UNKNOWN,
    F_CLEAR,
    F_MAJOR,
    F_MINOR,
    FAIL,
    FAIL_HARD_DROP,
    INSUFFICIENT_DATA,
    INSUFFICIENT_DATA_STOP,
    MANUAL_REVIEW,
    MANUAL_REVIEW_DEFERRED_RECOVERY,
    MANUAL_REVIEW_STOP,
    MATERIALITY_UNKNOWN,
    NOT_OK,
    OK,
    PASS,
    PASS_FULL,
    PASS_RECOVERY_PROFILE,
    UNRESOLVED,
    evaluate_gate2_recovery_profile,
)


def base_input(**overrides):
    values = {
        "standard_gate2_status": MANUAL_REVIEW_DEFERRED_RECOVERY,
        "gate3_recovery_status": PASS,
        "earnings_condition": PASS,
        "independent_catalyst_score": 1.5,
        "catalyst_underlying_cause": "independent_contract",
        "earnings_underlying_cause": "earnings_result",
        "negative_status": CLEAR_VERIFIED,
        "catalyst_source_confidence": OK,
        "negative_scan_coverage": CLEAR_VERIFIED,
        "eps_basis_integrity": OK,
        "trap_f_status": F_CLEAR,
        "split_share_count_basis": OK,
    }
    values.update(overrides)
    return values


class Gate2RecoveryProfileTests(unittest.TestCase):
    def evaluate(self, **overrides):
        return evaluate_gate2_recovery_profile(**base_input(**overrides))

    def test_happy_path_pass(self):
        result = self.evaluate()

        self.assertEqual(PASS_RECOVERY_PROFILE, result)

    def test_2_02_only_blocked(self):
        result = self.evaluate(
            independent_catalyst_score=0.0,
            catalyst_underlying_cause="earnings_2_02",
            earnings_underlying_cause="earnings_2_02",
        )

        self.assertNotEqual(PASS_RECOVERY_PROFILE, result)
        self.assertEqual(MANUAL_REVIEW, result)

    def test_negative_clear_not_positive(self):
        result = self.evaluate(
            earnings_condition=MANUAL_REVIEW,
            independent_catalyst_score=0.0,
        )

        self.assertEqual(MANUAL_REVIEW, result)

    def test_earnings_plus_clear_only_is_manual(self):
        result = self.evaluate(independent_catalyst_score=0.0)

        self.assertEqual(MANUAL_REVIEW, result)

    def test_weak_catalyst_blocked(self):
        for score in (1.0, 0.5):
            with self.subTest(score=score):
                result = self.evaluate(independent_catalyst_score=score)

                self.assertEqual(MANUAL_REVIEW, result)

    def test_recovery_profile_result_is_distinct_from_pass_full(self):
        recovery_result = self.evaluate()
        pass_full_result = self.evaluate(standard_gate2_status=PASS_FULL)

        self.assertEqual(PASS_RECOVERY_PROFILE, recovery_result)
        self.assertEqual(PASS_FULL, pass_full_result)
        self.assertNotEqual(pass_full_result, recovery_result)

    def test_eps_basis_integrity(self):
        result = self.evaluate(split_share_count_basis=UNRESOLVED)

        self.assertEqual(INSUFFICIENT_DATA, result)

    def test_undetected_negative_not_clear(self):
        result = self.evaluate(negative_scan_coverage=COVERAGE_UNKNOWN)

        self.assertEqual(MANUAL_REVIEW, result)

    def test_same_cause_catalyst_rejected(self):
        result = self.evaluate(
            catalyst_underlying_cause="earnings_result",
            earnings_underlying_cause="earnings_result",
        )

        self.assertEqual(MANUAL_REVIEW, result)

    def test_standard_gate2_pass_full_returns_pass_full(self):
        result = self.evaluate(standard_gate2_status=PASS_FULL)

        self.assertEqual(PASS_FULL, result)

    def test_fail_hard_drop_cannot_be_revived(self):
        result = self.evaluate(standard_gate2_status=FAIL_HARD_DROP)

        self.assertEqual(FAIL, result)

    def test_standard_manual_review_stop_routes_to_manual_review(self):
        result = self.evaluate(standard_gate2_status=MANUAL_REVIEW_STOP)

        self.assertEqual(MANUAL_REVIEW, result)

    def test_standard_insufficient_data_stop_routes_to_insufficient_data(self):
        result = self.evaluate(standard_gate2_status=INSUFFICIENT_DATA_STOP)

        self.assertEqual(INSUFFICIENT_DATA, result)

    def test_active_negative_routes_to_fail(self):
        result = self.evaluate(negative_status=ACTIVE_NEGATIVE)

        self.assertEqual(FAIL, result)

    def test_trap_f_major_routes_to_fail(self):
        result = self.evaluate(trap_f_status=F_MAJOR)

        self.assertEqual(FAIL, result)

    def test_trap_f_minor_routes_to_manual_review(self):
        result = self.evaluate(trap_f_status=F_MINOR)

        self.assertEqual(MANUAL_REVIEW, result)

    def test_invalid_enum_value_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.evaluate(gate3_recovery_status="NOT_A_STATUS")

    def test_non_numeric_independent_catalyst_score_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.evaluate(independent_catalyst_score="1.5")

    def test_priority_fail_beats_manual(self):
        result = self.evaluate(
            trap_f_status=F_MAJOR,
            negative_scan_coverage=COVERAGE_UNKNOWN,
        )

        self.assertEqual(FAIL, result)

    def test_priority_insufficient_beats_manual(self):
        result = self.evaluate(
            split_share_count_basis=UNRESOLVED,
            trap_f_status=F_MINOR,
        )

        self.assertEqual(INSUFFICIENT_DATA, result)

    def test_materiality_unknown_routes_to_manual_review(self):
        result = self.evaluate(negative_status=MATERIALITY_UNKNOWN)

        self.assertEqual(MANUAL_REVIEW, result)

    def test_source_confidence_not_ok_routes_to_manual_review(self):
        result = self.evaluate(catalyst_source_confidence=NOT_OK)

        self.assertEqual(MANUAL_REVIEW, result)


if __name__ == "__main__":
    unittest.main()
