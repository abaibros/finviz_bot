#!/usr/bin/env python3
"""Generate a metadata-only universe quality audit from universe_master.csv."""

from __future__ import annotations

import collections
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "universe_master.csv"
REPORT_DIR = ROOT / "reports"
AUDIT_CSV = REPORT_DIR / "universe_quality_audit_v0_1.csv"
SUMMARY_MD = REPORT_DIR / "universe_quality_audit_summary_v0_1.md"
EXPECTED_INPUT_ROWS = 656

OUTPUT_FIELDS = [
    "ticker",
    "name",
    "market",
    "sector",
    "sub_industry",
    "market_cap_usd_b",
    "source",
    "company_type",
    "turnaround_flag",
    "universe_role",
    "quality_risk_level",
    "risk_flags",
    "review_reason",
    "recommended_next_action",
]

ALLOWED_ROLES = {
    "CORE",
    "EXTENDED",
    "HIGH_RISK_REVIEW",
    "DISCOVERY_ONLY",
    "EXCLUDE_CANDIDATE",
}
ALLOWED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"}
ALLOWED_RISK_FLAGS = {
    "BIOTECH_RISK",
    "PHARMA_EVENT_RISK",
    "KOSDAQ_THEME_RISK",
    "KOSDAQ_TOP15_RISK",
    "TURNAROUND_RISK",
    "SMALL_CAP_RISK",
    "ADR_FOREIGN_LISTING",
    "HOLDING_COMPANY",
    "TICKER_REVIEW",
    "M_AND_A_REVIEW",
    "DATA_LIMITATION",
    "HEALTHCARE_EVENT_RISK",
    "SECTOR_VOLATILITY",
    "RECENT_INDEX_INCLUSION",
    "NONE",
}
RISK_FLAG_ORDER = [
    "BIOTECH_RISK",
    "PHARMA_EVENT_RISK",
    "KOSDAQ_THEME_RISK",
    "KOSDAQ_TOP15_RISK",
    "TURNAROUND_RISK",
    "SMALL_CAP_RISK",
    "ADR_FOREIGN_LISTING",
    "HOLDING_COMPANY",
    "TICKER_REVIEW",
    "M_AND_A_REVIEW",
    "DATA_LIMITATION",
    "HEALTHCARE_EVENT_RISK",
    "SECTOR_VOLATILITY",
    "RECENT_INDEX_INCLUSION",
]
ALLOWED_ACTIONS = {
    "KEEP_CORE",
    "KEEP_EXTENDED",
    "REVIEW_BEFORE_SCORING",
    "DISCOVERY_ONLY",
    "MANUAL_REVIEW",
    "EXCLUSION_REVIEW",
}
ALLOWED_REASON_CODES = {
    "MARKET_CAP_BELOW_THRESHOLD",
    "BIOTECH_CLINICAL_RISK",
    "PHARMA_EVENT_RISK",
    "KOSDAQ_THEME_SLOT",
    "KOSDAQ_TOP15_RISK",
    "TURNAROUND_IN_PROGRESS",
    "SECTOR_VOLATILITY",
    "HOLDING_COMPANY_NATURE",
    "ADR_LISTING_RISK",
    "RECENT_INDEX_INCLUSION",
    "SMALL_CAP_KOREA",
    "M_AND_A_OR_SPECIAL_SITUATION",
    "TICKER_REVIEW",
    "NO_FINANCIAL_DATA_AVAILABLE",
    "METADATA_ONLY_AUDIT",
}

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


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "GIT_UNAVAILABLE"
    return result.stdout.strip() if result.returncode == 0 else "GIT_HEAD_UNAVAILABLE"


def read_universe() -> list[dict[str, str]]:
    if not INPUT_PATH.exists():
        print("FAIL: universe_master.csv not found")
        sys.exit(1)
    with INPUT_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_cap(row: dict[str, str]) -> float:
    try:
        return float(row.get("market_cap_usd_b") or 0)
    except ValueError:
        return 0.0


def has_any_token(text: str, tokens: list[str]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


def ordered_flags(flags: set[str]) -> str:
    if not flags:
        return "NONE"
    return ";".join(flag for flag in RISK_FLAG_ORDER if flag in flags)


def make_reason(codes: list[str], note: str) -> str:
    unique_codes: list[str] = []
    for code in codes:
        if code not in unique_codes:
            unique_codes.append(code)
    return "; ".join(unique_codes[:3] + [note])


def action_for(role: str, flags: set[str]) -> str:
    if role == "CORE":
        return "KEEP_CORE"
    if role == "EXTENDED":
        return "KEEP_EXTENDED"
    if role == "HIGH_RISK_REVIEW":
        if "TICKER_REVIEW" in flags or "DATA_LIMITATION" in flags:
            return "MANUAL_REVIEW"
        return "REVIEW_BEFORE_SCORING"
    if role == "DISCOVERY_ONLY":
        return "DISCOVERY_ONLY"
    return "EXCLUSION_REVIEW"


def classify(
    row: dict[str, str],
    duplicate_tickers: set[str],
    kr_format_fail: set[str],
) -> dict[str, str]:
    ticker = row["ticker"]
    name = row["name"]
    market = row["market"]
    sector = row["sector"]
    sub_industry = row["sub_industry"]
    source = row["source"]
    company_type = row["company_type"]
    turnaround = row["turnaround_flag"]
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
    if turnaround == "Y":
        flags.add("TURNAROUND_RISK")
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
    if is_health and not (cap >= 100 and is_pharma and turnaround != "Y"):
        flags.add("HEALTHCARE_EVENT_RISK")
    if is_kosdaq and (sub_industry in VOLATILE_KOSDAQ_SUB_INDUSTRIES or name in VOLATILE_KOSDAQ_NAMES):
        flags.add("SECTOR_VOLATILITY")

    if ticker in duplicate_tickers or ticker in kr_format_fail:
        flags.update({"TICKER_REVIEW", "DATA_LIMITATION"})
        role = "EXCLUDE_CANDIDATE"
        risk = "VERY_HIGH"
        reason = make_reason(
            ["TICKER_REVIEW", "NO_FINANCIAL_DATA_AVAILABLE"],
            "ticker structure requires manual review",
        )
    elif has_any_token(text_blob, SPECIAL_SITUATION_TOKENS):
        flags.update({"M_AND_A_REVIEW", "DATA_LIMITATION"})
        role = "EXCLUDE_CANDIDATE"
        risk = "VERY_HIGH"
        reason = make_reason(
            ["M_AND_A_OR_SPECIAL_SITUATION", "NO_FINANCIAL_DATA_AVAILABLE"],
            "special situation marker found in metadata",
        )
    elif turnaround == "Y" and cap < 10 and is_health:
        flags.update({"DATA_LIMITATION", "SMALL_CAP_RISK", "HEALTHCARE_EVENT_RISK"})
        role = "EXCLUDE_CANDIDATE"
        risk = "VERY_HIGH"
        reason = make_reason(
            ["TURNAROUND_IN_PROGRESS", "MARKET_CAP_BELOW_THRESHOLD", "NO_FINANCIAL_DATA_AVAILABLE"],
            "turnaround healthcare row below 10B metadata threshold",
        )
    elif turnaround == "Y":
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["TURNAROUND_IN_PROGRESS", "METADATA_ONLY_AUDIT"],
            "turnaround flag prevents core classification",
        )
    elif is_kosdaq and name in FORCED_KOSDAQ_BIO_NAMES:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        base_code = "PHARMA_EVENT_RISK" if is_pharma else "BIOTECH_CLINICAL_RISK"
        slot_code = "KOSDAQ_THEME_SLOT" if is_theme else "KOSDAQ_TOP15_RISK"
        reason = make_reason(
            [base_code, slot_code, "METADATA_ONLY_AUDIT"],
            "KOSDAQ healthcare row requires event-risk review",
        )
    elif is_kosdaq and is_health and (is_top15 or "KOSDAQ_THEME_BIO" in source) and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "KOSDAQ_TOP15_RISK", "METADATA_ONLY_AUDIT"],
            "KOSDAQ healthcare inclusion is monitoring metadata only",
        )
    elif is_biotech and cap < 30 and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "biotechnology row below 30B metadata threshold",
        )
    elif is_kosdaq and is_top15 and (
        sub_industry in VOLATILE_KOSDAQ_SUB_INDUSTRIES or name in VOLATILE_KOSDAQ_NAMES
    ):
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["KOSDAQ_TOP15_RISK", "SECTOR_VOLATILITY", "METADATA_ONLY_AUDIT"],
            "KOSDAQ top15 sector-volatility marker prevents core classification",
        )
    elif is_biotech and 30 <= cap < 100 and not is_stable_kr_health:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["BIOTECH_CLINICAL_RISK", "METADATA_ONLY_AUDIT"],
            "mid-large biotechnology row needs review before scoring",
        )
    elif is_pharma and is_health and cap < 10:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["PHARMA_EVENT_RISK", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "pharmaceutical row below 10B metadata threshold",
        )
    elif is_theme:
        role = "DISCOVERY_ONLY"
        risk = "HIGH"
        reason = make_reason(
            ["KOSDAQ_THEME_SLOT", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "theme-slot row retained for discovery monitoring only",
        )
    elif cap < 5 or (is_kr and cap < 3):
        role = "DISCOVERY_ONLY"
        risk = "HIGH"
        small_code = "SMALL_CAP_KOREA" if is_kr else "MARKET_CAP_BELOW_THRESHOLD"
        reason = make_reason(
            [small_code, "METADATA_ONLY_AUDIT"],
            "market cap metadata below core threshold",
        )
    elif cap >= 50 and not is_biotech and not (is_kosdaq and is_health) and not is_theme:
        role = "CORE"
        risk = "LOW"
        codes = ["METADATA_ONLY_AUDIT"]
        if company_type == "Holding":
            codes.insert(0, "HOLDING_COMPANY_NATURE")
        elif row.get("adr_flag") == "Y" or "ADR" in source:
            codes.insert(0, "ADR_LISTING_RISK")
        elif "RECENT_INDEX_INCLUSION" in flags:
            codes.insert(0, "RECENT_INDEX_INCLUSION")
        reason = make_reason(
            codes,
            "large-cap metadata row without forced review marker",
        )
    elif cap >= 10:
        role = "EXTENDED"
        risk = "MEDIUM"
        codes = ["MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"]
        if company_type == "Holding":
            codes.insert(0, "HOLDING_COMPANY_NATURE")
        elif row.get("adr_flag") == "Y" or "ADR" in source:
            codes.insert(0, "ADR_LISTING_RISK")
        elif "RECENT_INDEX_INCLUSION" in flags:
            codes.insert(0, "RECENT_INDEX_INCLUSION")
        reason = make_reason(
            codes,
            "below core threshold but retained for extended monitoring",
        )
    elif is_health or "SECTOR_VOLATILITY" in flags:
        role = "HIGH_RISK_REVIEW"
        risk = "HIGH"
        reason = make_reason(
            ["SECTOR_VOLATILITY", "MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "sub-10B metadata row needs review before scoring",
        )
    else:
        role = "EXTENDED"
        risk = "MEDIUM"
        reason = make_reason(
            ["MARKET_CAP_BELOW_THRESHOLD", "METADATA_ONLY_AUDIT"],
            "sub-10B row retained outside core classification",
        )

    return {
        "ticker": ticker,
        "name": name,
        "market": market,
        "sector": sector,
        "sub_industry": sub_industry,
        "market_cap_usd_b": row["market_cap_usd_b"],
        "source": source,
        "company_type": company_type,
        "turnaround_flag": turnaround,
        "universe_role": role,
        "quality_risk_level": risk,
        "risk_flags": ordered_flags(flags),
        "review_reason": reason,
        "recommended_next_action": action_for(role, flags),
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None_\n"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "/") for cell in row) + " |")
    return "\n".join(lines) + "\n"


def sorted_by_cap(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(rows, key=parse_cap, reverse=True)


def write_audit_csv(audit_rows: list[dict[str, str]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows)


def write_summary(rows: list[dict[str, str]], audit_rows: list[dict[str, str]]) -> None:
    by_ticker = {row["ticker"]: row for row in rows}
    role_counts = collections.Counter(row["universe_role"] for row in audit_rows)
    risk_counts = collections.Counter(row["quality_risk_level"] for row in audit_rows)
    market_counts = collections.Counter(row["market"] for row in rows)

    high_risk = sorted_by_cap([row for row in audit_rows if row["universe_role"] == "HIGH_RISK_REVIEW"])
    discovery = sorted_by_cap([row for row in audit_rows if row["universe_role"] == "DISCOVERY_ONLY"])
    exclude = sorted_by_cap([row for row in audit_rows if row["universe_role"] == "EXCLUDE_CANDIDATE"])
    kosdaq = [row for row in audit_rows if row["ticker"].endswith(".KQ")]
    bio_pharma_risk = sorted_by_cap(
        [
            row
            for row in audit_rows
            if any(flag in row["risk_flags"] for flag in ["BIOTECH_RISK", "PHARMA_EVENT_RISK", "HEALTHCARE_EVENT_RISK"])
            and row["universe_role"] in {"HIGH_RISK_REVIEW", "DISCOVERY_ONLY", "EXCLUDE_CANDIDATE"}
        ]
    )
    turnaround = sorted_by_cap([row for row in audit_rows if row["turnaround_flag"] == "Y"])
    large_pharma_not_auto_high = sorted_by_cap(
        [
            row
            for row in audit_rows
            if row["sector"] == "Health Care"
            and row["sub_industry"] == "Pharmaceuticals"
            and parse_cap(row) >= 100
            and row["universe_role"] != "HIGH_RISK_REVIEW"
        ]
    )

    def compact(rows_in: list[dict[str, str]], limit: int | None = None) -> list[list[str]]:
        selected = rows_in if limit is None else rows_in[:limit]
        return [
            [
                row["ticker"],
                row["name"],
                row["market_cap_usd_b"],
                row["universe_role"],
                row["quality_risk_level"],
                row["risk_flags"],
                row["review_reason"],
            ]
            for row in selected
        ]

    lines = [
        "# universe_quality_audit v0.1",
        "",
        "## 1. 작업 목적",
        "현재 universe_master.csv v0.2의 전체 종목을 같은 core 후보로 보지 않도록 메타데이터 기반 1차 위험 분류를 생성한다.",
        "",
        "## 2. 입력 파일 정보",
        f"- 입력 파일: {INPUT_PATH.name}",
        f"- 입력 row 수: {len(rows)}",
        f"- 출력 CSV: {AUDIT_CSV.as_posix()}",
        "",
        "## 3. 전체 종목 수",
        f"- {len(rows)}",
        "",
        "## 4. market별 종목 수",
        markdown_table(["market", "count"], [[market, str(count)] for market, count in sorted(market_counts.items())]),
        "## 5. universe_role별 종목 수",
        markdown_table(["universe_role", "count"], [[role, str(role_counts.get(role, 0))] for role in sorted(ALLOWED_ROLES)]),
        "## 6. quality_risk_level별 종목 수",
        markdown_table(["quality_risk_level", "count"], [[risk, str(risk_counts.get(risk, 0))] for risk in ["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]]),
        "## 7. HIGH_RISK_REVIEW 상위 30개 목록",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(high_risk, 30)),
        "## 8. DISCOVERY_ONLY 목록",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(discovery)),
        "## 9. EXCLUDE_CANDIDATE 목록",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(exclude)),
        "## 10. 한국 KOSDAQ 종목 분류 결과",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(kosdaq)),
        "## 11. 바이오/제약 리스크 종목 목록",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(bio_pharma_risk)),
        "## 12. turnaround_flag == Y 종목 분류 결과",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(turnaround)),
        "## 13. CORE로 분류된 종목 수",
        f"- {role_counts.get('CORE', 0)}",
        "",
        "## 14. 대형 제약사 중 자동 HIGH_RISK_REVIEW로 보내지 않은 종목 목록",
        markdown_table(["ticker", "name", "market_cap_usd_b", "role", "risk", "flags", "reason"], compact(large_pharma_not_auto_high)),
        "## 15. 주의 문구",
        "- 이 audit은 재무 데이터 기반 최종 검증이 아니다.",
        "- 메타데이터 기반 1차 위험 분류다.",
        "- 매수/추천 판단이 아니다.",
        "- Step 3 이전 선별 보조 자료다.",
        "",
        "## 16. 생성 기준 메모",
        "- 외부 데이터 조회 없이 universe_master.csv의 기존 컬럼만 사용했다.",
        "- EXCLUDE_CANDIDATE는 삭제가 아니라 별도 검토 대상으로 표시한 것이다.",
        f"- audit row 수와 입력 row 수 일치: {len(audit_rows) == len(rows)}",
    ]

    unused = by_ticker  # Keeps source-to-audit mapping explicit for future extension.
    if unused is None:
        raise AssertionError("unreachable")
    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(
    rows: list[dict[str, str]],
    audit_rows: list[dict[str, str]],
    start_hash: str,
    end_hash: str,
    start_head: str,
    end_head: str,
) -> list[str]:
    failures: list[str] = []
    audit_by_ticker = {row["ticker"]: row for row in audit_rows}
    tickers = [row["ticker"] for row in rows]

    if len(rows) != EXPECTED_INPUT_ROWS:
        failures.append("input row count is not 656")
    if not AUDIT_CSV.exists():
        failures.append("audit CSV not created")
    if len(audit_rows) != len(rows):
        failures.append("audit row count does not match input")
    if not SUMMARY_MD.exists():
        failures.append("summary md not created")
    if set(audit_by_ticker) != set(tickers):
        failures.append("ticker coverage mismatch")

    for row in audit_rows:
        if row["universe_role"] not in ALLOWED_ROLES:
            failures.append(f"invalid universe_role: {row['ticker']}")
        if row["quality_risk_level"] not in ALLOWED_RISK_LEVELS:
            failures.append(f"invalid quality_risk_level: {row['ticker']}")
        action = row["recommended_next_action"]
        if action not in ALLOWED_ACTIONS:
            failures.append(f"invalid recommended_next_action: {row['ticker']}")
        flags = row["risk_flags"].split(";") if row["risk_flags"] else []
        if any(flag not in ALLOWED_RISK_FLAGS for flag in flags):
            failures.append(f"invalid risk_flags: {row['ticker']}")
        if "NONE" in flags and len(flags) > 1:
            failures.append(f"NONE combined with other risk flags: {row['ticker']}")
        if not any(code in row["review_reason"] for code in ALLOWED_REASON_CODES):
            failures.append(f"review_reason has no allowed code: {row['ticker']}")

    if not any(row["universe_role"] in {"HIGH_RISK_REVIEW", "DISCOVERY_ONLY"} for row in audit_rows):
        failures.append("HIGH_RISK_REVIEW/DISCOVERY_ONLY count is zero")
    if not any(
        row["ticker"].endswith(".KQ") and row["universe_role"] in {"HIGH_RISK_REVIEW", "DISCOVERY_ONLY"}
        for row in audit_rows
    ):
        failures.append("no KOSDAQ row classified as HIGH_RISK_REVIEW/DISCOVERY_ONLY")

    source_by_ticker = {row["ticker"]: row for row in rows}
    for audit in audit_rows:
        source_row = source_by_ticker[audit["ticker"]]
        cap = parse_cap(source_row)
        if source_row["turnaround_flag"] == "Y" and audit["universe_role"] == "CORE":
            failures.append(f"turnaround CORE violation: {audit['ticker']}")
        if "KOSDAQ_THEME" in source_row["source"] and audit["universe_role"] == "CORE":
            failures.append(f"KOSDAQ_THEME CORE violation: {audit['ticker']}")
        if cap < 5 and audit["universe_role"] == "CORE":
            failures.append(f"small cap CORE violation: {audit['ticker']}")
        if (
            audit["universe_role"] == "EXCLUDE_CANDIDATE"
            and "M_AND_A_REVIEW" not in audit["risk_flags"]
            and "TICKER_REVIEW" not in audit["risk_flags"]
            and "DATA_LIMITATION" not in audit["risk_flags"]
        ):
            failures.append(f"EXCLUDE_CANDIDATE missing review flag: {audit['ticker']}")

    for name in FORCED_KOSDAQ_BIO_NAMES:
        for audit in audit_rows:
            if audit["name"] == name and audit["universe_role"] == "CORE":
                failures.append(f"KOSDAQ bio/pharma CORE violation: {audit['ticker']}")

    if start_hash != end_hash:
        failures.append("universe_master.csv hash changed during script run")
    if start_head != end_head:
        failures.append("git HEAD changed during script run")
    return failures


def main() -> int:
    start_hash = file_hash(INPUT_PATH) if INPUT_PATH.exists() else ""
    start_head = git_head()
    rows = read_universe()
    if len(rows) != EXPECTED_INPUT_ROWS:
        print(f"HOLD: input row count {len(rows)} != {EXPECTED_INPUT_ROWS}")
        return 2

    ticker_counts = collections.Counter(row["ticker"] for row in rows)
    duplicate_tickers = {ticker for ticker, count in ticker_counts.items() if count > 1}
    kr_format_fail = {
        row["ticker"]
        for row in rows
        if row["market"] == "KR" and not KR_TICKER_RE.match(row["ticker"])
    }

    audit_rows = [classify(row, duplicate_tickers, kr_format_fail) for row in rows]
    write_audit_csv(audit_rows)
    write_summary(rows, audit_rows)

    end_hash = file_hash(INPUT_PATH)
    end_head = git_head()
    failures = validate(rows, audit_rows, start_hash, end_hash, start_head, end_head)

    role_counts = collections.Counter(row["universe_role"] for row in audit_rows)
    risk_counts = collections.Counter(row["quality_risk_level"] for row in audit_rows)
    kosdaq_risk_count = sum(
        1
        for row in audit_rows
        if row["ticker"].endswith(".KQ")
        and row["universe_role"] in {"HIGH_RISK_REVIEW", "DISCOVERY_ONLY"}
    )
    bio_pharma_count = sum(
        1
        for row in audit_rows
        if any(flag in row["risk_flags"] for flag in ["BIOTECH_RISK", "PHARMA_EVENT_RISK", "HEALTHCARE_EVENT_RISK"])
        and row["universe_role"] in {"HIGH_RISK_REVIEW", "DISCOVERY_ONLY", "EXCLUDE_CANDIDATE"}
    )
    turnaround_count = sum(1 for row in rows if row["turnaround_flag"] == "Y")
    exclude_count = role_counts.get("EXCLUDE_CANDIDATE", 0)

    print("AUDIT_OUTPUT")
    print(f"input_rows: {len(rows)}")
    print(f"audit_rows: {len(audit_rows)}")
    print(f"market_counts: {dict(collections.Counter(row['market'] for row in rows))}")
    print(f"role_counts: {dict(role_counts)}")
    print(f"risk_counts: {dict(risk_counts)}")
    print(f"kosdaq_high_or_discovery: {kosdaq_risk_count}")
    print(f"bio_pharma_risk_count: {bio_pharma_count}")
    print(f"turnaround_flag_y_count: {turnaround_count}")
    print(f"exclude_candidate_count: {exclude_count}")
    print(f"universe_hash_unchanged: {start_hash == end_hash}")
    print(f"git_head_unchanged: {start_head == end_head}")
    print(f"audit_csv: {AUDIT_CSV}")
    print(f"summary_md: {SUMMARY_MD}")
    if failures:
        print("VALIDATION_FAILURES")
        for failure in failures:
            print(f"- {failure}")
        print("FINAL: FAIL")
        return 1
    print("VALIDATION_FAILURES: []")
    print("FINAL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
