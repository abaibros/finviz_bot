from __future__ import annotations

from types import MappingProxyType


A = "A"
B = "B"
C = "C"
D = "D"
E = "E"
F_MAJOR = "F_MAJOR"
F_MINOR = "F_MINOR"
G = "G"
H = "H"
I = "I"
J = "J"

FATAL = "fatal"
AUXILIARY = "auxiliary"

TRAP_ORDER = (
    C,
    I,
    B,
    F_MAJOR,
    A,
    H,
    D,
    F_MINOR,
    G,
    E,
    J,
)

FATAL_TRAPS = frozenset({
    C,
    I,
    B,
    F_MAJOR,
})

AUXILIARY_TRAPS = frozenset({
    A,
    D,
    E,
    F_MINOR,
    G,
    H,
    J,
})

TRAP_PRIORITY_RANKS = MappingProxyType({
    C: 1,
    I: 2,
    B: 3,
    F_MAJOR: 4,
    A: 5,
    H: 5,
    D: 6,
    F_MINOR: 7,
    G: 7,
    E: 7,
    J: 8,
})

ALLOWED_TRAP_CODES = FATAL_TRAPS | AUXILIARY_TRAPS


def classify_trap(trap_code: str) -> dict:
    _validate_trap_code(trap_code)

    is_fatal = trap_code in FATAL_TRAPS
    return {
        "trap_code": trap_code,
        "trap_type": FATAL if is_fatal else AUXILIARY,
        "is_fatal": is_fatal,
        "priority_rank": TRAP_PRIORITY_RANKS[trap_code],
    }


def summarize_traps(trap_codes: list[str]) -> dict:
    if not isinstance(trap_codes, list):
        raise ValueError("trap_codes must be a list")

    _validate_no_duplicate_traps(trap_codes)

    classifications = [classify_trap(trap_code) for trap_code in trap_codes]
    fatal_traps = _sort_by_trap_order([
        item["trap_code"] for item in classifications if item["is_fatal"]
    ])
    auxiliary_traps = _sort_by_trap_order([
        item["trap_code"] for item in classifications if not item["is_fatal"]
    ])

    if classifications:
        highest_priority_rank = min(item["priority_rank"] for item in classifications)
        highest_priority_traps = _sort_by_trap_order([
            item["trap_code"]
            for item in classifications
            if item["priority_rank"] == highest_priority_rank
        ])
    else:
        highest_priority_rank = None
        highest_priority_traps = []

    return {
        "fatal_trap_count": len(fatal_traps),
        "auxiliary_trap_count": len(auxiliary_traps),
        "fatal_traps": fatal_traps,
        "auxiliary_traps": auxiliary_traps,
        "highest_priority_rank": highest_priority_rank,
        "highest_priority_traps": highest_priority_traps,
        "has_fatal_trap": bool(fatal_traps),
    }


def _validate_trap_code(trap_code: str) -> None:
    if trap_code not in ALLOWED_TRAP_CODES:
        allowed = ", ".join(TRAP_ORDER)
        raise ValueError(f"trap_code must be one of: {allowed}")


def _validate_no_duplicate_traps(trap_codes: list[str]) -> None:
    seen = set()
    for trap_code in trap_codes:
        _validate_trap_code(trap_code)
        if trap_code in seen:
            raise ValueError(f"duplicate trap_code is not allowed: {trap_code}")
        seen.add(trap_code)


def _sort_by_trap_order(trap_codes: list[str]) -> list[str]:
    return [trap_code for trap_code in TRAP_ORDER if trap_code in trap_codes]
