from __future__ import annotations

from types import MappingProxyType


PASS = "PASS"
FAIL = "FAIL"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
MANUAL_REVIEW = "MANUAL_REVIEW"
INVALID = "INVALID"

IMMEDIATE_REVENUE_CATALYST = "IMMEDIATE_REVENUE_CATALYST"
FUNDAMENTAL_CATALYST = "FUNDAMENTAL_CATALYST"
STRATEGIC_CATALYST = "STRATEGIC_CATALYST"
SHAREHOLDER_RETURN_CATALYST = "SHAREHOLDER_RETURN_CATALYST"
NOISE = "NOISE"

OFFICIAL = "OFFICIAL"
MAJOR_MEDIA = "MAJOR_MEDIA"
GENERAL_NEWS = "GENERAL_NEWS"
BLOG_SOCIAL = "BLOG_SOCIAL"

LLM_POSITIVE = "positive"
LLM_NEGATIVE = "negative"
LLM_NEUTRAL = "neutral"
LLM_UNCLEAR = "unclear"

ACQUIRER = "ACQUIRER"
TARGET = "TARGET"
UNCLEAR = "UNCLEAR"
NOT_MNA = "NOT_MNA"

CATALYST_PASS_THRESHOLD = 3.0

COMMON_STATUS = frozenset({
    PASS,
    FAIL,
    INSUFFICIENT_DATA,
    MANUAL_REVIEW,
})

DATA_UNIT_STATUS = frozenset({
    PASS,
    INVALID,
    INSUFFICIENT_DATA,
    MANUAL_REVIEW,
})

POSITIVE_EVENT_CATEGORY = frozenset({
    IMMEDIATE_REVENUE_CATALYST,
    FUNDAMENTAL_CATALYST,
    STRATEGIC_CATALYST,
    SHAREHOLDER_RETURN_CATALYST,
    NOISE,
})

SOURCE_TIER = frozenset({
    OFFICIAL,
    MAJOR_MEDIA,
    GENERAL_NEWS,
    BLOG_SOCIAL,
})

LLM_CLASSIFICATION = frozenset({
    LLM_POSITIVE,
    LLM_NEGATIVE,
    LLM_NEUTRAL,
    LLM_UNCLEAR,
})

MNA_ROLE = frozenset({
    ACQUIRER,
    TARGET,
    UNCLEAR,
    NOT_MNA,
})

BASE_WEIGHTS = MappingProxyType({
    IMMEDIATE_REVENUE_CATALYST: 2.0,
    FUNDAMENTAL_CATALYST: 1.5,
    STRATEGIC_CATALYST: 1.0,
    SHAREHOLDER_RETURN_CATALYST: 0.5,
    NOISE: 0.0,
})

SOURCE_MULTIPLIERS = MappingProxyType({
    OFFICIAL: 1.0,
    MAJOR_MEDIA: 0.8,
    GENERAL_NEWS: 0.5,
    BLOG_SOCIAL: 0.3,
})

REQUIRED_EVENT_FIELDS = frozenset({
    "event_id",
    "event_category",
    "source_tier",
    "event_age_days",
    "llm_classification",
    "is_llm_only",
    "independent_source_count",
    "has_official_source",
    "mna_role",
    "data_unit_validation_status",
    "is_independent_catalyst",
})


def calculate_catalyst_scores(events: list[dict]) -> dict:
    if not isinstance(events, list):
        raise ValueError("events must be a list")

    indexed_events = [
        (index, _validate_and_copy_event(event)) for index, event in enumerate(events)
    ]
    representative_events = _deduplicate_events(indexed_events)

    ignored_event_ids = []
    manual_review_event_ids = []
    invalid_event_ids = []
    scoring_candidates = []

    for event in representative_events:
        validation = validate_catalyst_event(event)
        if validation["is_ignored"]:
            ignored_event_ids.append(event["event_id"])
        elif validation["is_invalid"]:
            invalid_event_ids.append(event["event_id"])
        elif validation["requires_manual_review"]:
            manual_review_event_ids.append(event["event_id"])
        elif validation["is_scoring_candidate"]:
            scoring_candidates.append(event)

    data_unit_validation_status = _aggregate_data_unit_status(scoring_candidates)
    source_validation_status = _aggregate_source_validation_status(
        scoring_candidates,
        manual_review_event_ids,
    )

    scored_events = [
        event
        for event in scoring_candidates
        if _validate_source(event) == PASS and event["data_unit_validation_status"] == PASS
    ]
    scored_event_ids = [event["event_id"] for event in scored_events]
    cumulative_catalyst_score = round(
        sum(score_positive_event(event) for event in scored_events),
        10,
    )
    independent_scores = [
        score_positive_event(event)
        for event in scored_events
        if event["is_independent_catalyst"]
    ]
    independent_catalyst_score = max(independent_scores, default=0.0)

    catalyst_component_status = _compute_catalyst_component_status(
        scoring_candidates=scoring_candidates,
        manual_review_event_ids=manual_review_event_ids,
        data_unit_validation_status=data_unit_validation_status,
        source_validation_status=source_validation_status,
        cumulative_catalyst_score=cumulative_catalyst_score,
        scored_event_ids=scored_event_ids,
    )

    return {
        "cumulative_catalyst_score": cumulative_catalyst_score,
        "independent_catalyst_score": independent_catalyst_score,
        "catalyst_component_status": catalyst_component_status,
        "source_validation_status": source_validation_status,
        "data_unit_validation_status": data_unit_validation_status,
        "scored_event_ids": scored_event_ids,
        "ignored_event_ids": ignored_event_ids,
        "manual_review_event_ids": manual_review_event_ids,
        "invalid_event_ids": invalid_event_ids,
    }


def validate_catalyst_event(event: dict) -> dict:
    event = _validate_and_copy_event(event)
    is_ignored = _is_ignored_event(event)
    is_invalid = not is_ignored and event["mna_role"] == TARGET
    requires_manual_review = not is_ignored and event["mna_role"] == UNCLEAR
    is_positive_candidate = (
        not is_ignored
        and not is_invalid
        and not requires_manual_review
        and event["event_category"] != NOISE
        and event["llm_classification"] == LLM_POSITIVE
        and event["is_llm_only"] is False
        and event["event_age_days"] <= 90
    )
    is_scoring_candidate = is_positive_candidate and event["mna_role"] in {ACQUIRER, NOT_MNA}
    source_validation_status = _validate_source(event) if is_scoring_candidate else None

    return {
        "event_id": event["event_id"],
        "event_score": score_positive_event(event),
        "is_ignored": is_ignored,
        "is_invalid": is_invalid,
        "requires_manual_review": requires_manual_review,
        "is_positive_candidate": is_positive_candidate,
        "is_scoring_candidate": is_scoring_candidate,
        "source_validation_status": source_validation_status,
        "data_unit_validation_status": event["data_unit_validation_status"],
    }


def score_positive_event(event: dict) -> float:
    event = _validate_and_copy_event(event)
    return round(
        BASE_WEIGHTS[event["event_category"]] * SOURCE_MULTIPLIERS[event["source_tier"]],
        10,
    )


def _validate_and_copy_event(event: dict) -> dict:
    if not isinstance(event, dict):
        raise ValueError("event must be a dict")

    missing_fields = sorted(REQUIRED_EVENT_FIELDS - event.keys())
    if missing_fields:
        raise ValueError(f"event missing required fields: {', '.join(missing_fields)}")

    copied = dict(event)
    _validate_event_id(copied["event_id"])
    _validate_enum("event_category", copied["event_category"], POSITIVE_EVENT_CATEGORY)
    _validate_enum("source_tier", copied["source_tier"], SOURCE_TIER)
    _validate_enum("llm_classification", copied["llm_classification"], LLM_CLASSIFICATION)
    _validate_enum("mna_role", copied["mna_role"], MNA_ROLE)
    _validate_enum(
        "data_unit_validation_status",
        copied["data_unit_validation_status"],
        DATA_UNIT_STATUS,
    )
    _validate_non_negative_int("event_age_days", copied["event_age_days"])
    _validate_non_negative_int("independent_source_count", copied["independent_source_count"])
    _validate_bool("is_llm_only", copied["is_llm_only"])
    _validate_bool("has_official_source", copied["has_official_source"])
    _validate_bool("is_independent_catalyst", copied["is_independent_catalyst"])
    return copied


def _validate_event_id(event_id: str) -> None:
    if not isinstance(event_id, str) or event_id == "":
        raise ValueError("event_id must be a non-empty string")


def _validate_enum(name: str, value: str, allowed_values: frozenset[str]) -> None:
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise ValueError(f"{name} must be one of: {allowed}")


def _validate_bool(name: str, value: bool) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")


def _validate_non_negative_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a non-negative int")
    if value < 0:
        raise ValueError(f"{name} must be a non-negative int")


def _deduplicate_events(indexed_events: list[tuple[int, dict]]) -> list[dict]:
    representatives = []
    positions_by_event_id = {}

    for index, event in indexed_events:
        event_id = event["event_id"]
        if event_id not in positions_by_event_id:
            positions_by_event_id[event_id] = len(representatives)
            representatives.append((index, event))
            continue

        position = positions_by_event_id[event_id]
        current_index, current_event = representatives[position]
        if _is_better_representative((index, event), (current_index, current_event)):
            representatives[position] = (index, event)

    return [event for _, event in representatives]


def _is_better_representative(
    candidate: tuple[int, dict],
    current: tuple[int, dict],
) -> bool:
    candidate_index, candidate_event = candidate
    current_index, current_event = current

    candidate_ignored = _is_ignored_event(candidate_event)
    current_ignored = _is_ignored_event(current_event)
    if candidate_ignored != current_ignored:
        return not candidate_ignored

    candidate_data_pass = candidate_event["data_unit_validation_status"] == PASS
    current_data_pass = current_event["data_unit_validation_status"] == PASS
    if candidate_data_pass != current_data_pass:
        return candidate_data_pass

    if candidate_event["has_official_source"] != current_event["has_official_source"]:
        return candidate_event["has_official_source"]

    candidate_multiplier = SOURCE_MULTIPLIERS[candidate_event["source_tier"]]
    current_multiplier = SOURCE_MULTIPLIERS[current_event["source_tier"]]
    if candidate_multiplier != current_multiplier:
        return candidate_multiplier > current_multiplier

    candidate_score = score_positive_event(candidate_event)
    current_score = score_positive_event(current_event)
    if candidate_score != current_score:
        return candidate_score > current_score

    if candidate_event["event_age_days"] != current_event["event_age_days"]:
        return candidate_event["event_age_days"] < current_event["event_age_days"]

    return candidate_index < current_index


def _is_ignored_event(event: dict) -> bool:
    return (
        event["event_category"] == NOISE
        or event["llm_classification"] in {LLM_NEGATIVE, LLM_NEUTRAL, LLM_UNCLEAR}
        or event["is_llm_only"] is True
        or event["event_age_days"] > 90
    )


def _validate_source(event: dict) -> str:
    if event["has_official_source"]:
        return PASS
    if event["independent_source_count"] >= 2 and event["source_tier"] != BLOG_SOCIAL:
        return PASS
    return FAIL


def _aggregate_data_unit_status(scoring_candidates: list[dict]) -> str:
    statuses = [event["data_unit_validation_status"] for event in scoring_candidates]
    if not statuses:
        return INSUFFICIENT_DATA
    if INVALID in statuses:
        return INVALID
    if INSUFFICIENT_DATA in statuses:
        return INSUFFICIENT_DATA
    if MANUAL_REVIEW in statuses:
        return MANUAL_REVIEW
    return PASS


def _aggregate_source_validation_status(
    scoring_candidates: list[dict],
    manual_review_event_ids: list[str],
) -> str:
    if not scoring_candidates and manual_review_event_ids:
        return MANUAL_REVIEW
    if not scoring_candidates and not manual_review_event_ids:
        return INSUFFICIENT_DATA

    statuses = [_validate_source(event) for event in scoring_candidates]
    if all(status == PASS for status in statuses):
        return PASS
    if any(status == PASS for status in statuses):
        return PASS
    return FAIL


def _compute_catalyst_component_status(
    *,
    scoring_candidates: list[dict],
    manual_review_event_ids: list[str],
    data_unit_validation_status: str,
    source_validation_status: str,
    cumulative_catalyst_score: float,
    scored_event_ids: list[str],
) -> str:
    if not scoring_candidates and manual_review_event_ids:
        return MANUAL_REVIEW
    if not scoring_candidates and not manual_review_event_ids:
        return INSUFFICIENT_DATA
    if data_unit_validation_status in {INVALID, INSUFFICIENT_DATA}:
        return INSUFFICIENT_DATA
    if source_validation_status == INSUFFICIENT_DATA:
        return INSUFFICIENT_DATA
    if source_validation_status == FAIL:
        return FAIL
    if data_unit_validation_status == MANUAL_REVIEW:
        return MANUAL_REVIEW
    if source_validation_status == MANUAL_REVIEW:
        return MANUAL_REVIEW
    if cumulative_catalyst_score >= CATALYST_PASS_THRESHOLD and scored_event_ids:
        return PASS
    if cumulative_catalyst_score < CATALYST_PASS_THRESHOLD and manual_review_event_ids:
        return MANUAL_REVIEW
    if cumulative_catalyst_score < CATALYST_PASS_THRESHOLD:
        return FAIL
    return MANUAL_REVIEW
