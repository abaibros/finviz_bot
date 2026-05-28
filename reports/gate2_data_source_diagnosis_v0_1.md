# Gate2 data source diagnosis v0.1

## 1. 작업 요약

이 문서는 Gate2 구현이 아니라 무료 소스 데이터 수집 가능성 진단이다. 1순위 검증축은 PIT(point-in-time) 재현 가능성이고, 2순위는 live 수집 가능성이다.

- 평가일: 2026-05-27
- live 창: 2026-02-27 ~ 2026-05-27
- PIT 테스트 기준일: 2026-01-15
- 표본: INTC, SBUX, BA, DIS, PYPL
- 기준 문서: docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md
- 작업 전 `git fetch origin` 수행: YES
- 운영 코드 수정: NO
- Gate2 룰/판정 엔진 구현: NO
- Telegram/운영 파이프라인 연결: NO

작업 전 `git status -sb`:

```text
## main...origin/main
?? backups/
?? reports/backtest_it_2026q1_data_v0_1.csv
?? reports/backtest_it_2026q1_summary_v0_1.md
?? reports/gate2_data_source_diagnosis_v0_1.md
?? reports/track_c_session_001_ai_assisted_review.xlsx
```

## 2. 샘플 종목 / 평가 기간 / PIT 기준일

| 구분 | 값 |
| --- | --- |
| 샘플 | INTC, SBUX, BA, DIS, PYPL |
| live 창 | 2026-02-27 ~ 2026-05-27 |
| PIT 기준일 | 2026-01-15 |
| negative-control 확장 표본 | 미포함 |
| 판정 목적 | 데이터 소스 진단, 종목 평가 아님 |

## 3. SEC submissions 진단

SEC `company_tickers.json`와 `data.sec.gov/submissions/CIK##########.json`를 사용했다. User-Agent를 포함했고 표본 단위로 rate limit을 피하기 위해 요청 간 짧은 간격을 두었다.

| ticker | CIK mapping | submissions API | live filings | live 8-K | 8-K items field | 10-Q/10-K | accession + primary doc | PIT 재현 메모 |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| INTC | Y | 200 | 53 | 7 | Y | Y | Y | filingDate 기준 필터 가능. 현재 API 기반 재구성이며 과거 API snapshot은 아님 |
| SBUX | Y | 200 | 42 | 5 | Y | Y | Y | filingDate 기준 필터 가능. 현재 API 기반 재구성이며 과거 API snapshot은 아님 |
| BA | Y | 200 | 25 | 2 | Y | Y | Y | filingDate 기준 필터 가능. 현재 API 기반 재구성이며 과거 API snapshot은 아님 |
| DIS | Y | 200 | 25 | 3 | Y | Y | Y | filingDate 기준 필터 가능. 현재 API 기반 재구성이며 과거 API snapshot은 아님 |
| PYPL | Y | 200 | 57 | 5 | Y | Y | Y | filingDate 기준 필터 가능. 현재 API 기반 재구성이며 과거 API snapshot은 아님 |

관찰:

- ticker -> CIK 매핑은 5/5 성공했다.
- 최근 3개월 filing metadata 수집은 5/5 성공했다.
- 8-K / 10-Q / 10-K 분리는 5/5 가능했다.
- `items` 필드는 표본의 live 8-K에서 확인됐다.
- accession number와 primary document는 5/5 확보 가능했다.
- SEC submissions는 official filing history라 filingDate 기준 PIT 필터링은 가능하다. 다만 "그 날짜 당시 API 화면"의 snapshot 재현은 아니다.

## 4. SEC efts 진단(실험)

`efts.sec.gov/LATEST/search-index`는 공식 문서화 REST API로 전제하지 않았다. 기존 probe의 전 종목 `10000` hits는 endpoint 자체 불안정 단정이 아니라 query/filter construction failure 가능성이 높다고 재판정한다.

CIK 필터 재probe 결과:

| ticker | ticker/date/form only hits | CIK no-zero hits | CIK zero-padded hits | empty keys + CIK zero-padded hits | 진단 |
| --- | ---: | ---: | ---: | ---: | --- |
| INTC | 10000 | 0 | 7 | 7 | zero-padded CIK 필터에서 submissions 8-K count와 일치 |
| SBUX | 10000 | 0 | 5 | 5 | zero-padded CIK 필터에서 submissions 8-K count와 일치 |
| BA | 10000 | 0 | 2 | 2 | zero-padded CIK 필터에서 submissions 8-K count와 일치 |
| DIS | 10000 | 500 error | 3 | 3 | zero-padded CIK 필터는 동작, no-zero는 server error |
| PYPL | 10000 | 0 | 500 error | 500 error | CIK zero-padded query가 server error |

결론:

- 기존 `10000` hits는 likely query/filter construction failure다.
- zero-padded CIK 필터는 4/5에서 useful하게 작동했다.
- PYPL은 CIK 필터에서 server error가 나와 efts를 안정 공식 API로 단정할 수 없다.
- Gate2 1차 catalyst source는 submissions 중심으로 유지하고, efts는 본문/EX-99.1 탐색 보조 후보로만 둔다.

## 5. 8-K item category mapping 재계산

Gate2 점수화는 item occurrence가 아니라 event/filing 단위가 더 적합하다. 그래도 audit 가능성을 위해 occurrence 기준과 filing 기준을 모두 계산했다.

### 5-1. item occurrence 기준

| item | count | positive numerator 포함 여부 | 처리 기준 |
| --- | ---: | --- | --- |
| 1.01 | 0 | Y if present | Material Definitive Agreement. 대형/중요 계약 후보이나 표본 live 창 0건 |
| 2.02 | 5 | Y | Earnings. 펀더멘털 호재 1.5 후보로 규칙 매핑 가능 |
| 2.05 | 1 | N | negative_event candidate. positive numerator 제외 |
| 2.06 | 0 | N | negative_event candidate. positive numerator 제외 |
| 5.02 | 6 | N | 임원 선임/사임/보상. 양방향 가능, neutral/context_required |
| 5.07 | 5 | N | 주주총회 결과. 자동 호재 분자 제외 |
| 7.01 | 3 | N | Regulation FD. 본문/첨부 없이 카테고리 확정 불가 |
| 8.01 | 6 | N | Other Events. 본문/첨부 없이 카테고리 확정 불가 |
| 9.01 | 17 | N | 첨부. 독립 이벤트 아님 |

재계산:

| 기준 | numerator | denominator | mapping률 |
| --- | ---: | ---: | ---: |
| occurrence, 9.01 포함 | 5 | 43 | 11.6% |
| occurrence, 9.01 제외 | 5 | 26 | 19.2% |

기존 27.9% 정정:

- 기존 분자 12는 `2.02(5) + 5.02(6) + 2.05(1)`이었다.
- 보강 기준에서는 `5.02`를 neutral/context_required로 정정하고, `2.05`를 negative_event candidate로 분리한다.
- 따라서 positive item-only numerator는 `2.02(5) + 1.01(0) = 5`다.
- 기존 27.9%는 유지하지 않고 폐기한다.

### 5-2. event/filing 기준

| 기준 | positive filing numerator | filing denominator | mapping률 |
| --- | ---: | ---: | ---: |
| live 8-K filing 기준 | 5 | 22 | 22.7% |
| 9.01-only filing 제외 기준 | 5 | 22 | 22.7% |

진단:

- 표본 live 창에서 9.01-only filing은 없었다.
- filing 기준으로도 positive category를 item code만으로 닫을 수 있는 비율은 22.7%다.
- 주주환원 호재(자사주 매입/배당 인상/주식 분할)는 Gate2 봉인상 0.5점 카테고리지만 item code만으로는 자동 규칙 매핑이 어렵다. 본문/첨부 확인 전에는 `shareholder_return_context_required` 또는 `category_unresolved_from_item_code`로 기록해야 한다.

mapping 불가 사유:

| reason | 설명 |
| --- | --- |
| category_unresolved_from_item_code | 7.01/8.01은 본문/첨부 없이 카테고리 확정 불가 |
| neutral_or_context_required | 5.02/5.07은 자동 positive 분자 제외 |
| shareholder_return_not_item_code_resolvable | 주주환원은 8.01/7.01/9.01 또는 본문에 섞여 나올 수 있어 item-only 불가 |
| attachment_not_independent_event | 9.01은 첨부이며 독립 이벤트 아님 |
| negative_event_separate_track | 2.05/2.06은 positive catalyst가 아니라 negative_event 후보 |

## 6. negative_event status 분리

negative_event는 "없음"과 "수집 실패"를 분리했다.

| enum | 의미 |
| --- | --- |
| negative_absent | 평가 창에서 부정 이벤트 후보 미관찰. 결측이 아니라 Hard Negative 없음 신호일 수 있음 |
| negative_candidate_detected | 후보 관찰. active/material/unresolved는 manual review |
| negative_uncollectable | 수집 경로 자체 실패 |
| negative_unknown_due_to_source_failure | Finviz 429/API 실패 등으로 확인 불가 |

| ticker | negative_event_status | 근거 | source coverage caveat |
| --- | --- | --- | --- |
| INTC | negative_absent | SEC 2.05/2.06 없음, Finviz sample에서 negative candidate 미관찰 | Finviz current page는 live snapshot이며 PIT 아님 |
| SBUX | negative_candidate_detected | SEC 8-K item 2.05, Finviz headline candidates | materiality/manual review 필요 |
| BA | negative_absent | 평가일 이전 SEC negative item code 없음. Finviz FAA-related headline은 2026-05-28 look-ahead라 eval 근거 제외 | negative_absent; lookahead_headline_excluded |
| DIS | negative_absent | 재probe에서 Finviz access 성공, SEC negative item code 미관찰 | headline materiality는 manual |
| PYPL | negative_absent | 재probe에서 Finviz access 성공, SEC negative item code 미관찰 | headline materiality는 manual |

## 7. live_status / pit_status 분리

`overall_status`는 min(live_status, pit_status)가 아니다. 용도별로 분리한다.

- 라이브 운영 가능성 판단: `live_status`
- P9 백테스트/과거 재현 가능성 판단: `pit_status`
- `overall_status`는 어디에서 막히는지 설명하는 요약 label이다.

| ticker | live_status | pit_status | overall_status | overall_status_reason |
| --- | --- | --- | --- | --- |
| INTC | PARTIAL | PARTIAL | PARTIAL | SEC/yfinance live 가능, item-only category 제한, analyst_revision PIT 불가 |
| SBUX | PARTIAL | PARTIAL | PARTIAL | SEC 2.05/2.02와 Finviz/yfinance live 가능, negative materiality와 analyst PIT는 manual/불가 |
| BA | PARTIAL | PARTIAL | PARTIAL | SEC 2.02와 Finviz headline live 가능, negative materiality와 analyst PIT는 manual/불가 |
| DIS | PARTIAL | PARTIAL | PARTIAL | SEC 2.02와 yfinance live 가능, item-only category 제한과 analyst PIT 불가 |
| PYPL | PARTIAL | PARTIAL | PARTIAL | SEC 2.02와 yfinance live 가능, item-only category 제한과 analyst PIT 불가 |

진단:

- analyst_revision_PIT_unavailable이 live_status를 자동으로 낮추지는 않는다.
- 다만 live 기준도 catalyst_event category와 negative_event materiality가 완전 자동화되지 않아 FEASIBLE이 아니라 PARTIAL이다.

종목별 `live_status`는 전체 Gate2 입력을 종목 단위로 본 상태라 5개 표본이 모두 PARTIAL일 수 있다. 다음 설계 판단은 종목별 `overall_status`가 아니라 섹션 12의 모듈별 live/PIT 표를 기준으로 한다. 현재 핵심 신호는 `earnings_trend live = FEASIBLE`, `catalyst_event live = PARTIAL`, `analyst_revision PIT = NOT_FEASIBLE`이며, Recovery Track용 제한 Gate2 설계 여부도 이 모듈별 상태를 기준으로 판단한다.

## 8. Ground truth candidate 표

event_name/date는 source에서 특정 가능한 범위만 썼다. source metadata만으로 특정 못하면 `unspecified_from_source` 또는 `date_unknown_from_source`를 유지했다.

| ticker | candidate_event_name | event_date | source_type | source_identifier | observed_before_eval_date | observed_before_pit_date | gate2_input_connection | capture_status | manual_review_needed | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | unspecified_from_source | 2026-05-15 | SEC | 0000050863-26-000118 / intc-20260513.htm / items=5.07 | Y | N | source_confidence | captured | Y | event name not inferred beyond source metadata |
| INTC | unspecified_from_source | 2026-04-30 | SEC | 0001193125-26-197845 / d143782d8k.htm / items=8.01,9.01 | Y | N | source_confidence | captured | Y | category unresolved from item code |
| SBUX | unspecified_from_source | 2026-05-15 | SEC | 0000829224-26-000088 / sbux-20260513.htm / items=2.05 | Y | N | negative_event | captured | Y | negative candidate; active/material/unresolved manual |
| SBUX | unspecified_from_source | 2026-04-28 | SEC | 0000829224-26-000078 / sbux-20260428.htm / items=2.02,9.01 | Y | N | catalyst_event | captured | N | item 2.02 category mapping possible |
| BA | unspecified_from_source | 2026-04-22 | SEC | 0001628280-26-026391 / ba-20260422.htm / items=2.02,9.01 | Y | N | catalyst_event | captured | N | item 2.02 category mapping possible |
| BA | unspecified_from_source | 2026-05-28 | Finviz | Boeing Shares Rise As FAA Clears Path Toward 47 Max Jets Monthly / finance.yahoo.com / 2026-05-28 | N | N | negative_event | not_captured | Y | look-ahead relative to 2026-05-27; not usable for eval |
| DIS | unspecified_from_source | 2026-05-06 | SEC | 0001744489-26-000036 / dis-20260506.htm / items=2.02,9.01 | Y | N | catalyst_event | captured | N | item 2.02 category mapping possible |
| DIS | unspecified_from_source | 2026-03-03 | SEC | 0001193125-26-088356 / d116769d8k.htm / items=8.01,9.01 | Y | N | source_confidence | captured | Y | category unresolved from item code |
| PYPL | unspecified_from_source | 2026-05-05 | SEC | 0001633917-26-000065 / pypl-20260505.htm / items=2.02,9.01 | Y | N | catalyst_event | captured | N | item 2.02 category mapping possible |
| PYPL | unspecified_from_source | 2026-05-27 | Finviz | PayPal Links With WeChat Pay / finance.yahoo.com / 2026-05-27 | Y | N | catalyst_event | captured | Y | headline candidate only; category/materiality manual |

## 9. Finviz lookback days 정량화

Probe date는 2026-05-28로 두었다. 평가일은 2026-05-27이므로 2026-05-28 headline은 look-ahead로 계산했다.

| ticker | quote_page_status | news_table_status | oldest_headline_date | newest_headline_date | lookback_days_from_probe_date | lookback_days_until_eval_date | publisher domain available | rate_limit_status | lookahead_headline_count | usable_headline_count_before_eval_date |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | ---: | ---: |
| INTC | 200 | Y | 2026-05-15 | 2026-05-28 | 13 | 12 | Y | OK | 5 | 95 |
| SBUX | 200 | Y | 2026-04-28 | 2026-05-26 | 30 | 29 | Y | OK | 0 | 100 |
| BA | 200 | Y | 2026-05-11 | 2026-05-28 | 17 | 16 | Y | OK | 3 | 97 |
| DIS | 200 | Y | 2026-04-29 | 2026-05-28 | 29 | 28 | Y | OK | 1 | 99 |
| PYPL | 200 | Y | 2026-03-31 | 2026-05-28 | 58 | 57 | Y | OK | 2 | 98 |

진단:

- DIS/PYPL은 1차 리포트에서 429가 있었으나 이번 보강 재시도 1회에서는 200으로 회복됐다.
- Finviz는 live 화면 lookback 측정에는 쓸 수 있다.
- Finviz PIT 복원 가능으로 단정하지 않는다. 과거 특정 평가일 화면 재현은 불가 가능성이 높다.

## 10. yfinance 증거 표

`get_earnings_dates(limit=5/12/25)`를 모두 호출했지만 5개 표본 모두 25 rows가 반환됐다. 따라서 "실제 전체 available rows"가 아니라 yfinance endpoint가 현재 25 rows bundle을 반환한 것으로 기록한다.

| ticker | earnings_dates row_count | row_count 해석 | latest earnings sample row | calendar fields observed | recommendations fields observed | upgrades_downgrades sample | eps_revisions fields observed | eps_revisions current snapshot only | PIT reconstruction possible | evidence_note |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | 25 | limit 5/12/25 모두 25 반환 | 2026-04-23, EPS estimate 0.01, reported 0.29, surprise 2108.68 | Dividend Date, Earnings Date, Earnings Average, Revenue Average | period, strongBuy, buy, hold, sell, strongSell | 2026-05-18 Citigroup Buy->Buy Raises 130/95 | upLast7days, upLast30days, downLast30days, downLast7Days, currency | Y | N | live snapshot usable, PIT analyst revision unavailable |
| SBUX | 25 | limit 5/12/25 모두 25 반환 | 2026-04-28, EPS estimate 0.44, reported 0.50, surprise 14.51 | Dividend Date, Earnings Date, Earnings Average, Revenue Average | period, strongBuy, buy, hold, sell, strongSell | 2026-05-14 TD Cowen Hold->Buy Raises 120/106 | upLast7days, upLast30days, downLast30days, downLast7Days, currency | Y | N | live snapshot usable, PIT analyst revision unavailable |
| BA | 25 | limit 5/12/25 모두 25 반환 | 2026-04-22, EPS estimate -0.67, reported -0.20, surprise 70.26 | Dividend Date, Earnings Date, Earnings Average, Revenue Average | period, strongBuy, buy, hold, sell, strongSell | 2026-05-18 Citigroup Buy->Buy Raises 260/256 | upLast7days, upLast30days, downLast30days, downLast7Days, currency | Y | N | live snapshot usable, PIT analyst revision unavailable |
| DIS | 25 | limit 5/12/25 모두 25 반환 | 2026-05-06, EPS estimate 1.50, reported 1.57, surprise 4.98 | Dividend Date, Earnings Date, Earnings Average, Revenue Average | period, strongBuy, buy, hold, sell, strongSell | 2026-05-08 Citigroup Buy->Buy Raises 145/135 | upLast7days, upLast30days, downLast30days, downLast7Days, currency | Y | N | live snapshot usable, PIT analyst revision unavailable |
| PYPL | 25 | limit 5/12/25 모두 25 반환 | 2026-05-05, EPS estimate 1.27, reported 1.34, surprise 5.59 | Dividend Date, Earnings Date, Earnings Average, Revenue Average | period, strongBuy, buy, hold, sell, strongSell | 2026-05-12 Truist Sell->Sell Lowers 44/45 | upLast7days, upLast30days, downLast30days, downLast7Days, currency | Y | N | live snapshot usable, PIT analyst revision unavailable |

EPS estimate가 0에 가까운 경우 surprise%는 과도하게 커지거나 반올림 영향이 커질 수 있다. 예를 들어 INTC sample row는 EPS estimate 0.01, reported EPS 0.29, surprise 2108.68로 관찰되어 surprise% 단독으로 beat 강도를 판단하면 왜곡될 수 있다. 향후 Recovery용 Gate2 설계에서는 surprise% 단독 사용을 피하고 actual vs estimate 방향성과 absolute EPS delta를 함께 확인해야 한다. 이번 리포트에서는 설계 변경이 아니라 yfinance 데이터 해석 caveat로만 기록한다.

## 11. 종목별 수집 가능성 표

diagnosis_status 기준:

- PASS = Gate2 필수 입력 전부 수집 가능
- PARTIAL = 일부 가능
- FAIL = catalyst 또는 negative 수집 불가

| ticker | SEC available Y/N | 8-K items 필드 Y/N | Finviz headlines Y/N | Finviz publisher 식별 Y/N | yfinance earnings Y/N | yfinance analyst(현재) Y/N | yfinance analyst(PIT) Y/N | negative event source Y/N | diagnosis_status | missing_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | Y | Y | Y | Y | Y | Y | N | N | PARTIAL | negative_absent; analyst_revision_PIT_unavailable; category_mapping_partial |
| SBUX | Y | Y | Y | Y | Y | Y | N | Y | PARTIAL | analyst_revision_PIT_unavailable; negative_materiality_manual |
| BA | Y | Y | Y | Y | Y | Y | N | N | PARTIAL | negative_absent; lookahead_headline_excluded; analyst_revision_PIT_unavailable |
| DIS | Y | Y | Y | Y | Y | Y | N | N | PARTIAL | negative_absent; analyst_revision_PIT_unavailable; category_mapping_partial |
| PYPL | Y | Y | Y | Y | Y | Y | N | N | PARTIAL | negative_absent; analyst_revision_PIT_unavailable; category_mapping_partial |

## 12. Gate2 하위 모듈별 자동화 가능성

| module | live | PIT | 메모 |
| --- | --- | --- | --- |
| catalyst_event | PARTIAL | PARTIAL | SEC 8-K metadata는 가능. positive item-only category mapping은 9.01 포함 11.6%, filing 기준 22.7% |
| earnings_trend | FEASIBLE | PARTIAL | yfinance reported EPS/surprise 가능. PIT forward estimate snapshot은 불가 |
| analyst_revision | PARTIAL | NOT_FEASIBLE | current recommendations/upgrades는 가능. PIT consensus/revision snapshot이 단일 병목 |
| negative_event | PARTIAL | PARTIAL | SEC item 2.05/2.06와 일부 headline은 가능. active/material/unresolved 판정은 manual |
| source_confidence | PARTIAL | PARTIAL | SEC official source는 강함. Finviz publisher domain은 live에서 가능하나 PIT 한계 |
| llm_event_classifier | FEASIBLE_LIMITED | FEASIBLE_LIMITED | headline 감성 enum만 가능: positive/negative/neutral/unclear. category/투자판단 금지 |

## 13. LLM 봉인 진단

- LLM 허용 범위: headline 감성 enum `positive / negative / neutral / unclear`
- `unclear` 자동 무시 필요
- LLM 단독 통과 근거 불가
- 최소 2개 독립 출처 또는 1개 공식 출처 필요
- LLM이 카테고리, 종목 판단, 추천 문구를 생성하면 봉인 위반

진단:

- positive item-only mapping률이 9.01 포함 11.6%, filing 기준 22.7%라 LLM이 카테고리를 보정하려는 압력이 생긴다.
- 따라서 Gate2 구현을 진행한다면 규칙 매핑 가능한 SEC item subset부터 제한 적용해야 한다.

## 14. 무료 데이터 한계 / 수동 reference 항목

- analyst_revision PIT는 무료 자동 수집으로 재현 불가에 가깝다.
- Finviz는 이번 재probe에서는 5/5 접근됐지만 무료 화면 기반이고 과거 화면 PIT 복원이 어렵다.
- SEC는 공식 filing history라 가장 안정적이지만, 8-K item code만으로 category가 충분히 닫히지 않는다.
- negative_event의 active/material/unresolved 상태는 manual review가 필요하다.
- Reuters/Bloomberg/WSJ는 Tier 2 manual reference로 남긴다.

## 15. rate limit / scale caveat

표본 5종목 probe 결과를 universe 656종목에 바로 외삽할 수 없다.

- SEC는 10 req/s User-Agent 준수가 필요하다.
- yfinance는 schema/rate limit/blacklist caveat가 있다.
- Finviz는 무료 quote page 기반이므로 캐싱/재시도/간격 제어가 없으면 429 가능성이 있다.
- 656종목 스케일에서는 캐싱, 재시도, 소스별 쿼터, 실패 격리 없이는 안정 운영 진단 불가다.

## 16. 수정 파일 목록 / git diff 요약 / git 상태

수정 파일:

- reports/gate2_data_source_diagnosis_v0_1.md

git diff 요약:

```text
git diff --stat
(tracked diff 없음; 신규 report는 untracked)
```

최종 `git status -sb`:

```text
## main...origin/main
?? backups/
?? reports/backtest_it_2026q1_data_v0_1.csv
?? reports/backtest_it_2026q1_summary_v0_1.md
?? reports/gate2_data_source_diagnosis_v0_1.md
?? reports/track_c_session_001_ai_assisted_review.xlsx
```

## 17. 최종 결론 13문항

### 1. item-only mapping률 9.01 포함/제외 각 몇 %?

- 9.01 포함: 5 / 43 = 11.6%
- 9.01 제외: 5 / 26 = 19.2%

### 2. event/filing 기준 mapping률 몇 %?

- live 8-K filing 기준: 5 / 22 = 22.7%
- 9.01-only filing 제외 기준도 표본에서는 5 / 22 = 22.7%

### 3. 기존 27.9% 유지/수정?

수정한다. 기존 27.9%는 `2.02(5)+5.02(6)+2.05(1)`를 분자로 둔 값이었다. 보강 기준에서 `5.02`는 neutral/context_required, `2.05`는 negative_event candidate라 positive numerator에서 제외한다.

### 4. 1.01이 표본 live 창에서 몇 건?

0건.

### 5. 5.02가 neutral/context_required로 정정됐는가?

YES. 5.02는 임원 선임/사임/보상 등 양방향 가능성이 있어 자동 호재 분자에 넣지 않는다.

### 6. negative_event absent/uncollectable 분리됐는가?

YES. `negative_absent`, `negative_candidate_detected`, `negative_uncollectable`, `negative_unknown_due_to_source_failure`로 분리했다.

### 7. live 기준 Gate2 수집 가능성은?

PARTIAL. SEC/yfinance/Finviz live 데이터는 수집 가능성이 있지만, category mapping과 negative materiality가 완전 자동화되지 않는다.

### 8. PIT 기준 Gate2 수집 가능성은?

PARTIAL. SEC filingDate 기준 재구성은 가능하지만 yfinance/Finviz analyst_revision PIT와 Finviz 과거 화면 재현이 막힌다.

### 9. analyst_revision PIT 병목으로 Continuation C-E는 여전히 막히는가?

YES. yfinance/Finviz 무료 소스로 2026-01-15 당시 analyst revision snapshot을 안정 재현하지 못한다.

### 10. Recovery Track 중심부터 시작 결론은 유지되는가?

YES. Recovery Track 중심 Gate2부터 SEC official filings + yfinance earnings_trend + manual negative_event review 조합으로 제한 시작하는 결론을 유지한다.

### 11. Finviz lookback days가 ticker별 숫자로 나왔는가?

YES. INTC 12일, SBUX 29일, BA 16일, DIS 28일, PYPL 57일로 평가일 기준 usable lookback을 기록했다.

### 12. yfinance 25 rows는 실제인가 limit인가?

현재 probe에서는 `limit=5/12/25` 모두 25 rows가 반환됐다. 따라서 "전체 available rows"라고 쓰지 않고 yfinance endpoint가 현재 25-row bundle을 반환한 것으로 기록한다.

### 13. efts 10000 hits는 쿼리 실패인가 endpoint 불안정인가?

기존 10000 hits는 likely query/filter construction failure다. zero-padded CIK 필터 재probe는 4/5에서 submissions 8-K count와 맞는 hits로 줄었다. 다만 PYPL에서 server error가 있어 efts를 안정 공식 API로 단정하지 않고 보조 probe로만 둔다.

## 18. 최종 판정

Gate2 전체 구현 가능성: PARTIAL.

Continuation C-E까지 무료 소스만으로 닫기는 어렵다. analyst_revision PIT가 단일 병목이며, category mapping과 negative materiality도 완전 자동화되지 않는다. Recovery Track 중심 Gate2부터 제한적으로 진단/설계를 이어가는 것이 현실적이다.
