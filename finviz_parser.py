"""
모듈 1: Finviz HTML 파싱 → 종목 티커 추출
"""

import re
import time
import requests

from config import (
    FINVIZ_URLS,
    AREA_DESCRIPTIONS,
    REQUEST_HEADERS,
    REQUEST_DELAY,
    MAX_PAGES_PER_URL,
    ITEMS_PER_PAGE,
    MAX_RETRIES,
    RETRY_DELAY,
)


def fetch_page(url, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=15,
            )

            print(f"HTTP 상태: {response.status_code}")

            if response.status_code == 200:
                return response.text

            if response.status_code in [403, 429]:
                print(f"접속 제한 가능성: HTTP {response.status_code}")
                time.sleep(RETRY_DELAY * 2)
                continue

            print(f"HTTP 오류: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"요청 실패: {e}")

        time.sleep(RETRY_DELAY)

    return None


def clean_ticker(raw):
    ticker = raw.strip().upper()

    if not ticker:
        return None

    banned_words = {
        "USA", "CHINA", "BRAZIL", "ISRAEL", "CANADA", "MEXICO",
        "ENERGY", "TECHNOLOGY", "HEALTHCARE", "FINANCIAL",
        "INDUSTRIALS", "BASIC", "MATERIALS", "CONSUMER",
        "DEFENSIVE", "CYCLICAL", "REAL", "ESTATE", "UTILITIES",
        "COMMUNICATION", "SERVICES", "ETF", "STOCK", "NEWS",
        "MAPS", "HOME", "LOGIN", "REGISTER", "HELP"
    }

    if ticker in banned_words:
        return None

    if len(ticker) > 7:
        return None

    if not ticker.replace(".", "").replace("-", "").isalnum():
        return None

    return ticker


def parse_tickers_from_html(html):
    """
    Finviz HTML에서 티커 추출.
    현재 Finviz HTML은 quote.ashx?t= 외에도
    screener row 안에 data-url="/quote.ashx?t=XXX" 형태가 섞일 수 있음.
    그래서 정규식 여러 개로 잡는다.
    """

    raw_matches = []

    patterns = [
        r'quote\.ashx\?t=([A-Za-z0-9.\-]+)',
        r'/quote\.ashx\?t=([A-Za-z0-9.\-]+)',
        r'data-url=["\']/quote\.ashx\?t=([A-Za-z0-9.\-]+)',
        r'href=["\']/quote\.ashx\?t=([A-Za-z0-9.\-]+)',
        r'href=["\']quote\.ashx\?t=([A-Za-z0-9.\-]+)',
        r'"ticker"\s*:\s*"([A-Za-z0-9.\-]+)"',
        r"'ticker'\s*:\s*'([A-Za-z0-9.\-]+)'",
        r'ticker=([A-Za-z0-9.\-]+)',
        r't=([A-Z]{1,6})&',
    ]

    for pattern in patterns:
        found = re.findall(pattern, html, flags=re.IGNORECASE)
        raw_matches.extend(found)

    print(f"디버그 raw match 수: {len(raw_matches)}")
    if raw_matches:
        print(f"디버그 raw 예시: {raw_matches[:30]}")

    tickers = []

    for raw in raw_matches:
        ticker = clean_ticker(raw)

        if ticker and ticker not in tickers:
            tickers.append(ticker)

    return tickers


def fetch_all_pages(base_url, area):
    all_tickers = []

    for page in range(MAX_PAGES_PER_URL):
        if page == 0:
            url = base_url
        else:
            start_row = page * ITEMS_PER_PAGE + 1
            connector = "&" if "?" in base_url else "?"
            url = f"{base_url}{connector}r={start_row}"

        print(f"\n영역 {area} 페이지 {page + 1} 호출")
        print(f"URL: {url}")

        html = fetch_page(url)

        if html is None:
            print(f"영역 {area} 페이지 {page + 1} 실패")
            break

        debug_file = f"debug_area_{area}_page_{page + 1}.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"디버그 HTML 저장: {debug_file}")

        page_tickers = parse_tickers_from_html(html)

        print(f"추출 티커 수: {len(page_tickers)}")

        if not page_tickers:
            print("빈 결과 → 종료")
            break

        print(f"종목 예시: {', '.join(page_tickers[:20])}")

        for ticker in page_tickers:
            if ticker not in all_tickers:
                all_tickers.append(ticker)

        if page < MAX_PAGES_PER_URL - 1:
            time.sleep(REQUEST_DELAY)

    return all_tickers


def fetch_all_areas():
    results = {}

    for area, url in FINVIZ_URLS.items():
        print("\n" + "=" * 60)
        print(f"영역 {area} ({AREA_DESCRIPTIONS[area]}) 시작")
        print("=" * 60)

        tickers = fetch_all_pages(url, area)
        results[area] = tickers

        print(f"\n영역 {area} 완료: 총 {len(tickers)}개 종목")

        time.sleep(REQUEST_DELAY)

    return results


def build_ticker_to_areas(area_results):
    ticker_to_areas = {}

    for area, tickers in area_results.items():
        for ticker in tickers:
            if ticker not in ticker_to_areas:
                ticker_to_areas[ticker] = []

            if area not in ticker_to_areas[ticker]:
                ticker_to_areas[ticker].append(area)

    return ticker_to_areas


def main():
    print("=" * 60)
    print("모듈 1: Finviz 종목 추출 테스트")
    print("=" * 60)

    area_results = fetch_all_areas()

    print("\n" + "=" * 60)
    print("영역별 추출 결과")
    print("=" * 60)

    for area, tickers in area_results.items():
        desc = AREA_DESCRIPTIONS[area]

        print(f"\n[{area}] {desc}: {len(tickers)}개")

        if tickers:
            print(f"종목: {', '.join(tickers[:30])}")

            if len(tickers) > 30:
                print(f"... 외 {len(tickers) - 30}개")
        else:
            print("(해당 없음)")

    ticker_to_areas = build_ticker_to_areas(area_results)

    print("\n" + "=" * 60)
    print("다중 영역 통과 종목")
    print("=" * 60)

    multi_area_tickers = {
        ticker: areas
        for ticker, areas in ticker_to_areas.items()
        if len(areas) >= 2
    }

    if multi_area_tickers:
        for ticker, areas in sorted(
            multi_area_tickers.items(),
            key=lambda x: (-len(x[1]), x[0])
        ):
            print(f"{ticker}: 영역 {', '.join(areas)}")
    else:
        print("다중 영역 통과 종목 없음")

    print("\n" + "=" * 60)
    print("종합 통계")
    print("=" * 60)
    print(f"전체 고유 종목 수: {len(ticker_to_areas)}")
    print(f"다중 영역 통과: {len(multi_area_tickers)}")
    print(f"영역별 합계: {sum(len(t) for t in area_results.values())}")
    print("=" * 60)
    print("모듈 1 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()