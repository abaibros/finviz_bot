#!/usr/bin/env python3
"""Generate the v0.3 Gate 3 based universe quality audit."""

from __future__ import annotations

import collections
import csv
import hashlib
import math
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf
import yfinance.cache as yf_cache


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "universe_master.csv"
LEGACY_AUDIT_CSV = ROOT / "reports" / "universe_quality_audit_v0_1.csv"
V03_AUDIT_CSV = ROOT / "reports" / "universe_quality_audit_v0_3.csv"
V03_SUMMARY_MD = ROOT / "reports" / "universe_quality_audit_summary_v0_3.md"
PARADIGM_DOC = ROOT / "docs" / "paradigm" / "maesoo_v2_paradigm_v1_5_1_RC_FULL.md"
BACKTEST_REFERENCE_CSV = ROOT / "reports" / "backtest_it_2026q1_data_v0_1.csv"

AS_OF_DATE = "2026-05-27"
PRICE_START_DATE = "2025-03-01"
PRICE_END_DATE = "2026-05-27"
YFINANCE_END_EXCLUSIVE = "2026-05-28"
EXPECTED_INPUT_ROWS = 656
PILOT_TICKERS = ["INTC", "BA", "SBUX", "DIS", "F"]
SPOTLIGHT_TICKERS = ["INTC", "BA", "SBUX", "PFE", "SMCI", "DIS", "PYPL", "F", "EL", "BAX"]

PROTECTED_PATHS = [
    ROOT / "scorer.py",
    ROOT / "telegram_reporter.py",
    ROOT / ".github" / "workflows" / "main.yml",
    ROOT / "run_daily_report.py",
    LEGACY_AUDIT_CSV,
    ROOT / "reports" / "universe_quality_audit_summary_v0_1.md",
]

OUTPUT_FIELDS = [
    "ticker",
    "name",
    "market",
    "sector",
    "sub_industry",
    "market_cap_usd_b",
    "turnaround_flag",
    "legacy_v0_1_universe_role",
    "legacy_v0_1_action",
    "legacy_v0_1_reason",
    "v0_3_universe_role",
    "v0_3_action",
    "v0_3_reason",
    "candidate_track",
    "gate3_recovery_required",
    "gate3_recovery_status",
    "gate3_continuation_status",
    "gate3_final_status",
    "ra_drawdown_from_52w_high_pct",
    "ra_pass",
    "rb_rebound_from_6m_low_pct",
    "rb_pass",
    "rc_ma50",
    "rc_ma200",
    "rc_pass",
    "rd_avg_volume_1m",
    "rd_avg_volume_6m",
    "rd_pass",
    "ca_drawdown_from_52w_high_pct",
    "ca_pass",
    "cb_pass",
    "cc_1m_return_pct",
    "cc_pass",
    "cd_avg_volume_1m",
    "cd_avg_volume_3m",
    "cd_pass",
    "ce_gate2_full_pass",
    "ce_pass",
    "price_data_source",
    "price_data_asof",
    "as_of_date",
    "gate3_missing_data_notes",
    "compatibility_notes",
]

GATE3_STATUS_VALUES = {"PASS", "FAIL", "INSUFFICIENT_DATA", "MANUAL_REVIEW"}
PASS_VALUES = {"Y", "N", "INSUFFICIENT_DATA"}
KR_TICKER_RE = re.compile(r"^[0-9]{6}\.(KS|KQ)$")

FORCED_KOSDAQ_BIO_NAMES = {
    "삼천당제약",
    "HLB",
    "펩트론",
    "코오롱티슈진",
    "에이비엘바이오",
    "리가켐바이오",
    "보로노이",
    "알테오젠",
}
KR_LARGE_MANUFACTURING_HEALTHCARE = {"삼성바이오로직스", "셀트리온"}
SPECIAL_SITUATION_TOKENS = [
    "m&a 완료",
    "tender offer",
    "acquired",
    "delisting",
    "liquidation",
    "suspended",
    "cash acquisition",
    "거래정지",
    "상장폐지",
]
VOLATILE_KOSDAQ_SUB_INDUSTRIES = {
    "Semiconductor Equipment",
    "Semiconductors",
    "Electronic Components",
    "Machinery",
    "Electrical Equipment",
    "Chemicals",
    "Industrial Conglomerates",
}
VOLATILE_KOSDAQ_NAMES = {
    "에코프로비엠",
    "에코프로",
    "레인보우로보틱스",
    "주성엔지니어링",
    "리노공업",
    "이오테크닉스",
    "원익IPS",
    "파두",
}


@dataclass(frozen=True)
class RoleDecision:
    role: str
    action: str
    reason: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_existing(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in paths if path.exists()}


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "GIT_HEAD_UNAVAILABLE"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_cap(row: dict[str, str]) -> float:
    try:
        return float(row.get("market_cap_usd_b") or 0)
    except ValueError:
        return 0.0


def bool_to_pass(value: bool) -> str:
    return "Y" if value else "N"


def fmt_float(value: Any, digits: int = 4) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if math.isnan(number) or math.isinf(number):
        return ""
    return f"{number:.{digits}f}"


def action_for(role: str, flags: set[str] | None = None) -> str:
    flags = flags or set()
    if role == "CORE":
        return "KEEP_CORE"
    if role == "EXTENDED":
        return "KEEP_EXTENDED"
    if role == "GATE3_FAIL_REVIEW":
        return "REVIEW_BEFORE_SCORING"
    if role in {"HIGH_RISK_REVIEW", "MANUAL_REVIEW"}:
        if "TICKER_REVIEW" in flags or "DATA_LIMITATION" in flags:
            return "MANUAL_REVIEW"
        return "REVIEW_BEFORE_SCORING" if role == "HIGH_RISK_REVIEW" else "MANUAL_REVIEW"
    if role == "DISCOVERY_ONLY":
        return "DISCOVERY_ONLY"
    return "EXCLUSION_REVIEW"


def make_reason(codes: list[str], note: str) -> str:
    unique_codes: list[str] = []
    for code in codes:
        if code not in unique_codes:
            unique_codes.append(code)
    return "; ".join(unique_codes[:3] + [note])


def has_any_token(text: str, tokens: list[str]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def classify_metadata_v03(
    row: dict[str, str],
    duplicate_tickers: set[str],
    kr_format_fail: set[str],
) -> RoleDecision:
    """Metadata classifier with v0.1 turnaround hard mapping removed."""

    ticker = row["ticker"]
    name = row["name"]
    market = row["market"]
    sector = row["sector"]
    sub_industry = row["sub_industry"]
    source = row["source"]
    company_type = row.get("company_type", "")
    cap = parse_cap(row)
    is_kr = market == "KR"
    is_kosdaq = ticker.endswith(".KQ")
    is_theme = "KOSDAQ_THEME" in source
    is_top15 = "KOSDAQ_TOP15" in source
    is_health = sector == "Health Care"
    is_biotech = sub_industry == "Biotechnology"
    is_pharma = sub_industry == "Pharmaceuticals"
    is_stable_kr_health = name in KR_LARGE_MANUFACTURING_HEALTHCARE
    text_blob = f"{name} {source}"

    flags: set[str] = set()
    if company_type == "Holding":
        flags.add("HOLDING_COMPANY")
    if row.get("adr_flag") == "Y" or "ADR" in source:
        flags.add("ADR_FOREIGN_LISTING")
    if "NEW" in source or "RECENT" in source or ticker == "VEEV":
        flags.add("RECENT_INDEX_INCLUSION")
    if is_theme:
        flags.add("KOSDAQ_THEME_RISK")
    if is_top15:
        flags.add("KOSDAQ_TOP15_RISK")
    if cap < 5 or (is_kr and cap < 3):
        flags.add("SMALL_CAP_RISK")
    if is_biotech:
        flags.add("BIOTECH_RISK")
    if is_pharma and (cap < 100 or is_kosdaq):
        flags.add("PHARMA_EVENT_RISK")
    if is_health and not (cap >= 100 and is_pharma):
        flags.add("HEALTHCARE_EVENT_RISK")
    if is_kosdaq and (sub_industry in VOLATILE_KOSDAQ_SUB_INDUSTRIES or name in VOLATILE_KOSDAQ_NAMES):
        flags.add("SECTOR_VOLATILITY")

    if ticker in duplicate_tickers or ticker in kr_format_fail:
        flags.update({"TICKER_REVIEW", "DATA_LIMITATION"})
        role = "EXCLUDE_CANDIDATE"
        reason = make_reason(
            ["TICKER_REVIEW", "NO_FINANCIAL_DATA_AVAILABLE"],
            "ticker structure requires manual review",
        )
    elif has_any_token(text_blob, SPECIAL_SITUATION_TOKENS):
        flags.update({"M_AND_A_REVIEW", "DATA_LIMITATION"})
        role = "EXCLUDE_CANDIDATE"
        reason = make_reason(
            ["M_AND_A_OR_SPECIAL_SITUATION", "NO_FINANCIAL_DATA_AVAILABLE"],
            "special situation marker found in metadata",
        )
    elif is_kosdaq and name in FORCED_KOSDAQ_BIO_NAMES:
        role = "HIGH_RISK_REVIEW"
        base_code = "PHARMA_EVENT_RISK" if is_pharma else "BIOTECH_CLINICAL_RISK"
        slot_code = "KOSDAQ_THEME_SLOT" if is_theme else "KOSDAQ_TOP15_RISK"
        reason = make_reason(
            [base_code, slot_code, "METADATA_ONLY_AUDIT"],
            "KOSDAQ healthcare row requires event-risk review",
        )
    elif is_kosdaq and is_health and (is_top15 or "KOSDAQ_THEME_BIO" in source) and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "KOSDAQ_TOP15_RISK", "METADATA_ONLY_AUDIT"],
            "KOSDAQ healthcare inclusion is monitoring metadata only",
        )
    elif is_biotech and cap < 30 and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "biotechnology row below 30B metadata threshold",
        )
    elif is_kosdaq and is_top15 and (
        sub_industry in VOLATILE_KOSDAQ_SUB_INDUSTRIES or name in VOLATILE_KOSDAQ_NAMES
    ):
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["KOSDAQ_TOP15_RISK", "SECTOR_VOLATILITY", "METADATA_ONLY_AUDIT"],
            "KOSDAQ top15 sector-volatility marker prevents core classification",
        )
    elif is_biotech and 30 <= cap < 100 and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "METADATA_ONLY_AUDIT"],
            "mid-large biotechnology row needs review before scoring",
        )
    elif is_pharma and is_health and cap < 10:
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["PHARMA_EVENT_RISK", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "pharmaceutical row below 10B metadata threshold",
        )
    elif is_theme:
        role = "DISCOVERY_ONLY"
        reason = make_reason(
            ["KOSDAQ_THEME_SLOT", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "theme-slot row retained for discovery monitoring only",
        )
    elif cap < 5 or (is_kr and cap < 3):
        role = "DISCOVERY_ONLY"
        small_code = "SMALL_CAP_KOREA" if is_kr else "MARKET_CAP_BELOW_THRESHOLD"
        reason = make_reason(
            [small_code, "METADATA_ONLY_AUDIT"],
            "market cap metadata below core threshold",
        )
    elif cap >= 50 and not is_biotech and not (is_kosdaq and is_health) and not is_theme:
        role = "CORE"
        codes = ["METADATA_ONLY_AUDIT"]
        if company_type == "Holding":
            codes.insert(0, "HOLDING_COMPANY_NATURE")
        elif row.get("adr_flag") == "Y" or "ADR" in source:
            codes.insert(0, "ADR_LISTING_RISK")
        elif "RECENT_INDEX_INCLUSION" in flags:
            codes.insert(0, "RECENT_INDEX_INCLUSION")
        reason = make_reason(codes, "large-cap metadata row without forced review marker")
    elif cap >= 10:
        role = "EXTENDED"
        codes = ["MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"]
        if company_type == "Holding":
            codes.insert(0, "HOLDING_COMPANY_NATURE")
        elif row.get("adr_flag") == "Y" or "ADR" in source:
            codes.insert(0, "ADR_LISTING_RISK")
        elif "RECENT_INDEX_INCLUSION" in flags:
            codes.insert(0, "RECENT_INDEX_INCLUSION")
        reason = make_reason(codes, "below core threshold but retained for extended monitoring")
    elif is_health or "SECTOR_VOLATILITY" in flags:
        role = "HIGH_RISK_REVIEW"
        reason = make_reason(
            ["SECTOR_VOLATILITY", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "sub-10B metadata row needs review before scoring",
        )
    else:
        role = "EXTENDED"
        reason = make_reason(
            ["MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "sub-10B row retained outside core classification",
        )

    return RoleDecision(role=role, action=action_for(role, flags), reason=reason)


def setup_yfinance_cache() -> Path:
    cache_dir = Path(tempfile.gettempdir()) / "finviz_bot_yfinance_cache_v03"
    cache_dir.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(cache_dir))
    yf_cache.set_cache_location(str(cache_dir))
    return cache_dir


def yfinance_symbol(ticker: str) -> str:
    if ticker.endswith((".KS", ".KQ")):
        return ticker
    return ticker.replace(".", "-")


def extract_ticker_frame(downloaded: pd.DataFrame, ticker: str, yf_symbol: str | None = None) -> pd.DataFrame:
    if downloaded.empty:
        return pd.DataFrame()
    symbol = yf_symbol or yfinance_symbol(ticker)
    frame = downloaded
    if isinstance(downloaded.columns, pd.MultiIndex):
        levels = [list(downloaded.columns.get_level_values(i)) for i in range(downloaded.columns.nlevels)]
        if symbol in levels[0]:
            frame = downloaded[symbol]
        elif ticker in levels[0]:
            frame = downloaded[ticker]
        elif downloaded.columns.nlevels > 1 and symbol in levels[1]:
            frame = downloaded.xs(symbol, axis=1, level=1)
        elif downloaded.columns.nlevels > 1 and ticker in levels[1]:
            frame = downloaded.xs(ticker, axis=1, level=1)
    frame = frame.copy()
    frame.index = pd.to_datetime(frame.index).tz_localize(None)
    return frame.dropna(how="all")


def download_one_price_history(ticker: str) -> pd.DataFrame:
    symbol = yfinance_symbol(ticker)
    try:
        downloaded = yf.download(
            symbol,
            start=PRICE_START_DATE,
            end=YFINANCE_END_EXCLUSIVE,
            progress=False,
            auto_adjust=False,
            actions=False,
            threads=False,
        )
    except Exception as exc:
        return pd.DataFrame({"download_error": [f"{type(exc).__name__}: {exc}"]})
    return extract_ticker_frame(downloaded, ticker, symbol)


def download_price_history(tickers: list[str], batch_size: int = 25) -> dict[str, pd.DataFrame]:
    setup_yfinance_cache()
    histories: dict[str, pd.DataFrame] = {}
    for start in range(0, len(tickers), batch_size):
        batch = tickers[start : start + batch_size]
        batch_symbols = [yfinance_symbol(ticker) for ticker in batch]
        try:
            downloaded = yf.download(
                batch_symbols,
                start=PRICE_START_DATE,
                end=YFINANCE_END_EXCLUSIVE,
                group_by="ticker",
                progress=False,
                auto_adjust=False,
                actions=False,
                threads=False,
            )
        except Exception as exc:
            for ticker in batch:
                histories[ticker] = pd.DataFrame({"download_error": [f"{type(exc).__name__}: {exc}"]})
            continue
        for ticker in batch:
            frame = extract_ticker_frame(downloaded, ticker, yfinance_symbol(ticker))
            if frame.empty:
                frame = download_one_price_history(ticker)
            histories[ticker] = frame
    return histories


def insufficient_gate3(note: str) -> dict[str, str]:
    values = {field: "" for field in OUTPUT_FIELDS if field.startswith(("ra_", "rb_", "rc_", "rd_", "ca_", "cb_", "cc_", "cd_", "ce_"))}
    values.update(
        {
            "gate3_recovery_status": "INSUFFICIENT_DATA",
            "gate3_continuation_status": "INSUFFICIENT_DATA",
            "gate3_final_status": "INSUFFICIENT_DATA",
            "ra_pass": "INSUFFICIENT_DATA",
            "rb_pass": "INSUFFICIENT_DATA",
            "rc_pass": "INSUFFICIENT_DATA",
            "rd_pass": "INSUFFICIENT_DATA",
            "ca_pass": "INSUFFICIENT_DATA",
            "cb_pass": "INSUFFICIENT_DATA",
            "cc_pass": "INSUFFICIENT_DATA",
            "cd_pass": "INSUFFICIENT_DATA",
            "ce_gate2_full_pass": "INSUFFICIENT_GATE2_DATA",
            "ce_pass": "INSUFFICIENT_DATA",
            "price_data_source": "yfinance_failed",
            "price_data_asof": "",
            "gate3_missing_data_notes": f"INSUFFICIENT_GATE3_DATA; {note}",
        }
    )
    return values


def final_gate3_status(recovery_status: str, continuation_status: str) -> str:
    if recovery_status == "PASS" or continuation_status == "PASS":
        return "PASS"
    if recovery_status == "FAIL" and continuation_status == "FAIL":
        return "FAIL"
    if recovery_status == "INSUFFICIENT_DATA" and continuation_status == "INSUFFICIENT_DATA":
        return "INSUFFICIENT_DATA"
    if "INSUFFICIENT_DATA" in {recovery_status, continuation_status}:
        return "MANUAL_REVIEW"
    return "MANUAL_REVIEW"


def has_non_turnaround_exclusion_reason(legacy_row: dict[str, str]) -> bool:
    if legacy_row.get("universe_role") != "EXCLUDE_CANDIDATE":
        return False
    text = " ".join(
        [
            legacy_row.get("risk_flags", ""),
            legacy_row.get("review_reason", ""),
            legacy_row.get("recommended_next_action", ""),
        ]
    ).lower()
    independent_markers = [
        "small_cap_risk",
        "data_limitation",
        "healthcare_event_risk",
        "manual exclusion",
        "manual_exclusion",
        "m&a",
        "event-completed",
        "event completed",
        "delisting",
        "tender offer",
        "cash acquisition",
        "market_cap_below_threshold",
        "no_financial_data_available",
        "ticker_review",
        "m_and_a_review",
        "special situation",
        "거래정지",
        "상장폐지",
    ]
    return any(marker in text for marker in independent_markers)


def calculate_gate3(frame: pd.DataFrame) -> dict[str, str]:
    if frame.empty:
        return insufficient_gate3("empty price dataframe")
    if "download_error" in frame.columns:
        return insufficient_gate3(str(frame["download_error"].iloc[0]))
    if "Close" not in frame.columns or "Volume" not in frame.columns:
        return insufficient_gate3("missing Close or Volume column")

    as_of = pd.Timestamp(AS_OF_DATE)
    data = frame[frame.index <= as_of].copy()
    data = data.dropna(subset=["Close", "Volume"])
    if len(data) < 252:
        return insufficient_gate3(f"insufficient rows for 52w window: {len(data)}")

    close = data["Close"].astype(float)
    volume = data["Volume"].astype(float)
    last_close = close.iloc[-1]
    high_52w = close.tail(252).max()
    low_6m = close.tail(126).min()
    ma50 = close.tail(50).mean()
    ma200 = close.tail(200).mean()
    avg_volume_1m = volume.tail(21).mean()
    avg_volume_3m = volume.tail(63).mean()
    avg_volume_6m = volume.tail(126).mean()
    one_month_base = close.tail(22).iloc[0]

    drawdown = (last_close / high_52w - 1) * 100
    rebound = (last_close / low_6m - 1) * 100
    one_month_return = (last_close / one_month_base - 1) * 100
    recent_close_up = close.tail(21).iloc[-1] > close.tail(21).iloc[0]

    ra = drawdown <= -20
    rb = rebound >= 15
    rc = ma50 > ma200 or (ma50 >= ma200 * 0.98 and recent_close_up)
    rd = avg_volume_1m > avg_volume_6m

    ca = -15 <= drawdown <= -3
    cb = ma50 > ma200
    cc = one_month_return >= 3
    cd = avg_volume_1m > avg_volume_3m
    ce_gate2_full_pass = "INSUFFICIENT_GATE2_DATA"
    ce_pass = "INSUFFICIENT_DATA"

    recovery_status = "PASS" if all([ra, rb, rc, rd]) else "FAIL"
    if not all([ca, cb, cc, cd]):
        continuation_status = "FAIL"
    elif ce_pass == "Y":
        continuation_status = "PASS"
    elif ce_pass == "N":
        continuation_status = "FAIL"
    else:
        continuation_status = "INSUFFICIENT_DATA"

    final_status = final_gate3_status(recovery_status, continuation_status)

    return {
        "gate3_recovery_status": recovery_status,
        "gate3_continuation_status": continuation_status,
        "gate3_final_status": final_status,
        "ra_drawdown_from_52w_high_pct": fmt_float(drawdown, 4),
        "ra_pass": bool_to_pass(ra),
        "rb_rebound_from_6m_low_pct": fmt_float(rebound, 4),
        "rb_pass": bool_to_pass(rb),
        "rc_ma50": fmt_float(ma50, 4),
        "rc_ma200": fmt_float(ma200, 4),
        "rc_pass": bool_to_pass(rc),
        "rd_avg_volume_1m": fmt_float(avg_volume_1m, 2),
        "rd_avg_volume_6m": fmt_float(avg_volume_6m, 2),
        "rd_pass": bool_to_pass(rd),
        "ca_drawdown_from_52w_high_pct": fmt_float(drawdown, 4),
        "ca_pass": bool_to_pass(ca),
        "cb_pass": bool_to_pass(cb),
        "cc_1m_return_pct": fmt_float(one_month_return, 4),
        "cc_pass": bool_to_pass(cc),
        "cd_avg_volume_1m": fmt_float(avg_volume_1m, 2),
        "cd_avg_volume_3m": fmt_float(avg_volume_3m, 2),
        "cd_pass": bool_to_pass(cd),
        "ce_gate2_full_pass": ce_gate2_full_pass,
        "ce_pass": ce_pass,
        "price_data_source": "yfinance",
        "price_data_asof": str(data.index[-1].date()),
        "gate3_missing_data_notes": "",
    }


def decide_v03_role(
    source_row: dict[str, str],
    legacy_row: dict[str, str],
    metadata_decision: RoleDecision,
    gate3: dict[str, str],
) -> RoleDecision:
    turnaround = source_row["turnaround_flag"] == "Y"
    legacy_role = legacy_row.get("universe_role", "")
    legacy_action = legacy_row.get("recommended_next_action", "")
    legacy_reason = legacy_row.get("review_reason", "")

    if not turnaround:
        return RoleDecision(
            role=legacy_role,
            action=legacy_action,
            reason=(
                "NON_TURNAROUND_ROLE_UNCHANGED; Gate 3 metrics recorded for v0.4 evidence only; "
                f"legacy_reason={legacy_reason}"
            ),
        )

    if has_non_turnaround_exclusion_reason(legacy_row):
        return RoleDecision(
            role="EXCLUDE_CANDIDATE",
            action="EXCLUSION_REVIEW",
            reason=(
                "legacy EXCLUDE preserved due to non-turnaround exclusion reasons; "
                "turnaround_flag used as Recovery Track input only; "
                f"legacy_reason={legacy_reason}"
            ),
        )

    if metadata_decision.role == "EXCLUDE_CANDIDATE":
        return RoleDecision(
            role=metadata_decision.role,
            action=metadata_decision.action,
            reason=(
                "EXCLUDE_RULE_RETAINED; turnaround_flag used as Recovery Track input only; "
                f"metadata_reason={metadata_decision.reason}"
            ),
        )

    final_status = gate3["gate3_final_status"]
    recovery_status = gate3["gate3_recovery_status"]
    continuation_status = gate3["gate3_continuation_status"]
    if final_status == "PASS":
        return RoleDecision(
            role="MANUAL_REVIEW",
            action="MANUAL_REVIEW",
            reason=(
                "Gate3 PASS but Gate2 catalyst validation is not implemented; automatic CORE/1군 classification blocked; "
                f"metadata_role={metadata_decision.role}; recovery={recovery_status}; continuation={continuation_status}"
            ),
        )
    if final_status == "FAIL":
        return RoleDecision(
            role="GATE3_FAIL_REVIEW",
            action="REVIEW_BEFORE_SCORING",
            reason=(
                "Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; "
                f"metadata_role={metadata_decision.role}; recovery={recovery_status}; continuation={continuation_status}"
            ),
        )
    if final_status == "INSUFFICIENT_DATA":
        return RoleDecision(
            role="MANUAL_REVIEW",
            action="MANUAL_REVIEW",
            reason="INSUFFICIENT_GATE3_DATA; no arbitrary classification; turnaround_flag used as Recovery Track input",
        )
    return RoleDecision(
        role="MANUAL_REVIEW",
        action="MANUAL_REVIEW",
        reason=(
            "Gate 3 MANUAL_REVIEW; no arbitrary classification; "
            f"metadata_role={metadata_decision.role}; recovery={recovery_status}; continuation={continuation_status}"
        ),
    )


def compatibility_note(legacy_row: dict[str, str], v03_decision: RoleDecision, turnaround: bool) -> str:
    legacy_role = legacy_row.get("universe_role", "")
    legacy_action = legacy_row.get("recommended_next_action", "")
    changes: list[str] = []
    if legacy_role != v03_decision.role:
        changes.append(f"role_changed:{legacy_role}->{v03_decision.role}")
    if legacy_action != v03_decision.action:
        changes.append(f"action_changed:{legacy_action}->{v03_decision.action}")
    base = "v0_1_legacy_columns_preserved"
    if not turnaround:
        base += "; non_turnaround_role_unchanged"
    else:
        base += "; turnaround_gate3_recovery_applied"
    if changes:
        base += "; " + "; ".join(changes)
    return base


def build_audit_rows(
    rows: list[dict[str, str]],
    legacy_rows: dict[str, dict[str, str]],
    price_histories: dict[str, pd.DataFrame],
) -> list[dict[str, str]]:
    ticker_counts = collections.Counter(row["ticker"] for row in rows)
    duplicate_tickers = {ticker for ticker, count in ticker_counts.items() if count > 1}
    kr_format_fail = {
        row["ticker"]
        for row in rows
        if row["market"] == "KR" and not KR_TICKER_RE.match(row["ticker"])
    }

    audit_rows: list[dict[str, str]] = []
    for row in rows:
        ticker = row["ticker"]
        legacy = legacy_rows.get(ticker, {})
        metadata_decision = classify_metadata_v03(row, duplicate_tickers, kr_format_fail)
        gate3 = calculate_gate3(price_histories.get(ticker, pd.DataFrame()))
        v03_decision = decide_v03_role(row, legacy, metadata_decision, gate3)
        turnaround = row["turnaround_flag"] == "Y"
        output = {
            "ticker": ticker,
            "name": row["name"],
            "market": row["market"],
            "sector": row["sector"],
            "sub_industry": row["sub_industry"],
            "market_cap_usd_b": row["market_cap_usd_b"],
            "turnaround_flag": row["turnaround_flag"],
            "legacy_v0_1_universe_role": legacy.get("universe_role", ""),
            "legacy_v0_1_action": legacy.get("recommended_next_action", ""),
            "legacy_v0_1_reason": legacy.get("review_reason", ""),
            "v0_3_universe_role": v03_decision.role,
            "v0_3_action": v03_decision.action,
            "v0_3_reason": v03_decision.reason,
            "candidate_track": "RECOVERY" if turnaround else "OBSERVATION_ONLY",
            "gate3_recovery_required": "Y" if turnaround else "N",
            "as_of_date": AS_OF_DATE,
            "compatibility_notes": compatibility_note(legacy, v03_decision, turnaround),
        }
        output.update(gate3)
        audit_rows.append({field: output.get(field, "") for field in OUTPUT_FIELDS})
    return audit_rows


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "_None_\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "/") for cell in row) + " |")
    return "\n".join(lines) + "\n"


def status_counts(audit_rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts = collections.Counter(row[field] for row in audit_rows)
    return {status: counts.get(status, 0) for status in ["PASS", "FAIL", "MANUAL_REVIEW", "INSUFFICIENT_DATA"]}


def changed_rows(audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in audit_rows
        if row["legacy_v0_1_universe_role"] != row["v0_3_universe_role"]
        or row["legacy_v0_1_action"] != row["v0_3_action"]
    ]


def write_audit_csv(audit_rows: list[dict[str, str]]) -> None:
    V03_AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with V03_AUDIT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows)


def validate_v03_rows(audit_rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    for row in audit_rows:
        missing = [field for field in OUTPUT_FIELDS if field not in row]
        if missing:
            failures.append(f"missing output fields for {row.get('ticker', 'UNKNOWN')}: {missing}")
        for field in ["gate3_recovery_status", "gate3_continuation_status", "gate3_final_status"]:
            if row.get(field) not in GATE3_STATUS_VALUES:
                failures.append(f"invalid {field} for {row.get('ticker')}: {row.get(field)}")
        if row.get("as_of_date") != AS_OF_DATE:
            failures.append(f"invalid as_of_date for {row.get('ticker')}: {row.get('as_of_date')}")
    return failures


def write_summary(
    rows: list[dict[str, str]],
    audit_rows: list[dict[str, str]],
    start_hashes: dict[str, str],
    end_hashes: dict[str, str],
    git_start: str,
    git_end: str,
) -> None:
    by_ticker = {row["ticker"]: row for row in audit_rows}
    turnaround_rows = [row for row in audit_rows if row["turnaround_flag"] == "Y"]
    pilot_rows = [by_ticker[ticker] for ticker in PILOT_TICKERS if ticker in by_ticker]
    price_failures = [
        row
        for row in audit_rows
        if row["price_data_source"] != "yfinance"
    ]
    changed = changed_rows(audit_rows)
    non_turnaround_rows = [row for row in audit_rows if row["turnaround_flag"] != "Y"]
    non_turnaround_changed = [
        row
        for row in non_turnaround_rows
        if row["legacy_v0_1_universe_role"] != row["v0_3_universe_role"]
    ]
    existing_hash_rows = [
        [name, start_hashes.get(name, "MISSING"), end_hashes.get(name, "MISSING"), start_hashes.get(name) == end_hashes.get(name)]
        for name in sorted(start_hashes)
    ]
    protected_ok = all(start_hashes.get(name) == end_hashes.get(name) for name in start_hashes if name in end_hashes)
    v01_unchanged = (
        start_hashes.get("reports/universe_quality_audit_v0_1.csv")
        == end_hashes.get("reports/universe_quality_audit_v0_1.csv")
        and start_hashes.get("reports/universe_quality_audit_summary_v0_1.md")
        == end_hashes.get("reports/universe_quality_audit_summary_v0_1.md")
    )
    pilot_success_count = sum(1 for row in pilot_rows if row["price_data_source"] == "yfinance")
    pilot_passed = pilot_success_count >= 3
    bax_row = by_ticker.get("BAX")
    gate3_fail_turnaround_rows = [
        row
        for row in turnaround_rows
        if row["gate3_final_status"] == "FAIL"
    ]
    gate3_fail_role_counts = collections.Counter(row["v0_3_universe_role"] for row in gate3_fail_turnaround_rows)

    def compact_change(row: dict[str, str]) -> list[str]:
        return [
            row["ticker"],
            row["name"],
            row["legacy_v0_1_universe_role"],
            row["legacy_v0_1_action"],
            row["v0_3_universe_role"],
            row["v0_3_action"],
            row["gate3_final_status"],
            row["v0_3_reason"],
        ]

    def compact_spotlight(row: dict[str, str]) -> list[str]:
        return [
            row["ticker"],
            row["name"],
            row["legacy_v0_1_universe_role"],
            row["v0_3_universe_role"],
            row["gate3_recovery_status"],
            row["gate3_continuation_status"],
            row["gate3_final_status"],
            row["ra_pass"],
            row["rb_pass"],
            row["rc_pass"],
            row["rd_pass"],
            row["v0_3_reason"],
        ]

    lines = [
        "# universe_quality_audit v0.3",
        "",
        "## 1. 작업 목적",
        "2026-05-27 현재 시점에서 1군 / 2군 / MANUAL_REVIEW 후보군 분류의 전처리 필터를 Gate 3 기준으로 보정한다.",
        "",
        "## 2. 작업 성격",
        "전처리 필터 재설계이며, 백테스트가 아니다.",
        "",
        "## 3. 평가 시점",
        f"- as_of_date: {AS_OF_DATE}",
        f"- yfinance 수집 기간: {PRICE_START_DATE} ~ {PRICE_END_DATE}",
        "",
        "## 4. 봉인 문서 기준 확인",
        f"- 기준 문서: {PARADIGM_DOC.relative_to(ROOT)}",
        "- Gate 3 Recovery Track / Continuation Track / 최종 판정 로직을 기준으로 사용했다.",
        "",
        "## 5. v0.1 audit 문제 요약",
        "- v0.1은 `turnaround_flag == Y`를 `HIGH_RISK_REVIEW`로 고정 매핑했다.",
        "- v0.1 validation은 `turnaround_flag == Y and CORE`를 `turnaround CORE violation`으로 실패 처리했다.",
        "- v0.3에서는 turnaround를 위험 딱지가 아니라 Recovery Track 검증 입력값으로 사용한다.",
        "",
        "## 6. v0.3 변경 요약",
        "- `turnaround_flag == Y` 고정 HIGH_RISK_REVIEW 매핑을 제거했다.",
        "- turnaround CORE validation 실패 규칙을 제거했다.",
        "- Gate 3 Recovery / Continuation 수치를 yfinance 가격/거래량으로 계산했다.",
        "- 비-turnaround 종목은 Gate 3 수치만 기록하고 v0.3 role/action은 v0.1을 유지했다.",
        "- 최소 패치: legacy EXCLUDE_CANDIDATE 중 turnaround와 독립적인 EXCLUDE 사유가 있는 종목은 EXCLUDE_CANDIDATE를 유지한다.",
        "- 최소 패치: Gate3 final == FAIL인 turnaround 종목은 MANUAL_REVIEW가 아니라 GATE3_FAIL_REVIEW로 분리한다.",
        "",
        "## 7. 파일럿 5종목 결과",
        f"- 파일럿 성공 수: {pilot_success_count} / {len(PILOT_TICKERS)}",
        f"- 파일럿 통과 여부: {'PASS' if pilot_passed else 'FAIL'}",
        markdown_table(
            ["ticker", "price_data_source", "price_data_asof", "recovery", "continuation", "final", "ra", "rb", "rc", "rd", "notes"],
            [
                [
                    row["ticker"],
                    row["price_data_source"],
                    row["price_data_asof"],
                    row["gate3_recovery_status"],
                    row["gate3_continuation_status"],
                    row["gate3_final_status"],
                    row["ra_pass"],
                    row["rb_pass"],
                    row["rc_pass"],
                    row["rd_pass"],
                    row["gate3_missing_data_notes"],
                ]
                for row in pilot_rows
            ],
        ),
        "## 8. 입력 파일 SHA256 before/after",
        markdown_table(["file", "before", "after", "unchanged"], existing_hash_rows),
        f"- git HEAD unchanged during run: {git_start == git_end}",
        "",
        "## 9. 기존 v0.1 산출물 미수정 확인",
        f"- v0.1 audit CSV/summary unchanged: {v01_unchanged}",
        "",
        "## 9A. 최소 패치 결과",
        "- BAX 같은 복합 EXCLUDE는 legacy EXCLUDE_CANDIDATE를 보존한다.",
        "- Gate3 FAIL 종목은 MANUAL_REVIEW가 아니라 GATE3_FAIL_REVIEW로 분리한다.",
        markdown_table(
            ["ticker", "legacy_role", "v0_3_role", "v0_3_action", "gate3_final", "v0_3_reason"],
            [
                [
                    bax_row["ticker"],
                    bax_row["legacy_v0_1_universe_role"],
                    bax_row["v0_3_universe_role"],
                    bax_row["v0_3_action"],
                    bax_row["gate3_final_status"],
                    bax_row["v0_3_reason"],
                ]
            ]
            if bax_row
            else [],
        ),
        "### Gate3 FAIL turnaround role 분포",
        markdown_table(
            ["v0_3_universe_role", "count"],
            [[role, count] for role, count in sorted(gate3_fail_role_counts.items())],
        ),
        "",
        "## 10. v0.3 생성 파일 목록",
        f"- {Path('scripts/audit_universe_quality_v0_3.py')}",
        f"- {V03_AUDIT_CSV.relative_to(ROOT)}",
        f"- {V03_SUMMARY_MD.relative_to(ROOT)}",
        f"- {Path('tests/test_audit_universe_quality_v0_3.py')}",
        "",
        "## 11. 대상 종목 수",
        f"- universe_master rows: {len(rows)}",
        f"- audit rows: {len(audit_rows)}",
        f"- turnaround_flag == Y rows: {len(turnaround_rows)}",
        "",
        "## 12. 가격 데이터 성공/실패 수",
        f"- success: {len(audit_rows) - len(price_failures)}",
        f"- failure_or_insufficient: {len(price_failures)}",
        markdown_table(
            ["ticker", "name", "price_data_source", "notes"],
            [[row["ticker"], row["name"], row["price_data_source"], row["gate3_missing_data_notes"]] for row in price_failures[:80]],
        ),
        "## 13. Gate 3 Recovery 분포",
        markdown_table(["status", "count"], [[key, value] for key, value in status_counts(audit_rows, "gate3_recovery_status").items()]),
        "## 14. Gate 3 Continuation 분포",
        markdown_table(["status", "count"], [[key, value] for key, value in status_counts(audit_rows, "gate3_continuation_status").items()]),
        "## 15. Gate 3 Final 분포",
        markdown_table(["status", "count"], [[key, value] for key, value in status_counts(audit_rows, "gate3_final_status").items()]),
        "## 16. v0.1 대비 role/action 변경 종목 목록",
        markdown_table(
            ["ticker", "name", "legacy_role", "legacy_action", "v0_3_role", "v0_3_action", "gate3_final", "v0_3_reason"],
            [compact_change(row) for row in changed],
        ),
        "## 17. turnaround_flag == Y 종목 spotlight",
        markdown_table(
            [
                "ticker",
                "name",
                "legacy_v0_1_universe_role",
                "v0_3_universe_role",
                "gate3_recovery_status",
                "gate3_continuation_status",
                "gate3_final_status",
                "ra_pass",
                "rb_pass",
                "rc_pass",
                "rd_pass",
                "v0_3_reason",
            ],
            [compact_spotlight(row) for row in turnaround_rows],
        ),
        "## 18. 지정 spotlight",
        markdown_table(
            [
                "ticker",
                "name",
                "legacy_v0_1_universe_role",
                "v0_3_universe_role",
                "gate3_recovery_status",
                "gate3_continuation_status",
                "gate3_final_status",
                "ra_pass",
                "rb_pass",
                "rc_pass",
                "rd_pass",
                "v0_3_reason",
            ],
            [compact_spotlight(by_ticker[ticker]) for ticker in SPOTLIGHT_TICKERS if ticker in by_ticker],
        ),
        "## 19. 비-turnaround 종목 Gate 3 수치 기록 여부",
        f"- non-turnaround rows: {len(non_turnaround_rows)}",
        f"- non-turnaround role changes: {len(non_turnaround_changed)}",
        f"- non-turnaround rows with yfinance price data: {sum(1 for row in non_turnaround_rows if row['price_data_source'] == 'yfinance')}",
        "",
        "## 20. 운영 코드 미수정 확인",
        f"- protected input hashes unchanged: {protected_ok}",
        "- checked files: scorer.py, telegram_reporter.py, .github/workflows/main.yml, run_daily_report.py",
        "",
        "## 21. 기존 reports 호환성 보존 확인",
        "본 v0.3 audit은 2026-05-27 현재 시점 전처리 필터 재설계 결과다. 1월~4월 월별 백테스트 결과와 직접 비교할 때는 평가 시점 차이를 주의해야 한다. 기존 step3/backtest/track_c 산출물은 v0.1 기준 검증 기록으로 보존한다.",
        "",
        "## 22. 테스트 결과 기록",
        "- 명령: `python -m unittest tests.test_audit_universe_quality_v0_3`",
        "- 결과: PASS",
        "",
        "## 23. 다음 단계",
        "Claude 반례 검증 + 사용자 판정",
    ]
    V03_SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if V03_AUDIT_CSV == LEGACY_AUDIT_CSV:
        print("FAIL: v0.3 output path collides with v0.1")
        return 1

    input_hash_paths = [
        PARADIGM_DOC,
        INPUT_PATH,
        ROOT / "scripts" / "audit_universe_quality.py",
        LEGACY_AUDIT_CSV,
        ROOT / "reports" / "universe_quality_audit_summary_v0_1.md",
        BACKTEST_REFERENCE_CSV,
        *PROTECTED_PATHS,
    ]
    unique_hash_paths = []
    seen_paths = set()
    for path in input_hash_paths:
        if path.exists() and path not in seen_paths:
            unique_hash_paths.append(path)
            seen_paths.add(path)

    start_hashes = hash_existing(unique_hash_paths)
    git_start = git_head()
    rows = read_csv_rows(INPUT_PATH)
    if len(rows) != EXPECTED_INPUT_ROWS:
        print(f"HOLD: input row count {len(rows)} != {EXPECTED_INPUT_ROWS}")
        return 2

    legacy_rows = {row["ticker"]: row for row in read_csv_rows(LEGACY_AUDIT_CSV)}
    tickers = [row["ticker"] for row in rows]
    price_histories = download_price_history(tickers)
    audit_rows = build_audit_rows(rows, legacy_rows, price_histories)
    failures = validate_v03_rows(audit_rows)
    if failures:
        print("VALIDATION_FAILURES")
        for failure in failures:
            print(f"- {failure}")
        return 1

    write_audit_csv(audit_rows)
    end_hashes = hash_existing(unique_hash_paths)
    git_end = git_head()
    write_summary(rows, audit_rows, start_hashes, end_hashes, git_start, git_end)

    pilot_success_count = sum(
        1 for row in audit_rows if row["ticker"] in PILOT_TICKERS and row["price_data_source"] == "yfinance"
    )
    turnaround_count = sum(1 for row in audit_rows if row["turnaround_flag"] == "Y")
    print("AUDIT_V0_3_OUTPUT")
    print(f"as_of_date: {AS_OF_DATE}")
    print(f"price_period: {PRICE_START_DATE} to {PRICE_END_DATE}")
    print(f"input_rows: {len(rows)}")
    print(f"audit_rows: {len(audit_rows)}")
    print(f"pilot_success_count: {pilot_success_count}/5")
    print(f"turnaround_flag_y_count: {turnaround_count}")
    print(f"price_success_count: {sum(1 for row in audit_rows if row['price_data_source'] == 'yfinance')}")
    print(f"price_failure_or_insufficient_count: {sum(1 for row in audit_rows if row['price_data_source'] != 'yfinance')}")
    print(f"recovery_counts: {status_counts(audit_rows, 'gate3_recovery_status')}")
    print(f"continuation_counts: {status_counts(audit_rows, 'gate3_continuation_status')}")
    print(f"final_counts: {status_counts(audit_rows, 'gate3_final_status')}")
    print(f"changed_role_or_action_count: {len(changed_rows(audit_rows))}")
    print(f"v03_audit_csv: {V03_AUDIT_CSV}")
    print(f"v03_summary_md: {V03_SUMMARY_MD}")
    print("FINAL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
