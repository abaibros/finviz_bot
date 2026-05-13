"""
모듈 2-3: yfinance 실전 검증기 + 애널리스트 정보 추가

입력:
- Finviz 후보 티커

출력:
- finviz_yfinance_validated.csv

추가 컬럼:
- recommendation
- analyst_recommendation_mean
- analyst_opinion_count
"""

import time
import math
import pandas as pd
import yfinance as yf

from finviz_parser import fetch_all_areas, build_ticker_to_areas


OUTPUT_CSV = "finviz_yfinance_validated.csv"
REQUEST_DELAY = 0.4


def safe_round(value, digits=2):
    if value is None:
        return None

    try:
        if isinstance(value, float) and math.isnan(value):
            return None
        return round(float(value), digits)

    except Exception:
        return None


def safe_number(value):
    if value is None:
        return None

    try:
        if isinstance(value, float) and math.isnan(value):
            return None
        return value

    except Exception:
        return None


def calc_return(start_price, end_price):
    if start_price is None or end_price is None:
        return None

    try:
        if start_price == 0:
            return None
        return ((end_price / start_price) - 1) * 100

    except Exception:
        return None


def get_price_metrics(ticker):
    result = {
        "current_price": None,
        "return_5d_pct": None,
        "return_1m_pct": None,
        "return_1y_pct": None,
        "high_52w": None,
        "low_52w": None,
        "drawdown_from_52w_high_pct": None,
        "upside_from_52w_low_pct": None,
    }

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y", interval="1d", auto_adjust=True)

        if hist is None or hist.empty:
            return result

        close = hist["Close"].dropna()

        if close.empty:
            return result

        current_price = float(close.iloc[-1])
        high_52w = float(close.max())
        low_52w = float(close.min())

        result["current_price"] = safe_round(current_price)
        result["high_52w"] = safe_round(high_52w)
        result["low_52w"] = safe_round(low_52w)

        if len(close) >= 6:
            result["return_5d_pct"] = safe_round(
                calc_return(float(close.iloc[-6]), current_price)
            )

        if len(close) >= 22:
            result["return_1m_pct"] = safe_round(
                calc_return(float(close.iloc[-22]), current_price)
            )

        if len(close) >= 2:
            result["return_1y_pct"] = safe_round(
                calc_return(float(close.iloc[0]), current_price)
            )

        if high_52w and high_52w > 0:
            result["drawdown_from_52w_high_pct"] = safe_round(
                calc_return(high_52w, current_price)
            )

        if low_52w and low_52w > 0:
            result["upside_from_52w_low_pct"] = safe_round(
                calc_return(low_52w, current_price)
            )

        return result

    except Exception as e:
        print(f"  가격 데이터 오류: {e}")
        return result


def get_info_metrics(ticker):
    result = {
        "market_cap": None,
        "trailing_pe": None,
        "forward_pe": None,
        "volume": None,
        "average_volume": None,
        "sector": None,
        "industry": None,
        "beta": None,
        "roe": None,
        "revenue_growth": None,
        "earnings_growth": None,
        "debt_to_equity": None,
        "recommendation": None,
        "analyst_recommendation_mean": None,
        "analyst_opinion_count": None,
    }

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        result["market_cap"] = safe_number(info.get("marketCap"))
        result["trailing_pe"] = safe_round(info.get("trailingPE"))
        result["forward_pe"] = safe_round(info.get("forwardPE"))
        result["volume"] = safe_number(info.get("volume"))
        result["average_volume"] = safe_number(info.get("averageVolume"))
        result["sector"] = info.get("sector")
        result["industry"] = info.get("industry")
        result["beta"] = safe_round(info.get("beta"))

        roe = info.get("returnOnEquity")
        if roe is not None:
            result["roe"] = safe_round(roe * 100)

        revenue_growth = info.get("revenueGrowth")
        if revenue_growth is not None:
            result["revenue_growth"] = safe_round(revenue_growth * 100)

        earnings_growth = info.get("earningsGrowth")
        if earnings_growth is not None:
            result["earnings_growth"] = safe_round(earnings_growth * 100)

        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity is not None:
            result["debt_to_equity"] = safe_round(debt_to_equity)

        result["recommendation"] = info.get("recommendationKey")

        recommendation_mean = info.get("recommendationMean")
        if recommendation_mean is not None:
            result["analyst_recommendation_mean"] = safe_round(
                recommendation_mean
            )

        analyst_count = info.get("numberOfAnalystOpinions")
        if analyst_count is not None:
            result["analyst_opinion_count"] = int(analyst_count)

        return result

    except Exception as e:
        print(f"  기본 정보 오류: {e}")
        return result


def validate_one_ticker(ticker, areas):
    print(f"검증 중: {ticker} / 영역: {','.join(areas)}")

    price_metrics = get_price_metrics(ticker)
    info_metrics = get_info_metrics(ticker)

    row = {
        "ticker": ticker,
        "areas": ",".join(areas),
        "area_count": len(areas),
    }

    row.update(price_metrics)
    row.update(info_metrics)

    return row


def sort_results(df):
    sort_df = df.copy()

    sort_df["sort_drawdown"] = sort_df["drawdown_from_52w_high_pct"].fillna(0)
    sort_df["sort_volume"] = sort_df["volume"].fillna(0)

    sort_df = sort_df.sort_values(
        by=["area_count", "sort_drawdown", "sort_volume"],
        ascending=[False, True, False],
    )

    sort_df = sort_df.drop(columns=["sort_drawdown", "sort_volume"])

    return sort_df


def main():
    print("=" * 70)
    print("모듈 2-3: yfinance 검증기 + 애널리스트 정보 추가")
    print("=" * 70)

    print("\n1단계: Finviz 후보 수집")
    area_results = fetch_all_areas()

    ticker_to_areas = build_ticker_to_areas(area_results)
    all_tickers = sorted(ticker_to_areas.keys())

    print("\n" + "=" * 70)
    print("Finviz 수집 결과")
    print("=" * 70)

    for area, tickers in area_results.items():
        print(f"영역 {area}: {len(tickers)}개")

    print(f"전체 고유 티커: {len(all_tickers)}개")

    rows = []

    print("\n" + "=" * 70)
    print("2단계: yfinance 검증 시작")
    print("=" * 70)

    for idx, ticker in enumerate(all_tickers, start=1):
        print(f"\n[{idx}/{len(all_tickers)}]")

        areas = ticker_to_areas.get(ticker, [])
        row = validate_one_ticker(ticker, areas)
        rows.append(row)

        time.sleep(REQUEST_DELAY)

    df = pd.DataFrame(rows)
    df = sort_results(df)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 70)
    print("검증 완료")
    print("=" * 70)

    print(f"CSV 저장 완료: {OUTPUT_CSV}")
    print(f"총 검증 종목 수: {len(df)}")

    print("\n애널리스트 컬럼 확인:")
    for col in [
        "recommendation",
        "analyst_recommendation_mean",
        "analyst_opinion_count",
    ]:
        if col in df.columns:
            non_null_count = df[col].notna().sum()
            print(f"{col}: {non_null_count}/{len(df)}")
        else:
            print(f"{col}: 없음")

    print("\n상위 20개 후보 미리보기:")
    preview_cols = [
        "ticker",
        "areas",
        "area_count",
        "current_price",
        "return_5d_pct",
        "return_1y_pct",
        "drawdown_from_52w_high_pct",
        "roe",
        "debt_to_equity",
        "revenue_growth",
        "recommendation",
        "analyst_recommendation_mean",
        "analyst_opinion_count",
        "sector",
    ]

    existing_cols = [
        col for col in preview_cols
        if col in df.columns
    ]

    print(df[existing_cols].head(20).to_string(index=False))

    print("=" * 70)


if __name__ == "__main__":
    main()