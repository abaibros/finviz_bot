import csv
import os
from collections.abc import Mapping
from datetime import datetime, timezone


WATCHLIST_LOG_CSV = "watchlist_log.csv"

WATCHLIST_LOG_FIELDS = [
    "created_at_utc",
    "run_id",
    "alert_version",
    "market",
    "currency",
    "ticker",
    "rank",
    "areas",
    "total_score",
    "score_roe",
    "score_de",
    "score_revenue_growth",
    "score_drawdown",
    "score_volume",
    "score_beta",
    "score_multi_area",
    "return_1y_pct",
    "return_5d_pct",
    "roe",
    "revenue_growth",
    "debt_to_equity",
    "trailing_pe",
    "volume",
    "beta",
    "price_fetched_at",
    "fundamentals_fetched_at",
    "prior_observation_count",
]

STRING_FIELDS_TO_CHECK = [
    "created_at_utc",
    "run_id",
    "alert_version",
    "market",
    "currency",
    "ticker",
    "areas",
    "price_fetched_at",
    "fundamentals_fetched_at",
]

FORBIDDEN_WORDS = [
    "매수 신호",
    "매수 후보",
    "분할 매수",
]


class ObservationCounts(dict):
    def __init__(self, *args, dedup_keys=None, fieldnames=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dedup_keys = dedup_keys or set()
        self.fieldnames = fieldnames or []


def generate_run_timestamp():
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=(now.microsecond // 1000) * 1000)


def _coerce_utc_datetime(run_timestamp_utc):
    if isinstance(run_timestamp_utc, datetime):
        dt = run_timestamp_utc
    else:
        raw = str(run_timestamp_utc).strip()
        if raw.endswith("Z"):
            raw = f"{raw[:-1]}+00:00"
        dt = datetime.fromisoformat(raw)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def format_created_at_utc(run_timestamp_utc):
    dt = _coerce_utc_datetime(run_timestamp_utc)
    return (
        dt.strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{dt.microsecond // 1000:03d}Z"
    )


def build_run_id(run_timestamp_utc):
    dt = _coerce_utc_datetime(run_timestamp_utc)
    return dt.strftime("%Y%m%dT%H%M%S") + f"{dt.microsecond // 1000:03d}Z"


def _is_missing(value):
    if value is None:
        return True

    if isinstance(value, (list, tuple, set, dict)):
        return False

    try:
        import pandas as pd

        return bool(pd.isna(value))
    except Exception:
        pass

    try:
        return bool(value != value)
    except Exception:
        return False


def _candidate_get(candidate, key, default=""):
    if isinstance(candidate, Mapping):
        return candidate.get(key, default)

    getter = getattr(candidate, "get", None)
    if callable(getter):
        return getter(key, default)

    return getattr(candidate, key, default)


def _clean_value(value):
    if _is_missing(value):
        return ""
    return value


def _clean_string(value):
    if _is_missing(value):
        return ""
    return str(value).strip()


def normalize_areas(value):
    if _is_missing(value):
        return ""

    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        raw_values = value
    else:
        raw_values = [value]

    normalized = []
    for raw_value in raw_values:
        if _is_missing(raw_value):
            continue
        area = str(raw_value).strip().upper()
        if area:
            normalized.append(area)

    return ",".join(sorted(set(normalized)))


def build_watchlist_log_row(
    candidate,
    rank,
    run_id,
    alert_version,
    market,
    currency,
    created_at_utc,
    prior_observation_count,
):
    row = {
        "created_at_utc": _clean_string(created_at_utc),
        "run_id": _clean_string(run_id),
        "alert_version": _clean_string(alert_version),
        "market": _clean_string(market),
        "currency": _clean_string(currency),
        "ticker": _clean_string(_candidate_get(candidate, "ticker")),
        "rank": int(rank),
        "areas": normalize_areas(_candidate_get(candidate, "areas")),
        "total_score": _clean_value(_candidate_get(candidate, "total_score")),
        "score_roe": _clean_value(_candidate_get(candidate, "score_roe")),
        "score_de": _clean_value(_candidate_get(candidate, "score_de")),
        "score_revenue_growth": _clean_value(
            _candidate_get(candidate, "score_revenue_growth")
        ),
        "score_drawdown": _clean_value(_candidate_get(candidate, "score_drawdown")),
        "score_volume": _clean_value(_candidate_get(candidate, "score_volume")),
        "score_beta": _clean_value(_candidate_get(candidate, "score_beta")),
        "score_multi_area": _clean_value(_candidate_get(candidate, "score_multi_area")),
        "return_1y_pct": _clean_value(_candidate_get(candidate, "return_1y_pct")),
        "return_5d_pct": _clean_value(_candidate_get(candidate, "return_5d_pct")),
        "roe": _clean_value(_candidate_get(candidate, "roe")),
        "revenue_growth": _clean_value(_candidate_get(candidate, "revenue_growth")),
        "debt_to_equity": _clean_value(_candidate_get(candidate, "debt_to_equity")),
        "trailing_pe": _clean_value(_candidate_get(candidate, "trailing_pe")),
        "volume": _clean_value(_candidate_get(candidate, "volume")),
        "beta": _clean_value(_candidate_get(candidate, "beta")),
        "price_fetched_at": _clean_string(_candidate_get(candidate, "price_fetched_at")),
        "fundamentals_fetched_at": _clean_string(
            _candidate_get(candidate, "fundamentals_fetched_at")
        ),
        "prior_observation_count": int(prior_observation_count),
    }

    return {field: row.get(field, "") for field in WATCHLIST_LOG_FIELDS}


def assert_no_forbidden_words(text):
    value = "" if text is None else str(text)
    for word in FORBIDDEN_WORDS:
        if word in value:
            raise ValueError(f"Forbidden word found: {word}")


def assert_no_forbidden_words_in_row(row):
    for field in STRING_FIELDS_TO_CHECK:
        assert_no_forbidden_words(row.get(field, ""))


def load_existing_observation_counts(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return ObservationCounts()

    counts = ObservationCounts()

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        counts.fieldnames = reader.fieldnames or []

        for row in reader:
            market = _clean_string(row.get("market"))
            ticker = _clean_string(row.get("ticker"))
            run_id = _clean_string(row.get("run_id"))

            if market and ticker:
                key = (market, ticker)
                counts[key] = counts.get(key, 0) + 1

            if run_id and market and ticker:
                counts.dedup_keys.add((run_id, market, ticker))

    return counts


def validate_watchlist_log_header(path=WATCHLIST_LOG_CSV):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return True

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.reader(csvfile)
        try:
            header = next(reader)
        except StopIteration:
            return True

    if header != WATCHLIST_LOG_FIELDS:
        raise ValueError("Existing watchlist_log.csv header does not match M-1R schema")

    return True


def _should_write_header(path):
    return not os.path.exists(path) or os.path.getsize(path) == 0


def _append_rows(path, rows, write_header):
    with open(path, "a", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=WATCHLIST_LOG_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def _ensure_header(path):
    with open(path, "a", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=WATCHLIST_LOG_FIELDS)
        writer.writeheader()


def _coerce_candidates(candidates):
    if candidates is None:
        return []

    iterrows = getattr(candidates, "iterrows", None)
    if callable(iterrows):
        return [row.to_dict() for _, row in candidates.iterrows()]

    return list(candidates)


def append_watchlist_rows(
    candidates,
    run_id,
    alert_version,
    market,
    currency,
    created_at_utc,
    path=WATCHLIST_LOG_CSV,
):
    candidate_list = _coerce_candidates(candidates)
    write_header = _should_write_header(path)

    if not candidate_list:
        if write_header:
            _ensure_header(path)
        return 0

    validate_watchlist_log_header(path)
    existing_counts = load_existing_observation_counts(path)

    rows_to_append = []
    new_keys = set()

    for rank, candidate in enumerate(candidate_list, 1):
        ticker = _clean_string(_candidate_get(candidate, "ticker"))
        prior_count = existing_counts.get((_clean_string(market), ticker), 0)
        row = build_watchlist_log_row(
            candidate=candidate,
            rank=rank,
            run_id=run_id,
            alert_version=alert_version,
            market=market,
            currency=currency,
            created_at_utc=created_at_utc,
            prior_observation_count=prior_count,
        )
        assert_no_forbidden_words_in_row(row)

        dedup_key = (row["run_id"], row["market"], row["ticker"])
        if dedup_key in existing_counts.dedup_keys or dedup_key in new_keys:
            continue

        rows_to_append.append(row)
        new_keys.add(dedup_key)

    if not rows_to_append:
        return 0

    _append_rows(path, rows_to_append, write_header)
    return len(rows_to_append)
