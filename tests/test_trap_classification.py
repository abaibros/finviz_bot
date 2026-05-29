import unittest

from trap_classification import (
    AUXILIARY,
    FATAL,
    TRAP_ORDER,
    classify_trap,
    summarize_traps,
)


class TrapClassificationTests(unittest.TestCase):
    def test_c_i_b_f_major_are_fatal(self):
        for trap_code in ("C", "I", "B", "F_MAJOR"):
            with self.subTest(trap_code=trap_code):
                result = classify_trap(trap_code)

                self.assertEqual(trap_code, result["trap_code"])
                self.assertEqual(FATAL, result["trap_type"])
                self.assertTrue(result["is_fatal"])

    def test_auxiliary_traps_are_auxiliary(self):
        for trap_code in ("A", "D", "E", "F_MINOR", "G", "H", "J"):
            with self.subTest(trap_code=trap_code):
                result = classify_trap(trap_code)

                self.assertEqual(trap_code, result["trap_code"])
                self.assertEqual(AUXILIARY, result["trap_type"])
                self.assertFalse(result["is_fatal"])

    def test_classify_trap_rejects_bare_f(self):
        with self.assertRaises(ValueError):
            classify_trap("F")

    def test_summarize_traps_rejects_bare_f(self):
        with self.assertRaises(ValueError):
            summarize_traps(["F"])

    def test_unknown_trap_code_raises_value_error(self):
        with self.assertRaises(ValueError):
            classify_trap("UNKNOWN")

        with self.assertRaises(ValueError):
            summarize_traps(["A", "UNKNOWN"])

    def test_duplicate_trap_code_raises_value_error(self):
        with self.assertRaises(ValueError):
            summarize_traps(["B", "B"])

    def test_empty_list_is_valid(self):
        result = summarize_traps([])

        self.assertEqual(0, result["fatal_trap_count"])
        self.assertEqual(0, result["auxiliary_trap_count"])
        self.assertEqual([], result["fatal_traps"])
        self.assertEqual([], result["auxiliary_traps"])
        self.assertIsNone(result["highest_priority_rank"])
        self.assertEqual([], result["highest_priority_traps"])
        self.assertFalse(result["has_fatal_trap"])

    def test_all_fatal_traps_count_to_four(self):
        result = summarize_traps(["C", "I", "B", "F_MAJOR"])

        self.assertEqual(4, result["fatal_trap_count"])
        self.assertEqual(["C", "I", "B", "F_MAJOR"], result["fatal_traps"])
        self.assertTrue(result["has_fatal_trap"])

    def test_all_auxiliary_traps_count_to_seven(self):
        result = summarize_traps(["A", "D", "E", "F_MINOR", "G", "H", "J"])

        self.assertEqual(7, result["auxiliary_trap_count"])
        self.assertEqual(["A", "H", "D", "F_MINOR", "G", "E", "J"], result["auxiliary_traps"])
        self.assertFalse(result["has_fatal_trap"])

    def test_a_h_share_priority_rank_five(self):
        result = summarize_traps(["A", "H"])

        self.assertEqual(5, result["highest_priority_rank"])
        self.assertEqual(["A", "H"], result["highest_priority_traps"])

    def test_e_g_f_minor_share_priority_rank_seven_in_trap_order(self):
        result = summarize_traps(["E", "G", "F_MINOR"])

        self.assertEqual(7, result["highest_priority_rank"])
        self.assertEqual(["F_MINOR", "G", "E"], result["highest_priority_traps"])

    def test_j_d_b_highest_priority_is_b(self):
        result = summarize_traps(["J", "D", "B"])

        self.assertEqual(3, result["highest_priority_rank"])
        self.assertEqual(["B"], result["highest_priority_traps"])

    def test_f_major_beats_a_h(self):
        result = summarize_traps(["F_MAJOR", "A", "H"])

        self.assertEqual(4, result["highest_priority_rank"])
        self.assertEqual(["F_MAJOR"], result["highest_priority_traps"])

    def test_fatal_trap_count_matches_fatal_traps_length(self):
        result = summarize_traps(["J", "C", "F_MINOR", "B"])

        self.assertEqual(len(result["fatal_traps"]), result["fatal_trap_count"])

    def test_trap_lists_are_sorted_by_trap_order(self):
        result = summarize_traps(["J", "A", "F_MAJOR", "D", "I", "E"])

        self.assertEqual(["I", "F_MAJOR"], result["fatal_traps"])
        self.assertEqual(["A", "D", "E", "J"], result["auxiliary_traps"])
        self.assertEqual(
            sorted(result["fatal_traps"], key=TRAP_ORDER.index),
            result["fatal_traps"],
        )
        self.assertEqual(
            sorted(result["auxiliary_traps"], key=TRAP_ORDER.index),
            result["auxiliary_traps"],
        )

    def test_highest_priority_traps_are_sorted_by_trap_order(self):
        result = summarize_traps(["G", "E", "F_MINOR"])

        self.assertEqual(
            sorted(result["highest_priority_traps"], key=TRAP_ORDER.index),
            result["highest_priority_traps"],
        )

    def test_summarize_traps_rejects_non_list_input(self):
        with self.assertRaises(ValueError):
            summarize_traps(("A", "B"))


if __name__ == "__main__":
    unittest.main()
