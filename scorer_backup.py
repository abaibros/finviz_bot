"""
모듈 3: 종목 점수화 시스템

입력:
- finviz_yfinance_validated.csv

출력:
- finviz_scored.csv

현재 버전:
- D/E 컬럼이 없으면 해당 항목 0점 처리
- 핵심 가격/수익률/거래량 데이터가 없으면 제외
"""

import sys
import pandas as pd
import yfinance as yf

from config import (
    VIX_PANIC_THRESHOLD,
    AREA_D_REDUCTION_FACTOR,
    SCORE_THRESHOLDS,
    REQUIRED_COLUMNS,
)


INPUT_CSV = "finviz_yfinance_validated.csv"
OUTPUT_CSV = "finviz_scored.csv"


def fetch_vix():
    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")

        if hist is None or hist.empty:
            return None

        return float(hist["Close"].iloc[-1])

    except Exception as e:
        print(f"VIX 조회 실패: {e}")
        return None


def fetch_sp500_drawdown():
    try:
        sp = yf.Ticker("^GSPC")
        hist = sp.history(period="1y")

        if hist is None or hist.empty:
            return None

        high = hist["High"].max()
        current = hist["Close"].iloc[-1]

        if high == 0:
            return None

        return float((current - high) / high * 100)

    except Exception as e:
        print(f"S&P 500 조회 실패: {e}")
        return None


def ensure_columns(df):
    """
    필요한 컬럼이 없으면 생성.
    단, 핵심 컬럼은 없으면 종료.
    """

    missing_required = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_required:
        print("필수 컬럼 누락:")
        for col in missing_required:
            print(f"- {col}")
        sys.exit(1)

    optional_defaults = {
        "roe": None,
        "revenue_growth": None,
        "beta": None,
        "trailing_pe": None,
        "debt_to_equity": None,
        "return_5d_pct": None,
        "areas": "",
        "area_count": 0,
    }

    for col, default in optional_defaults.items():
        if col not in df.columns:
            df[col] = default

    return df


def filter_required_data(df):
    original_count = len(df)

    df_filtered = df.dropna(
        subset=REQUIRED_COLUMNS
    ).copy()

    excluded = original_count - len(df_filtered)

    return df_filtered, excluded


def score_roe(roe):
    """
    ROE 점수: 최대 15점
    ROE 15% = 0점
    ROE 45% 이상 = 15점
    """

    if pd.isna(roe):
        return 0.0

    score = (roe - 15) * 0.5

    return max(0.0, min(15.0, score))


def score_debt_equity(de):
    """
    D/E 점수: 최대 10점
    현재 CSV에 debt_to_equity가 없으면 0점.
    """

    if pd.isna(de):
        return 0.0

    de_ratio = de / 100 if de > 10 else de

    score = (2 - de_ratio) * 5

    return max(0.0, min(10.0, score))


def score_revenue_growth(revenue_growth):
    """
    매출 성장률 점수: 최대 20점
    5% = 0점
    25% 이상 = 20점
    """

    if pd.isna(revenue_growth):
        return 0.0

    rg = revenue_growth * 100 if abs(revenue_growth) < 1 else revenue_growth

    score = (rg - 5) * 1

    return max(0.0, min(20.0, score))


def score_drawdown(return_1y_pct, return_5d_pct, areas):
    """
    낙폭 과대 점수: 최대 25점

    C 영역:
    1년 -30% = 0점
    1년 -60% 이하 = 15점

    D 영역:
    5일 -10% = 0점
    5일 -20% 이하 = 10점
    """

    score = 0.0

    if "C" in areas and not pd.isna(return_1y_pct):
        c_score = (abs(return_1y_pct) - 30) * 0.5
        score += max(0.0, min(15.0, c_score))

    if "D" in areas and not pd.isna(return_5d_pct):
        d_score = (abs(return_5d_pct) - 10) * 1.0
        score += max(0.0, min(10.0, d_score))

    return score


def score_volume(volume):
    """
    거래량 점수: 최대 10점
    100만 = 0점
    1,100만 이상 = 10점
    """

    if pd.isna(volume) or volume <= 0:
        return 0.0

    volume_m = volume / 1_000_000

    score = (volume_m - 1) * 1

    return max(0.0, min(10.0, score))


def score_beta(beta):
    """
    Beta 점수: 최대 10점
    Beta 2 = 0점
    Beta 0 = 10점
    """

    if pd.isna(beta):
        return 0.0

    score = (2 - beta) * 5

    return max(0.0, min(10.0, score))


def score_multi_area(area_count):
    """
    다중 영역 점수: 최대 10점
    """

    if pd.isna(area_count):
        return 0.0

    try:
        area_count = int(area_count)
    except Exception:
        return 0.0

    if area_count >= 4:
        return 10.0

    if area_count == 3:
        return 8.0

    if area_count == 2:
        return 5.0

    return 0.0


def apply_vix_weighting(drawdown_score, areas, vix):
    """
    VIX 25 미만이면 D 영역 낙폭 점수 감산.
    """

    if vix is None:
        return drawdown_score

    if vix >= VIX_PANIC_THRESHOLD:
        return drawdown_score

    if "D" not in areas:
        return drawdown_score

    if "C" in areas:
        return drawdown_score * 0.8

    return drawdown_score * AREA_D_REDUCTION_FACTOR


def calculate_score(row, vix):
    areas_raw = row.get("areas", "")

    if isinstance(areas_raw, str):
        areas = [
            area.strip()
            for area in areas_raw.split(",")
            if area.strip()
        ]
    else:
        areas = []

    area_count = len(areas)

    s_roe = score_roe(row.get("roe"))
    s_de = score_debt_equity(row.get("debt_to_equity"))
    s_revenue = score_revenue_growth(row.get("revenue_growth"))

    s_drawdown_raw = score_drawdown(
        row.get("return_1y_pct"),
        row.get("return_5d_pct"),
        areas,
    )

    s_drawdown = apply_vix_weighting(
        s_drawdown_raw,
        areas,
        vix,
    )

    s_volume = score_volume(row.get("volume"))
    s_beta = score_beta(row.get("beta"))
    s_multi = score_multi_area(area_count)

    total = (
        s_roe
        + s_de
        + s_revenue
        + s_drawdown
        + s_volume
        + s_beta
        + s_multi
    )

    total = round(total, 2)

    if total >= SCORE_THRESHOLDS["strong"]:
        grade = "강력 후보"
    elif total >= SCORE_THRESHOLDS["candidate"]:
        grade = "후보"
    elif total >= SCORE_THRESHOLDS["weak"]:
        grade = "약한 후보"
    else:
        grade = "제외"

    return {
        "score_roe": round(s_roe, 2),
        "score_de": round(s_de, 2),
        "score_revenue_growth": round(s_revenue, 2),
        "score_drawdown": round(s_drawdown, 2),
        "score_volume": round(s_volume, 2),
        "score_beta": round(s_beta, 2),
        "score_multi_area": round(s_multi, 2),
        "total_score": total,
        "grade": grade,
    }


def main():
    print("=" * 70)
    print("모듈 3: 종목 점수화 시스템")
    print("=" * 70)

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"{INPUT_CSV} 파일 없음. 모듈 2 먼저 실행.")
        sys.exit(1)

    print(f"{INPUT_CSV} 로드 완료: {len(df)}개 종목")

    print("\nCSV 컬럼:")
    print(list(df.columns))

    df = ensure_columns(df)

    df_valid, excluded_count = filter_required_data(df)

    print("\n핵심 데이터 누락 제외:")
    print(f"- 제외: {excluded_count}개")
    print(f"- 잔여: {len(df_valid)}개")

    if len(df_valid) == 0:
        print("유효 종목 없음")
        sys.exit(1)

    print("\n시장 환경 조회")
    vix = fetch_vix()
    sp_drawdown = fetch_sp500_drawdown()

    if vix is not None:
        print(f"VIX: {vix:.2f}")

        if vix >= VIX_PANIC_THRESHOLD:
            print("셀오프 환경: D 영역 정상 가중")
        else:
            print("평시 환경: D 영역 감산 적용")
    else:
        print("VIX 조회 실패: D 영역 정상 가중")

    if sp_drawdown is not None:
        print(f"S&P 500 52주 고점 대비: {sp_drawdown:.2f}%")

    print("\n점수 계산 시작")

    score_rows = df_valid.apply(
        lambda row: calculate_score(row, vix),
        axis=1,
        result_type="expand",
    )

    df_scored = pd.concat(
        [
            df_valid.reset_index(drop=True),
            score_rows.reset_index(drop=True),
        ],
        axis=1,
    )

    df_scored = df_scored.sort_values(
        by="total_score",
        ascending=False,
    ).reset_index(drop=True)

    df_scored.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n등급별 분포:")
    grade_counts = df_scored["grade"].value_counts()

    for grade, count in grade_counts.items():
        print(f"- {grade}: {count}개")

    print("\n상위 20개 미리보기:")
    preview_cols = [
        "ticker",
        "areas",
        "area_count",
        "total_score",
        "grade",
        "score_roe",
        "score_de",
        "score_revenue_growth",
        "score_drawdown",
        "score_volume",
        "score_beta",
        "score_multi_area",
        "return_5d_pct",
        "return_1y_pct",
        "drawdown_from_52w_high_pct",
        "roe",
        "revenue_growth",
        "sector",
    ]

    existing_preview_cols = [
        col for col in preview_cols
        if col in df_scored.columns
    ]

    print(
        df_scored[existing_preview_cols]
        .head(20)
        .to_string(index=False)
    )

    print("\n저장 완료:")
    print(f"- {OUTPUT_CSV}")

    print("\n메타 정보:")
    print(f"- 원본 종목: {len(df)}")
    print(f"- 유효 종목: {len(df_valid)}")
    print(f"- VIX: {vix if vix is not None else 'N/A'}")
    print(f"- 최고 점수: {df_scored['total_score'].iloc[0]:.2f}")
    print(f"- 최저 점수: {df_scored['total_score'].iloc[-1]:.2f}")
    print(f"- 평균 점수: {df_scored['total_score'].mean():.2f}")

    print("=" * 70)
    print("모듈 3 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()