from __future__ import annotations

from numbers import Real


PASS_FULL = "PASS_FULL"
FAIL_HARD_DROP = "FAIL_HARD_DROP"
MANUAL_REVIEW_DEFERRED_RECOVERY = "MANUAL_REVIEW_DEFERRED_RECOVERY"
MANUAL_REVIEW_STOP = "MANUAL_REVIEW_STOP"
INSUFFICIENT_DATA_STOP = "INSUFFICIENT_DATA_STOP"

PASS_RECOVERY_PROFILE = "PASS_RECOVERY_PROFILE"
MANUAL_REVIEW = "MANUAL_REVIEW"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
FAIL = "FAIL"

PASS = "PASS"

CLEAR_VERIFIED = "CLEAR_VERIFIED"
ACTIVE_NEGATIVE = "ACTIVE_NEGATIVE"
MATERIALITY_UNKNOWN = "MATERIALITY_UNKNOWN"
COVERAGE_UNKNOWN = "COVERAGE_UNKNOWN"

F_CLEAR = "F_CLEAR"
F_MAJOR = "F_MAJOR"
F_MINOR = "F_MINOR"
F_UNKNOWN_DATA_MISSING = "F_UNKNOWN_DATA_MISSING"

OK = "OK"
NOT_OK = "NOT_OK"
UNRESOLVED = "UNRESOLVED"

STANDARD_GATE2_STATUS = frozenset({
    PASS_FULL,
    FAIL_HARD_DROP,
    MANUAL_REVIEW_DEFERRED_RECOVERY,
    MANUAL_REVIEW_STOP,
    INSUFFICIENT_DATA_STOP,
})

GATE2_RESULT = frozenset({
    PASS_FULL,
    PASS_RECOVERY_PROFILE,
    MANUAL_REVIEW,
    INSUFFICIENT_DATA,
    FAIL,
})

BASIC_STATUS = frozenset({
    PASS,
    FAIL,
    MANUAL_REVIEW,
    INSUFFICIENT_DATA,
})

NEGATIVE_STATUS = frozenset({
    CLEAR_VERIFIED,
    ACTIVE_NEGATIVE,
    MATERIALITY_UNKNOWN,
    COVERAGE_UNKNOWN,
})

TRAP_F_STATUS = frozenset({
    F_CLEAR,
    F_MAJOR,
    F_MINOR,
    F_UNKNOWN_DATA_MISSING,
})

SOURCE_CONFIDENCE = frozenset({
    OK,
    NOT_OK,
})

COVERAGE_STATUS = frozenset({
    CLEAR_VERIFIED,
    COVERAGE_UNKNOWN,
})

INTEGRITY_STATUS = frozenset({
    OK,
    FAIL,
    UNRESOLVED,
})


def evaluate_gate2_recovery_profile(
    *,
    standard_gate2_status: str,
    gate3_recovery_status: str,
    earnings_condition: str,
    independent_catalyst_score: float,
    catalyst_underlying_cause: str,
    earnings_underlying_cause: str,
    negative_status: str,
    catalyst_source_confidence: str,
    negative_scan_coverage: str,
    eps_basis_integrity: str,
    trap_f_status: str,
    split_share_count_basis: str,
) -> str:
    _validate_inputs(
        standard_gate2_status=standard_gate2_status,
        gate3_recovery_status=gate3_recovery_status,
        earnings_condition=earnings_condition,
        independent_catalyst_score=independent_catalyst_score,
        negative_status=negative_status,
        catalyst_source_confidence=catalyst_source_confidence,
        negative_scan_coverage=negative_scan_coverage,
        eps_basis_integrity=eps_basis_integrity,
        trap_f_status=trap_f_status,
        split_share_count_basis=split_share_count_basis,
    )

    if standard_gate2_status == PASS_FULL:
        return PASS_FULL
    if standard_gate2_status == FAIL_HARD_DROP:
        return FAIL
    if standard_gate2_status == MANUAL_REVIEW_STOP:
        return MANUAL_REVIEW
    if standard_gate2_status == INSUFFICIENT_DATA_STOP:
        return INSUFFICIENT_DATA

    if (
        standard_gate2_status == MANUAL_REVIEW_DEFERRED_RECOVERY
        and gate3_recovery_status == PASS
        and earnings_condition == PASS
        and independent_catalyst_score >= 1.5
        and catalyst_underlying_cause != earnings_underlying_cause
        and negative_status == CLEAR_VERIFIED
        and catalyst_source_confidence == OK
        and negative_scan_coverage == CLEAR_VERIFIED
        and eps_basis_integrity == OK
        and trap_f_status == F_CLEAR
        and split_share_count_basis == OK
    ):
        return PASS_RECOVERY_PROFILE

    if (
        negative_status == ACTIVE_NEGATIVE
        or trap_f_status == F_MAJOR
        or earnings_condition == FAIL
    ):
        return FAIL

    if (
        eps_basis_integrity == FAIL
        or split_share_count_basis == UNRESOLVED
        or trap_f_status == F_UNKNOWN_DATA_MISSING
        or earnings_condition == INSUFFICIENT_DATA
        or gate3_recovery_status == INSUFFICIENT_DATA
    ):
        return INSUFFICIENT_DATA

    if (
        negative_status == MATERIALITY_UNKNOWN
        or negative_status == COVERAGE_UNKNOWN
        or trap_f_status == F_MINOR
        or catalyst_source_confidence == NOT_OK
        or negative_scan_coverage == COVERAGE_UNKNOWN
        or gate3_recovery_status == MANUAL_REVIEW
        or earnings_condition == MANUAL_REVIEW
        or independent_catalyst_score < 1.5
        or catalyst_underlying_cause == earnings_underlying_cause
    ):
        return MANUAL_REVIEW

    return MANUAL_REVIEW


def _validate_inputs(
    *,
    standard_gate2_status: str,
    gate3_recovery_status: str,
    earnings_condition: str,
    independent_catalyst_score: float,
    negative_status: str,
    catalyst_source_confidence: str,
    negative_scan_coverage: str,
    eps_basis_integrity: str,
    trap_f_status: str,
    split_share_count_basis: str,
) -> None:
    _validate_member("standard_gate2_status", standard_gate2_status, STANDARD_GATE2_STATUS)
    _validate_member("gate3_recovery_status", gate3_recovery_status, BASIC_STATUS)
    _validate_member("earnings_condition", earnings_condition, BASIC_STATUS)
    _validate_member("negative_status", negative_status, NEGATIVE_STATUS)
    _validate_member("catalyst_source_confidence", catalyst_source_confidence, SOURCE_CONFIDENCE)
    _validate_member("negative_scan_coverage", negative_scan_coverage, COVERAGE_STATUS)
    _validate_member("eps_basis_integrity", eps_basis_integrity, INTEGRITY_STATUS)
    _validate_member("trap_f_status", trap_f_status, TRAP_F_STATUS)
    _validate_member("split_share_count_basis", split_share_count_basis, INTEGRITY_STATUS)

    if isinstance(independent_catalyst_score, bool) or not isinstance(
        independent_catalyst_score,
        Real,
    ):
        raise ValueError("independent_catalyst_score must be numeric")


def _validate_member(name: str, value: str, allowed_values: frozenset[str]) -> None:
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise ValueError(f"{name} must be one of: {allowed}")
