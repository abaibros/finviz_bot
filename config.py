"""
설정 파일: Finviz URL·상수·점수화 설정
"""

# =========================
# 모듈 1: Finviz URL 설정
# =========================

FINVIZ_URLS = {
    "A": "https://finviz.com/screener.ashx?v=111&f=cap_midover,earningsdate_thisweek,fa_epsqoq_pos,fa_salesqoq_pos,sh_avgvol_o500,ta_beta_u2,ta_perf_1wdown",

    "C": "https://finviz.com/screener.ashx?v=111&f=cap_midover,fa_roe_o15,fa_salesqoq_o5,sh_avgvol_o1000,ta_beta_u2,ta_perf_52w30u",

    "D": "https://finviz.com/screener.ashx?v=111&f=cap_largeover,fa_roe_o15,sh_avgvol_o1000,ta_beta_u2,ta_perf_1w10u",

    "E": "https://finviz.com/screener.ashx?v=111&f=an_recom_hold,cap_midover,fa_roe_o15,fa_salesqoq_o5,sh_avgvol_o1000,ta_beta_u2",
}


AREA_DESCRIPTIONS = {
    "A": "어닝 후 과민반응",
    "C": "1년 대폭 하락 우량주",
    "D": "셀오프 직격 우량주",
    "E": "컨센서스 외면 영역",
}


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


REQUEST_DELAY = 2.0
MAX_PAGES_PER_URL = 5
ITEMS_PER_PAGE = 20
MAX_RETRIES = 3
RETRY_DELAY = 2.0


# =========================
# 모듈 3: 점수화 설정
# =========================

VIX_PANIC_THRESHOLD = 25.0
AREA_D_REDUCTION_FACTOR = 0.5


SCORE_THRESHOLDS = {
    "strong": 80,
    "candidate": 60,
    "weak": 40,
}


REQUIRED_COLUMNS = [
    "current_price",
    "market_cap",
    "return_1y_pct",
    "drawdown_from_52w_high_pct",
    "volume",
]


OPTIONAL_COLUMNS = [
    "roe",
    "revenue_growth",
    "beta",
    "trailing_pe",
    "debt_to_equity",
]