import csv


MANUAL_EXCLUSION_FIELDS = [
    "ticker",
    "action",
    "reason_code",
    "reason_note",
    "exclusion_type",
    "source_note",
    "added_date",
]

ALLOWED_REASON_CODES = {
    "M_AND_A_COMPLETED",
    "TENDER_OFFER",
    "CASH_ACQUISITION",
    "DELISTING_SCHEDULED",
    "MANUAL_BLACKLIST",
}


def validate_reason_code(reason_code):
    value = "" if reason_code is None else str(reason_code).strip()
    if not value:
        return
    if value not in ALLOWED_REASON_CODES:
        raise ValueError(f"Invalid manual exclusion reason_code: {value}")


def validate_manual_exclusion_row(row):
    validate_reason_code(row.get("reason_code", ""))


def validate_manual_exclusion_rows(rows):
    for row in rows:
        validate_manual_exclusion_row(row)


def validate_manual_exclusion_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        validate_manual_exclusion_rows(reader)
