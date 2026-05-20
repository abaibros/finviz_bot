import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

from watchlist_logger import (
    WATCHLIST_LOG_CSV,
    append_watchlist_rows,
    assert_no_forbidden_words,
    assert_no_forbidden_words_in_row,
    build_run_id,
    build_watchlist_log_row,
    format_created_at_utc,
    generate_run_timestamp,
    validate_watchlist_log_header,
)


INPUT_CSV = "finviz_scored.csv"
WATCHLIST_ALERT_VERSION = "v1.1.1"
KST = ZoneInfo("Asia/Seoul")

SCORE_STRONG = 70
SCORE_CANDIDATE = 55
VIX_PANIC = 25.0
MAX_MESSAGE_LENGTH = 3900

COLUMN_CANDIDATES = {
    "week52_low": ["week52_low", "fiftyTwoWeekLow", "52w_low", "low_52w"],
    "return_1y": ["return_1y_pct", "return_1y", "1y_return"],
    "roe": ["roe", "returnOnEquity"],
    "revenue_growth": ["revenue_growth", "revenueGrowth"],
    "market_cap": ["market_cap", "marketCap"],
    "current_price": ["current_price", "price", "currentPrice"],
    "recommendation": ["recommendation", "recommendationKey"],
    "analyst_mean": ["analyst_recommendation_mean", "recommendationMean", "recommendation_mean"],
    "analyst_count": ["analyst_opinion_count", "numberOfAnalystOpinions", "analyst_count"],
}


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def resolve_columns(df: pd.DataFrame) -> dict:
    return {
        key: find_column(df, candidates)
        for key, candidates in COLUMN_CANDIDATES.items()
    }


def load_credentials() -> Tuple[str, str]:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("ERROR: .env에 TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 없습니다.")
        sys.exit(1)

    return token, chat_id


def load_scored_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(INPUT_CSV)
        print(f"✅ {INPUT_CSV} 로드: {len(df)}개 종목")
        return df
    except FileNotFoundError:
        print(f"ERROR: {INPUT_CSV} 없음. 먼저 python scorer.py 실행.")
        sys.exit(1)


def fetch_market_environment() -> dict:
    env = {"vix": None, "sp_drawdown_pct": None, "regime": "환경 조회 실패"}

    try:
        vix_hist = yf.Ticker("^VIX").history(period="5d")
        if not vix_hist.empty:
            env["vix"] = round(float(vix_hist["Close"].iloc[-1]), 2)
    except Exception as e:
        print(f"VIX 조회 실패: {e}")

    try:
        sp_hist = yf.Ticker("^GSPC").history(period="1y")
        if not sp_hist.empty:
            high = sp_hist["High"].max()
            current = sp_hist["Close"].iloc[-1]
            if high:
                env["sp_drawdown_pct"] = round(float((current - high) / high * 100), 2)
    except Exception as e:
        print(f"S&P 500 조회 실패: {e}")

    if env["vix"] is not None:
        env["regime"] = "셀오프 환경" if env["vix"] >= VIX_PANIC else "평시 환경"

    return env


def build_watchlist_candidates(df: pd.DataFrame) -> list:
    df_watchlist = df[df["total_score"] >= SCORE_CANDIDATE].copy()
    df_watchlist = df_watchlist.sort_values("total_score", ascending=False).reset_index(drop=True)
    return [row.to_dict() for _, row in df_watchlist.iterrows()]


def build_prospective_watchlist_rows(candidates, run_id, created_at_utc):
    return [
        build_watchlist_log_row(
            candidate=candidate,
            rank=rank,
            run_id=run_id,
            alert_version=WATCHLIST_ALERT_VERSION,
            market="US",
            currency="USD",
            created_at_utc=created_at_utc,
            prior_observation_count=0,
        )
        for rank, candidate in enumerate(candidates, 1)
    ]


def validate_watchlist_payload(message, candidates, run_id, created_at_utc):
    assert_no_forbidden_words(message)
    rows = build_prospective_watchlist_rows(candidates, run_id, created_at_utc)
    for row in rows:
        assert_no_forbidden_words_in_row(row)
    return rows


def fmt_number(v, suffix="", prefix="", decimals=1):
    if v is None or pd.isna(v):
        return "N/A"
    try:
        return f"{prefix}{float(v):.{decimals}f}{suffix}"
    except Exception:
        return "N/A"


def fmt_signed_pct(v):
    if v is None or pd.isna(v):
        return "N/A"
    try:
        val = float(v)
        if abs(val) < 1:
            val *= 100
        sign = "+" if val >= 0 else ""
        return f"{sign}{val:.1f}%"
    except Exception:
        return "N/A"


def fmt_market_cap(v):
    if v is None or pd.isna(v):
        return "N/A"
    try:
        val = float(v)
        if val >= 1e12:
            return f"${val / 1e12:.2f}T"
        if val >= 1e9:
            return f"${val / 1e9:.1f}B"
        if val >= 1e6:
            return f"${val / 1e6:.0f}M"
        return f"${val:.0f}"
    except Exception:
        return "N/A"


def get_value(row, cols, key):
    col = cols.get(key)
    if not col:
        return None
    return row.get(col)


def fmt_analyst(row, cols):
    rec = get_value(row, cols, "recommendation")
    mean = get_value(row, cols, "analyst_mean")
    count = get_value(row, cols, "analyst_count")

    parts = []

    if rec is not None and not pd.isna(rec):
        parts.append(str(rec))

    if mean is not None and not pd.isna(mean):
        parts.append(f"{float(mean):.2f}점")

    if count is not None and not pd.isna(count):
        parts.append(f"{int(float(count))}명")

    return " / ".join(parts) if parts else "N/A"


def format_stock_line(row, cols):
    ticker = row.get("ticker", "N/A")
    score = row.get("total_score", 0)
    areas = row.get("areas", "N/A")

    return (
        f"{ticker} - {float(score):.1f}점 ({areas})\n"
        f"   1년 {fmt_signed_pct(get_value(row, cols, 'return_1y'))} / "
        f"ROE {fmt_number(get_value(row, cols, 'roe'), '%')} / "
        f"매출 {fmt_signed_pct(get_value(row, cols, 'revenue_growth'))}\n"
        f"   시총 {fmt_market_cap(get_value(row, cols, 'market_cap'))} / "
        f"현재가 {fmt_number(get_value(row, cols, 'current_price'), '', '$', 2)}\n"
        f"   52주 저점 {fmt_number(get_value(row, cols, 'week52_low'), '', '$', 2)} / "
        f"애널 {fmt_analyst(row, cols)}"
    )


def build_signal_message(df, env, cols):
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    df_signal = df[df["total_score"] >= SCORE_CANDIDATE].copy()
    df_signal = df_signal.sort_values("total_score", ascending=False)

    df_strong = df_signal[df_signal["total_score"] >= SCORE_STRONG]
    df_candidate = df_signal[
        (df_signal["total_score"] >= SCORE_CANDIDATE)
        & (df_signal["total_score"] < SCORE_STRONG)
    ]

    lines = []
    lines.append(f"🔎 관찰 후보 발견 ({date_str}) - 후보 {len(df_candidate)}")
    lines.append("")
    lines.append("[시장 환경]")
    lines.append(f"VIX: {env['vix'] if env['vix'] is not None else 'N/A'} → {env['regime']}")
    lines.append(f"S&P 500: 52주 고점 {env['sp_drawdown_pct'] if env['sp_drawdown_pct'] is not None else 'N/A'}%")
    lines.append("")
    lines.append("[데이터 출처]")
    lines.append("yfinance / Finviz")
    lines.append(f"(미장 종가 기준, KST {date_str} {time_str} 조회)")
    lines.append("")

    if len(df_strong) > 0:
        lines.append("━━━━━━━━━━━━━━━━")
        lines.append(f"📊 강한 관찰 후보 ({SCORE_STRONG}+)")
        lines.append("━━━━━━━━━━━━━━━━")
        lines.append("")
        for i, (_, row) in enumerate(df_strong.iterrows(), 1):
            lines.append(f"{i}. {format_stock_line(row, cols)}")
            lines.append("")

    if len(df_candidate) > 0:
        lines.append("━━━━━━━━━━━━━━━━")
        lines.append(f"📊 관찰 후보 ({SCORE_CANDIDATE}~{SCORE_STRONG - 1})")
        lines.append("━━━━━━━━━━━━━━━━")
        lines.append("")
        start = len(df_strong) + 1
        for i, (_, row) in enumerate(df_candidate.iterrows(), start):
            lines.append(f"{i}. {format_stock_line(row, cols)}")
            lines.append("")

    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("📌 본인 프로필")
    lines.append("- 인내력 -20%")
    lines.append("- 한 종목 10~15%")
    lines.append("- 모멘텀 충동 → 분할 관찰")
    lines.append("")
    lines.append("⚠️ 본 알림은 영역 A/C/D/E 커버")
    lines.append("영역 B (신 CEO)는 본인 수동 관리")
    lines.append("")
    lines.append("✅ Claude Pro에 그대로 붙여넣고")
    lines.append('"확인해줘" 입력')
    lines.append("→ 정밀 검토 실행")

    return "\n".join(lines)


def build_no_signal_message(env):
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")

    return "\n".join([
        f"📊 관찰 후보 리포트 ({date_str})",
        "",
        f"VIX: {env['vix'] if env['vix'] is not None else 'N/A'}",
        f"S&P 500: 52주 고점 {env['sp_drawdown_pct'] if env['sp_drawdown_pct'] is not None else 'N/A'}%",
        f"→ {env['regime']}",
        "",
        "🔕 관찰 후보 없음",
        f"({SCORE_CANDIDATE}점 이상 종목 없음)",
    ])


def split_message(message, max_length=MAX_MESSAGE_LENGTH):
    if len(message) <= max_length:
        return [message]

    parts = []
    current = ""

    for line in message.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            parts.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line

    if current:
        parts.append(current)

    return [
        f"{part}\n\n[{i + 1}/{len(parts)}]"
        for i, part in enumerate(parts)
    ]


def send_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    parts = split_message(message)

    success_all = True

    for idx, part in enumerate(parts, 1):
        try:
            response = requests.post(
                url,
                data={"chat_id": chat_id, "text": part},
                timeout=10,
            )
            if response.status_code == 200:
                print(f"✅ 메시지 {idx}/{len(parts)} 발송 성공")
            else:
                print(f"❌ 메시지 {idx}/{len(parts)} 실패: {response.status_code}")
                print(response.text)
                success_all = False
        except Exception as e:
            print(f"❌ 메시지 {idx}/{len(parts)} 예외: {e}")
            success_all = False

    return success_all


def send_telegram_and_append_watchlist_log(
    token,
    chat_id,
    message,
    candidates,
    run_id,
    created_at_utc,
    path=WATCHLIST_LOG_CSV,
):
    if candidates:
        validate_watchlist_log_header(path)

    success = send_telegram(token, chat_id, message)
    append_count = 0

    if success:
        append_count = append_watchlist_rows(
            candidates,
            run_id=run_id,
            alert_version=WATCHLIST_ALERT_VERSION,
            market="US",
            currency="USD",
            created_at_utc=created_at_utc,
            path=path,
        )

    return success, append_count


def main():
    print("=" * 60)
    print("모듈 4: 텔레그램 자동 리포트")
    print("=" * 60)

    token, chat_id = load_credentials()
    df = load_scored_data()
    cols = resolve_columns(df)

    print("\n컬럼 매핑 결과:")
    for key, col in cols.items():
        print(f"{'✅' if col else '❌'} {key}: {col or '없음'}")

    env = fetch_market_environment()

    print("\n시장 환경:")
    print(f"VIX: {env['vix']}")
    print(f"S&P 500 52주 고점 대비: {env['sp_drawdown_pct']}%")
    print(f"판정: {env['regime']}")

    signal_count = len(df[df["total_score"] >= SCORE_CANDIDATE])
    print(f"\n{SCORE_CANDIDATE}점 이상 종목: {signal_count}개")

    if signal_count > 0:
        message = build_signal_message(df, env, cols)
    else:
        message = build_no_signal_message(env)

    run_timestamp_utc = generate_run_timestamp()
    created_at_utc = format_created_at_utc(run_timestamp_utc)
    run_id = build_run_id(run_timestamp_utc)
    watchlist_candidates = build_watchlist_candidates(df)
    validate_watchlist_payload(message, watchlist_candidates, run_id, created_at_utc)

    print(f"메시지 길이: {len(message)}자")

    success, append_count = send_telegram_and_append_watchlist_log(
        token,
        chat_id,
        message,
        watchlist_candidates,
        run_id,
        created_at_utc,
    )
    if success:
        print(f"watchlist_log append_count: {append_count}")

    print("=" * 60)
    print("모듈 4 완료" if success else "모듈 4 실패")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
