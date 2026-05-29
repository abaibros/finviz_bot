import unittest

from catalyst_score_calculator import (
    ACQUIRER,
    BLOG_SOCIAL,
    FAIL,
    FUNDAMENTAL_CATALYST,
    GENERAL_NEWS,
    IMMEDIATE_REVENUE_CATALYST,
    INSUFFICIENT_DATA,
    INVALID,
    LLM_NEGATIVE,
    LLM_NEUTRAL,
    LLM_POSITIVE,
    LLM_UNCLEAR,
    MAJOR_MEDIA,
    MANUAL_REVIEW,
    NOISE,
    NOT_MNA,
    OFFICIAL,
    PASS,
    SHAREHOLDER_RETURN_CATALYST,
    STRATEGIC_CATALYST,
    TARGET,
    UNCLEAR,
    calculate_catalyst_scores,
    score_positive_event,
    validate_catalyst_event,
)


def event(**overrides):
    values = {
        "event_id": "event-1",
        "event_category": IMMEDIATE_REVENUE_CATALYST,
        "source_tier": OFFICIAL,
        "event_age_days": 10,
        "llm_classification": LLM_POSITIVE,
        "is_llm_only": False,
        "independent_source_count": 1,
        "has_official_source": True,
        "mna_role": NOT_MNA,
        "data_unit_validation_status": PASS,
        "is_independent_catalyst": True,
    }
    values.update(overrides)
    return values


class CatalystScoreCalculatorTests(unittest.TestCase):
    def calculate(self, events):
        return calculate_catalyst_scores(events)

    def test_immediate_revenue_official_scores_two(self):
        self.assertEqual(2.0, score_positive_event(event()))

    def test_fundamental_major_media_scores_one_point_two(self):
        score = score_positive_event(event(
            event_category=FUNDAMENTAL_CATALYST,
            source_tier=MAJOR_MEDIA,
        ))

        self.assertEqual(1.2, score)

    def test_strategic_general_news_scores_zero_point_five(self):
        score = score_positive_event(event(
            event_category=STRATEGIC_CATALYST,
            source_tier=GENERAL_NEWS,
        ))

        self.assertEqual(0.5, score)

    def test_shareholder_return_official_scores_zero_point_five(self):
        score = score_positive_event(event(event_category=SHAREHOLDER_RETURN_CATALYST))

        self.assertEqual(0.5, score)

    def test_noise_is_ignored_and_not_scored(self):
        result = self.calculate([event(event_category=NOISE)])

        self.assertEqual(0.0, result["cumulative_catalyst_score"])
        self.assertEqual(["event-1"], result["ignored_event_ids"])
        self.assertEqual(INSUFFICIENT_DATA, result["catalyst_component_status"])

    def test_cumulative_score_at_least_three_passes_component(self):
        result = self.calculate([
            event(event_id="event-1"),
            event(event_id="event-2", event_category=FUNDAMENTAL_CATALYST),
        ])

        self.assertEqual(3.5, result["cumulative_catalyst_score"])
        self.assertEqual(PASS, result["catalyst_component_status"])

    def test_cumulative_score_below_three_is_not_pass(self):
        result = self.calculate([event()])

        self.assertEqual(2.0, result["cumulative_catalyst_score"])
        self.assertNotEqual(PASS, result["catalyst_component_status"])

    def test_event_older_than_ninety_days_is_ignored(self):
        result = self.calculate([event(event_age_days=91)])

        self.assertEqual(["event-1"], result["ignored_event_ids"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_unclear_llm_classification_is_ignored(self):
        result = self.calculate([event(llm_classification=LLM_UNCLEAR)])

        self.assertEqual(["event-1"], result["ignored_event_ids"])

    def test_llm_only_event_is_ignored(self):
        result = self.calculate([event(is_llm_only=True)])

        self.assertEqual(["event-1"], result["ignored_event_ids"])

    def test_blog_social_single_source_fails_source_validation_and_is_not_scored(self):
        result = self.calculate([event(
            source_tier=BLOG_SOCIAL,
            independent_source_count=1,
            has_official_source=False,
        )])

        self.assertEqual(FAIL, result["source_validation_status"])
        self.assertEqual(FAIL, result["catalyst_component_status"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_official_source_passes_with_single_source_count(self):
        result = self.calculate([event(independent_source_count=1, has_official_source=True)])

        self.assertEqual(PASS, result["source_validation_status"])

    def test_two_independent_non_blog_sources_pass_source_validation(self):
        result = self.calculate([event(
            source_tier=GENERAL_NEWS,
            independent_source_count=2,
            has_official_source=False,
        )])

        self.assertEqual(PASS, result["source_validation_status"])

    def test_mna_target_is_invalid_and_not_scored(self):
        result = self.calculate([event(mna_role=TARGET)])

        self.assertEqual(["event-1"], result["invalid_event_ids"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_mna_unclear_is_manual_review_and_not_scored(self):
        result = self.calculate([event(mna_role=UNCLEAR)])

        self.assertEqual(["event-1"], result["manual_review_event_ids"])
        self.assertEqual(MANUAL_REVIEW, result["catalyst_component_status"])

    def test_mna_acquirer_can_score_when_valid(self):
        result = self.calculate([event(mna_role=ACQUIRER)])

        self.assertEqual(["event-1"], result["scored_event_ids"])
        self.assertEqual(2.0, result["cumulative_catalyst_score"])

    def test_duplicate_event_id_is_scored_once(self):
        result = self.calculate([
            event(event_id="dup"),
            event(event_id="dup", event_category=FUNDAMENTAL_CATALYST),
        ])

        self.assertEqual(["dup"], result["scored_event_ids"])
        self.assertEqual(2.0, result["cumulative_catalyst_score"])

    def test_duplicate_event_id_prefers_higher_source_multiplier(self):
        result = self.calculate([
            event(
                event_id="dup",
                event_category=STRATEGIC_CATALYST,
                source_tier=GENERAL_NEWS,
                independent_source_count=2,
                has_official_source=False,
            ),
            event(
                event_id="dup",
                event_category=STRATEGIC_CATALYST,
                source_tier=MAJOR_MEDIA,
                independent_source_count=2,
                has_official_source=False,
            ),
        ])

        self.assertEqual(0.8, result["cumulative_catalyst_score"])

    def test_independent_catalyst_score_is_max_independent_event_score(self):
        result = self.calculate([
            event(event_id="independent-1", event_category=STRATEGIC_CATALYST),
            event(event_id="independent-2"),
            event(
                event_id="not-independent",
                event_category=FUNDAMENTAL_CATALYST,
                is_independent_catalyst=False,
            ),
        ])

        self.assertEqual(2.0, result["independent_catalyst_score"])

    def test_non_independent_event_is_excluded_from_independent_score(self):
        result = self.calculate([event(is_independent_catalyst=False)])

        self.assertEqual(0.0, result["independent_catalyst_score"])

    def test_data_unit_invalid_aggregates_invalid(self):
        result = self.calculate([event(data_unit_validation_status=INVALID)])

        self.assertEqual(INVALID, result["data_unit_validation_status"])

    def test_data_unit_insufficient_aggregates_insufficient(self):
        result = self.calculate([event(data_unit_validation_status=INSUFFICIENT_DATA)])

        self.assertEqual(INSUFFICIENT_DATA, result["data_unit_validation_status"])

    def test_data_unit_manual_review_aggregates_manual_review(self):
        result = self.calculate([event(data_unit_validation_status=MANUAL_REVIEW)])

        self.assertEqual(MANUAL_REVIEW, result["data_unit_validation_status"])

    def test_negative_neutral_unclear_events_are_ignored(self):
        result = self.calculate([
            event(event_id="negative", llm_classification=LLM_NEGATIVE),
            event(event_id="neutral", llm_classification=LLM_NEUTRAL),
            event(event_id="unclear", llm_classification=LLM_UNCLEAR),
        ])

        self.assertEqual(["negative", "neutral", "unclear"], result["ignored_event_ids"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_invalid_enum_value_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculate([event(event_category="BAD_CATEGORY")])

    def test_events_must_be_list(self):
        with self.assertRaises(ValueError):
            self.calculate("not-a-list")

    def test_event_must_be_dict(self):
        with self.assertRaises(ValueError):
            self.calculate(["not-a-dict"])

    def test_missing_required_field_raises_value_error(self):
        bad_event = event()
        del bad_event["source_tier"]

        with self.assertRaises(ValueError):
            self.calculate([bad_event])

    def test_empty_event_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.calculate([event(event_id="")])

    def test_bool_fields_reject_non_bool_values(self):
        for overrides in (
            {"is_llm_only": "False"},
            {"has_official_source": 1},
            {"is_independent_catalyst": "True"},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    self.calculate([event(**overrides)])

    def test_int_fields_reject_bool_and_negative_values(self):
        for overrides in (
            {"event_age_days": True},
            {"event_age_days": -1},
            {"independent_source_count": False},
            {"independent_source_count": -1},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    self.calculate([event(**overrides)])

    def test_duplicate_event_id_all_invalid_is_not_scored(self):
        result = self.calculate([
            event(event_id="dup", mna_role=TARGET),
            event(event_id="dup", mna_role=TARGET, event_category=FUNDAMENTAL_CATALYST),
        ])

        self.assertEqual(["dup"], result["invalid_event_ids"])
        self.assertEqual([], result["scored_event_ids"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_source_validation_fail_prevents_component_pass(self):
        result = self.calculate([event(
            source_tier=BLOG_SOCIAL,
            independent_source_count=0,
            has_official_source=False,
        )])

        self.assertEqual(FAIL, result["source_validation_status"])
        self.assertNotEqual(PASS, result["catalyst_component_status"])

    def test_manual_review_only_without_score_routes_component_manual_review(self):
        result = self.calculate([event(mna_role=UNCLEAR)])

        self.assertEqual(MANUAL_REVIEW, result["catalyst_component_status"])

    def test_empty_input_returns_insufficient_data(self):
        result = self.calculate([])

        self.assertEqual(0.0, result["cumulative_catalyst_score"])
        self.assertEqual(0.0, result["independent_catalyst_score"])
        self.assertEqual(INSUFFICIENT_DATA, result["catalyst_component_status"])
        self.assertEqual(INSUFFICIENT_DATA, result["source_validation_status"])
        self.assertEqual(INSUFFICIENT_DATA, result["data_unit_validation_status"])
        self.assertEqual([], result["scored_event_ids"])
        self.assertEqual([], result["ignored_event_ids"])
        self.assertEqual([], result["manual_review_event_ids"])
        self.assertEqual([], result["invalid_event_ids"])

    def test_data_unit_invalid_beats_manual_review(self):
        result = self.calculate([
            event(event_id="invalid", data_unit_validation_status=INVALID),
            event(event_id="manual", data_unit_validation_status=MANUAL_REVIEW),
        ])

        self.assertEqual(INVALID, result["data_unit_validation_status"])

    def test_data_unit_insufficient_beats_manual_review(self):
        result = self.calculate([
            event(event_id="insufficient", data_unit_validation_status=INSUFFICIENT_DATA),
            event(event_id="manual", data_unit_validation_status=MANUAL_REVIEW),
        ])

        self.assertEqual(INSUFFICIENT_DATA, result["data_unit_validation_status"])

    def test_no_scoring_candidate_with_manual_review_ids_routes_source_manual_review(self):
        result = self.calculate([event(mna_role=UNCLEAR)])

        self.assertEqual(MANUAL_REVIEW, result["source_validation_status"])

    def test_no_scoring_candidate_without_manual_review_ids_routes_source_insufficient(self):
        result = self.calculate([event(llm_classification=LLM_NEUTRAL)])

        self.assertEqual(INSUFFICIENT_DATA, result["source_validation_status"])

    def test_ignored_events_only_route_component_insufficient(self):
        result = self.calculate([event(llm_classification=LLM_NEUTRAL)])

        self.assertEqual(INSUFFICIENT_DATA, result["catalyst_component_status"])

    def test_mna_unclear_only_routes_component_manual_review(self):
        result = self.calculate([event(mna_role=UNCLEAR)])

        self.assertEqual(MANUAL_REVIEW, result["catalyst_component_status"])

    def test_cumulative_above_threshold_with_invalid_data_does_not_pass_component(self):
        result = self.calculate([
            event(event_id="valid-1"),
            event(event_id="valid-2", event_category=FUNDAMENTAL_CATALYST),
            event(event_id="invalid", data_unit_validation_status=INVALID),
        ])

        self.assertEqual(3.5, result["cumulative_catalyst_score"])
        self.assertEqual(INVALID, result["data_unit_validation_status"])
        self.assertNotEqual(PASS, result["catalyst_component_status"])

    def test_source_fail_does_not_pass_component(self):
        result = self.calculate([
            event(
                source_tier=BLOG_SOCIAL,
                independent_source_count=0,
                has_official_source=False,
            )
        ])

        self.assertEqual(FAIL, result["source_validation_status"])
        self.assertNotEqual(PASS, result["catalyst_component_status"])

    def test_independent_bool_is_type_checked_without_cross_field_meaning_check(self):
        result = self.calculate([
            event(event_category=FUNDAMENTAL_CATALYST, is_independent_catalyst=True)
        ])

        self.assertEqual(1.5, result["independent_catalyst_score"])

    def test_duplicate_representation_prefers_non_ignored_event_first(self):
        result = self.calculate([
            event(event_id="dup", event_age_days=91),
            event(event_id="dup", event_category=SHAREHOLDER_RETURN_CATALYST),
        ])

        self.assertEqual(["dup"], result["scored_event_ids"])
        self.assertEqual(0.5, result["cumulative_catalyst_score"])

    def test_duplicate_representation_prefers_data_pass_second(self):
        result = self.calculate([
            event(event_id="dup", data_unit_validation_status=INVALID),
            event(event_id="dup", event_category=SHAREHOLDER_RETURN_CATALYST),
        ])

        self.assertEqual(0.5, result["cumulative_catalyst_score"])
        self.assertEqual(PASS, result["data_unit_validation_status"])

    def test_duplicate_representation_prefers_official_source_third(self):
        result = self.calculate([
            event(
                event_id="dup",
                source_tier=MAJOR_MEDIA,
                independent_source_count=2,
                has_official_source=False,
            ),
            event(
                event_id="dup",
                event_category=SHAREHOLDER_RETURN_CATALYST,
                has_official_source=True,
            ),
        ])

        self.assertEqual(0.5, result["cumulative_catalyst_score"])

    def test_duplicate_representation_prefers_higher_source_multiplier_fourth(self):
        result = self.calculate([
            event(
                event_id="dup",
                event_category=STRATEGIC_CATALYST,
                source_tier=GENERAL_NEWS,
                independent_source_count=2,
                has_official_source=False,
            ),
            event(
                event_id="dup",
                event_category=STRATEGIC_CATALYST,
                source_tier=MAJOR_MEDIA,
                independent_source_count=2,
                has_official_source=False,
            ),
        ])

        self.assertEqual(0.8, result["cumulative_catalyst_score"])

    def test_duplicate_representation_prefers_higher_event_score_fifth(self):
        result = self.calculate([
            event(event_id="dup", event_category=SHAREHOLDER_RETURN_CATALYST),
            event(event_id="dup", event_category=IMMEDIATE_REVENUE_CATALYST),
        ])

        self.assertEqual(2.0, result["cumulative_catalyst_score"])

    def test_duplicate_representation_prefers_lower_age_sixth(self):
        result = self.calculate([
            event(event_id="dup", event_age_days=20, is_independent_catalyst=False),
            event(event_id="dup", event_age_days=10, is_independent_catalyst=True),
        ])

        self.assertEqual(2.0, result["independent_catalyst_score"])

    def test_duplicate_representation_uses_input_order_on_full_tie_seventh(self):
        result = self.calculate([
            event(event_id="dup", is_independent_catalyst=True),
            event(event_id="dup", is_independent_catalyst=False),
        ])

        self.assertEqual(2.0, result["independent_catalyst_score"])

    def test_source_pass_and_fail_mix_routes_source_status_pass(self):
        result = self.calculate([
            event(event_id="pass"),
            event(
                event_id="fail",
                source_tier=BLOG_SOCIAL,
                independent_source_count=0,
                has_official_source=False,
            ),
        ])

        self.assertEqual(PASS, result["source_validation_status"])
        self.assertEqual(["pass"], result["scored_event_ids"])

    def test_source_validation_fail_event_is_not_scored(self):
        result = self.calculate([
            event(
                source_tier=BLOG_SOCIAL,
                independent_source_count=0,
                has_official_source=False,
            )
        ])

        self.assertEqual([], result["scored_event_ids"])
        self.assertEqual(0.0, result["cumulative_catalyst_score"])

    def test_all_source_validation_fail_routes_source_status_fail(self):
        result = self.calculate([
            event(
                event_id="fail-1",
                source_tier=BLOG_SOCIAL,
                independent_source_count=0,
                has_official_source=False,
            ),
            event(
                event_id="fail-2",
                source_tier=GENERAL_NEWS,
                independent_source_count=1,
                has_official_source=False,
            ),
        ])

        self.assertEqual(FAIL, result["source_validation_status"])

    def test_validate_catalyst_event_reports_scoring_candidate_fields(self):
        result = validate_catalyst_event(event())

        self.assertEqual("event-1", result["event_id"])
        self.assertEqual(2.0, result["event_score"])
        self.assertFalse(result["is_ignored"])
        self.assertTrue(result["is_positive_candidate"])
        self.assertTrue(result["is_scoring_candidate"])
        self.assertEqual(PASS, result["source_validation_status"])


if __name__ == "__main__":
    unittest.main()
