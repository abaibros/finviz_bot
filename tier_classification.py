from __future__ import annotations

from numbers import Real

from gate2_recovery_profile import (
    ACTIVE_NEGATIVE,
    BASIC_STATUS,
    CLEAR_VERIFIED,
    COVERAGE_UNKNOWN,
    FAIL,
    GATE2_RESULT,
    INSUFFICIENT_DATA,
    MANUAL_REVIEW,
    MATERIALITY_UNKNOWN,
    NEGATIVE_STATUS,
    PASS,
    PASS_FULL,
    PASS_RECOVERY_PROFILE,
)


MANUAL_REVIEW_2G_ELIGIBLE = "MANUAL_REVIEW_2G_ELIGIBLE"

STRONG = "STRONG"
MID = "MID"
WEAK = "WEAK"
UNKNOWN = "UNKNOWN"

F3_STRENGTH = frozenset({
    STRONG,
    MID,
    WEAK,
    UNKNOWN,
})

def evaluate_manual_review_2g_eligible(
    *,
    market_cap_usd_b: float,
    debt_to_equity_pct: float,
    non_gaap_profit_turnaround_recent_2q: bool,
    moving_toward_profitability: bool,
) -> str:
    _validate_numeric("market_cap_usd_b", market_cap_usd_b)
    _validate_numeric("debt_to_equity_pct", debt_to_equity_pct)
    _validate_bool(
        "non_gaap_profit_turnaround_recent_2q",
        non_gaap_profit_turnaround_recent_2q,
    )
    _validate_bool("moving_toward_profitability", moving_toward_profitability)

    turnaround_profitability_progress = (
        non_gaap_profit_turnaround_recent_2q or moving_toward_profitability
    )

    if (
        market_cap_usd_b >= 50.0
        and debt_to_equity_pct <= 300.0
        and turnaround_profitability_progress
    ):
        return MANUAL_REVIEW_2G_ELIGIBLE

    return FAIL


def is_tier1_eligible(
    *,
    gate1_status: str,
    gate2_status: str,
    gate3_status: str,
    gate4_status: str,
    fatal_trap_count: int,
    f3_strength: str,
    entry_block: bool,
) -> bool:
    _validate_member("gate1_status", gate1_status, BASIC_STATUS)
    _validate_member("gate2_status", gate2_status, GATE2_RESULT)
    _validate_member("gate3_status", gate3_status, BASIC_STATUS)
    _validate_member("gate4_status", gate4_status, BASIC_STATUS)
    _validate_non_negative_int("fatal_trap_count", fatal_trap_count)
    _validate_member("f3_strength", f3_strength, F3_STRENGTH)
    _validate_bool("entry_block", entry_block)

    return (
        gate1_status == PASS
        and gate2_status == PASS_FULL
        and gate3_status == PASS
        and gate4_status == PASS
        and fatal_trap_count == 0
        and f3_strength == STRONG
        and entry_block is False
    )


def is_tier2_eligible(
    *,
    gate1_status: str,
    gate2_status: str,
    gate3_status: str,
    gate4_status: str,
    filter_f1: str,
    filter_f2: str,
    filter_f3: str,
    filter_f4: str,
    filter_f5: str,
    negative_status: str,
    fatal_trap_count: int,
    entry_block: bool,
) -> bool:
    _validate_member(
        "gate1_status",
        gate1_status,
        BASIC_STATUS | frozenset({MANUAL_REVIEW_2G_ELIGIBLE}),
    )
    _validate_member("gate2_status", gate2_status, GATE2_RESULT)
    _validate_member("gate3_status", gate3_status, BASIC_STATUS)
    _validate_member("gate4_status", gate4_status, BASIC_STATUS)
    _validate_member("filter_f1", filter_f1, BASIC_STATUS)
    _validate_member("filter_f2", filter_f2, BASIC_STATUS)
    _validate_member("filter_f3", filter_f3, BASIC_STATUS)
    _validate_member("filter_f4", filter_f4, BASIC_STATUS)
    _validate_member("filter_f5", filter_f5, BASIC_STATUS)
    _validate_member("negative_status", negative_status, NEGATIVE_STATUS)
    _validate_non_negative_int("fatal_trap_count", fatal_trap_count)
    _validate_bool("entry_block", entry_block)

    if gate2_status == PASS_RECOVERY_PROFILE and negative_status != CLEAR_VERIFIED:
        raise ValueError(
            "Inconsistent input: gate2_status == PASS_RECOVERY_PROFILE "
            "requires negative_status == CLEAR_VERIFIED"
        )

    return (
        gate1_status in {PASS, MANUAL_REVIEW_2G_ELIGIBLE}
        and gate2_status in {PASS_FULL, PASS_RECOVERY_PROFILE}
        and gate3_status == PASS
        and gate4_status in {PASS, MANUAL_REVIEW}
        and filter_f1 == PASS
        and filter_f2 == PASS
        and filter_f3 == PASS
        and filter_f4 == PASS
        and filter_f5 == PASS
        and negative_status != ACTIVE_NEGATIVE
        and fatal_trap_count == 0
        and entry_block is False
    )


def _validate_numeric(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be numeric")


def _validate_bool(name: str, value: bool) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be bool")


def _validate_non_negative_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a non-negative int")
    if value < 0:
        raise ValueError(f"{name} must be a non-negative int")


def _validate_member(name: str, value: str, allowed_values: frozenset[str]) -> None:
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise ValueError(f"{name} must be one of: {allowed}")
