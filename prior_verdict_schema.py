import csv
import os
import re
from datetime import datetime


PRIOR_VERDICT_LOG_CSV = "prior_verdict_log.csv"

PRIOR_VERDICT_FIELDS = [
    "created_at_utc",
    "verdict_date",
    "run_id",
    "ticker",
    "verdict",
    "prior_score",
    "alert_count",
    "source",
    "reviewer",
    "note",
    "review_after",
]

ALLOWED_VERDICTS = {
    "HOLD",
    "OBSERVE",
    "WATCHFUL",
    "RESUMED",
}

ALLOWED_SOURCES = {
    "manual",
    "system",
    "auto",
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CREATED_AT_UTC_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
)


def _clean_required(value, field_name):
    cleaned = "" if value is None else str(value).strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def _clean_optional(value):
    if value is None:
        return ""
    return str(value).strip()


def validate_verdict(verdict):
    value = _clean_required(verdict, "verdict")
    if value not in ALLOWED_VERDICTS:
        raise ValueError(f"Invalid prior verdict: {value}")


def validate_source(source):
    value = _clean_required(source, "source")
    if value not in ALLOWED_SOURCES:
        raise ValueError(f"Invalid prior verdict source: {value}")


def validate_date_yyyy_mm_dd(value, field_name):
    cleaned = _clean_required(value, field_name)
    if not DATE_PATTERN.fullmatch(cleaned):
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid date") from exc


def validate_created_at_utc(value):
    cleaned = _clean_required(value, "created_at_utc")
    if not CREATED_AT_UTC_PATTERN.fullmatch(cleaned):
        raise ValueError("created_at_utc must use ISO 8601 UTC millisecond format")
    try:
        datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise ValueError("created_at_utc must be a valid UTC timestamp") from exc


def validate_prior_verdict_row(row):
    _clean_required(row.get("ticker", ""), "ticker")
    validate_verdict(row.get("verdict", ""))
    validate_source(row.get("source", ""))
    validate_date_yyyy_mm_dd(row.get("verdict_date", ""), "verdict_date")
    validate_created_at_utc(row.get("created_at_utc", ""))

    review_after = _clean_optional(row.get("review_after", ""))
    if review_after:
        validate_date_yyyy_mm_dd(review_after, "review_after")


def validate_prior_verdict_rows(rows):
    for row in rows:
        validate_prior_verdict_row(row)


def _validate_header(fieldnames):
    if fieldnames != PRIOR_VERDICT_FIELDS:
        raise ValueError("prior_verdict_log.csv header does not match schema")


def validate_prior_verdict_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        _validate_header(reader.fieldnames or [])
        validate_prior_verdict_rows(reader)


def _should_write_header(path):
    return not os.path.exists(path) or os.path.getsize(path) == 0


def _ensure_header(path):
    with open(path, "a", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PRIOR_VERDICT_FIELDS)
        writer.writeheader()


def _row_key(row):
    return (
        _clean_optional(row.get("run_id", "")),
        _clean_optional(row.get("ticker", "")),
        _clean_optional(row.get("verdict_date", "")),
        _clean_optional(row.get("verdict", "")),
    )


def _load_existing_keys(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return set()

    with open(path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        _validate_header(reader.fieldnames or [])
        return {_row_key(row) for row in reader}


def _normalize_row(row):
    return {field: _clean_optional(row.get(field, "")) for field in PRIOR_VERDICT_FIELDS}


def append_prior_verdict_rows(rows, path=PRIOR_VERDICT_LOG_CSV):
    row_list = [_normalize_row(row) for row in (rows or [])]
    validate_prior_verdict_rows(row_list)

    write_header = _should_write_header(path)
    if not row_list:
        if write_header:
            _ensure_header(path)
        return 0

    existing_keys = _load_existing_keys(path)
    new_keys = set()
    rows_to_append = []

    for row in row_list:
        key = _row_key(row)
        if key in existing_keys or key in new_keys:
            continue
        rows_to_append.append(row)
        new_keys.add(key)

    if not rows_to_append:
        return 0

    with open(path, "a", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=PRIOR_VERDICT_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows_to_append)

    return len(rows_to_append)
