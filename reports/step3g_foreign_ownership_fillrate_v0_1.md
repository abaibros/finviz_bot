# Step 3-G foreign_ownership_pct Fill-Rate Diagnosis v0.1

## 0. Purpose
- This report diagnoses the availability and distribution of foreign_ownership_pct.
- It does not modify universe_master.csv.
- It does not modify audit CSV.
- It does not create v0.3 hard filter rules.
- It does not make buy/sell/recommendation judgments.

## 1. Input File Check
- universe_master.csv existence: True
- audit csv existence: True
- step3f sample csv existence: True
- universe rows: 656
- audit rows: 656
- step3f sample rows: 39
- ticker duplicates: universe=none; audit=none
- merge status: OK

## 2. Column Availability
- foreign_ownership_pct in universe_master.csv: YES
- foreign_ownership_pct in audit csv: NO
- source column availability: universe=YES; audit=YES
- market column availability: universe=YES; audit=YES
- role column availability: audit universe_role=YES
- risk_level column availability: audit quality_risk_level=YES

## 3. Overall Fill Rate
- total rows: 656
- filled foreign_ownership_pct rows: 87
- empty foreign_ownership_pct rows: 569
- fill rate: 13.3%
- value type issues: 0
- invalid values: none

## 4. Fill Rate by Market
| market | total_rows | filled_rows | empty_rows | fill_rate |
| --- | ---: | ---: | ---: | ---: |
| KR | 102 | 87 | 15 | 85.3% |
| US | 554 | 0 | 554 | 0.0% |

## 5. Fill Rate by Role
| role | total_rows | filled_rows | empty_rows | fill_rate |
| --- | ---: | ---: | ---: | ---: |
| CORE | 255 | 9 | 246 | 3.5% |
| DISCOVERY_ONLY | 16 | 10 | 6 | 62.5% |
| EXCLUDE_CANDIDATE | 1 | 0 | 1 | 0.0% |
| EXTENDED | 343 | 60 | 283 | 17.5% |
| HIGH_RISK_REVIEW | 41 | 8 | 33 | 19.5% |

## 6. Fill Rate by Risk Level
| risk_level | total_rows | filled_rows | empty_rows | fill_rate |
| --- | ---: | ---: | ---: | ---: |
| HIGH | 57 | 18 | 39 | 31.6% |
| LOW | 255 | 9 | 246 | 3.5% |
| MEDIUM | 343 | 60 | 283 | 17.5% |
| VERY_HIGH | 1 | 0 | 1 | 0.0% |

## 7. Distribution of foreign_ownership_pct Values
- count > 0: 87
- count >= 10: 81
- count >= 20: 54
- count >= 30: 36
- count >= 50: 8
- count >= 70: 3
- min: 5.0
- max: 75.0
- median: 25.0
- mean: 27.4
- top 30 rows by foreign_ownership_pct:
| ticker | name | market | role | risk_level | market_cap_usd_b | foreign_ownership_pct |
| --- | --- | --- | --- | --- | ---: | ---: |
| 105560.KS | KB금융 | KR | EXTENDED | MEDIUM | 41.9 | 75.0 |
| 055550.KS | 신한지주 | KR | EXTENDED | MEDIUM | 32.5 | 70.0 |
| 086790.KS | 하나금융지주 | KR | EXTENDED | MEDIUM | 23.5 | 70.0 |
| 010950.KS | S-Oil | KR | EXTENDED | MEDIUM | 8.9 | 63.0 |
| 000660.KS | SK하이닉스 | KR | CORE | LOW | 1044.6 | 55.0 |
| 000810.KS | 삼성화재 | KR | EXTENDED | MEDIUM | 18.5 | 55.0 |
| 005930.KS | 삼성전자 | KR | CORE | LOW | 1248.6 | 55.0 |
| 005935.KS | 삼성전자우 | KR | CORE | LOW | 107.3 | 55.0 |
| 030200.KS | KT | KR | EXTENDED | MEDIUM | 9.8 | 49.0 |
| 017670.KS | SK텔레콤 | KR | EXTENDED | MEDIUM | 15.7 | 45.0 |
| 033780.KS | KT&G | KR | EXTENDED | MEDIUM | 13.5 | 45.0 |
| 035420.KS | NAVER | KR | EXTENDED | MEDIUM | 22.4 | 45.0 |
| 316140.KS | 우리금융지주 | KR | EXTENDED | MEDIUM | 16.2 | 45.0 |
| 003550.KS | LG | KR | EXTENDED | MEDIUM | 13.5 | 40.0 |
| 005490.KS | POSCO홀딩스 | KR | EXTENDED | MEDIUM | 25.0 | 40.0 |
| 006400.KS | 삼성SDI | KR | EXTENDED | MEDIUM | 37.0 | 40.0 |
| 012450.KS | 한화에어로스페이스 | KR | EXTENDED | MEDIUM | 46.1 | 40.0 |
| 241560.KS | 두산밥캣 | KR | DISCOVERY_ONLY | HIGH | 4.7 | 40.0 |
| 402340.KS | SK스퀘어 | KR | CORE | LOW | 111.3 | 40.0 |
| 000270.KS | 기아 | KR | EXTENDED | MEDIUM | 46.6 | 38.0 |
| 051910.KS | LG화학 | KR | EXTENDED | MEDIUM | 17.7 | 38.0 |
| 005830.KS | DB손해보험 | KR | EXTENDED | MEDIUM | 7.0 | 35.0 |
| 012330.KS | 현대모비스 | KR | EXTENDED | MEDIUM | 43.0 | 35.0 |
| 042660.KS | 한화오션 | KR | EXTENDED | MEDIUM | 29.5 | 35.0 |
| 005380.KS | 현대차 | KR | CORE | LOW | 100.8 | 33.0 |
| 009540.KS | HD한국조선해양 | KR | EXTENDED | MEDIUM | 22.5 | 32.0 |
| 009150.KS | 삼성전기 | KR | CORE | LOW | 83.9 | 30.0 |
| 010140.KS | 삼성중공업 | KR | EXTENDED | MEDIUM | 19.1 | 30.0 |
| 028260.KS | 삼성물산 | KR | EXTENDED | MEDIUM | 47.6 | 30.0 |
| 032830.KS | 삼성생명 | KR | EXTENDED | MEDIUM | 49.7 | 30.0 |

## 8. Korean Stock Coverage
- KR total rows: 102
- KR filled rows: 87
- KR empty rows: 15
- KR fill rate: 85.3%
- KR filled ticker list with values: 005930.KS (삼성전자, 55), 000660.KS (SK하이닉스, 55), 373220.KS (LG에너지솔루션, 5), 207940.KS (삼성바이오로직스, 12), 402340.KS (SK스퀘어, 40), 005935.KS (삼성전자우, 55), 009150.KS (삼성전기, 30), 005380.KS (현대차, 33), 000270.KS (기아, 38), 068270.KS (셀트리온, 22), 034020.KS (두산에너빌리티, 18), 329180.KS (HD현대중공업, 30), 012450.KS (한화에어로스페이스, 40), 042660.KS (한화오션, 35), 028260.KS (삼성물산, 30), 006400.KS (삼성SDI, 40), 005490.KS (POSCO홀딩스, 40), 035420.KS (NAVER, 45), 267260.KS (HD현대일렉트릭, 25), 105560.KS (KB금융, 75), 298040.KS (효성중공업, 15), 010120.KS (LS ELECTRIC, 18), 055550.KS (신한지주, 70), 034730.KS (SK, 25), 012330.KS (현대모비스, 35), 010130.KS (고려아연, 18), 051910.KS (LG화학, 38), 032830.KS (삼성생명, 30), 009540.KS (HD한국조선해양, 32), 000810.KS (삼성화재, 55), 079550.KS (LIG넥스원, 20), 066570.KS (LG전자, 30), 011200.KS (HMM, 5), 011070.KS (LG이노텍, 25), 042700.KS (한미반도체, 15), 272210.KS (한화시스템, 15), 033780.KS (KT&G, 45), 086790.KS (하나금융지주, 70), 000150.KS (두산, 18), 259960.KS (크래프톤, 30), 064350.KS (현대로템, 22), 267250.KS (HD현대, 18), 010140.KS (삼성중공업, 30), 352820.KS (하이브, 18), 015760.KS (한국전력, 15), 316140.KS (우리금융지주, 45), 003670.KS (포스코퓨처엠, 12), 096770.KS (SK이노베이션, 28), 138040.KS (메리츠금융지주, 15), 006260.KS (LS, 20), 086280.KS (현대글로비스, 30), 307950.KS (현대오토에버, 12), 006800.KS (미래에셋증권, 25), 003550.KS (LG, 40), 003230.KS (삼양식품, 18), 010950.KS (S-Oil, 63), 090430.KS (아모레퍼시픽, 25), 097950.KS (CJ제일제당, 15), 017670.KS (SK텔레콤, 45), 030200.KS (KT, 49), 241560.KS (두산밥캣, 40), 000720.KS (현대건설, 20), 047810.KS (한국항공우주, 22), 018260.KS (삼성SDS, 14), 009830.KS (한화솔루션, 25), 336260.KS (두산퓨얼셀, 10), 180640.KS (한진칼, 18), 024110.KS (기업은행, 25), 035720.KS (카카오, 28), 088980.KS (맥쿼리인프라, 30), 000100.KS (유한양행, 18), 004020.KS (현대제철, 18), 032640.KS (LG유플러스, 25), 139480.KS (이마트, 12), 251270.KS (넷마블, 18), 004990.KS (롯데지주, 10), 005830.KS (DB손해보험, 35), 001440.KS (대한전선, 8), 018880.KS (한온시스템, 25), 078930.KS (GS, 20), 128940.KS (한미약품, 15), 247540.KQ (에코프로비엠, 10), 086520.KQ (에코프로, 8), 196170.KQ (알테오젠, 12), 277810.KQ (레인보우로보틱스, 5), 058470.KQ (리노공업, 30), 028300.KQ (HLB, 5)
- KR empty ticker list: 009450.KS (경동나비엔), 036930.KQ (주성엔지니어링), 950160.KQ (코오롱티슈진), 000250.KQ (삼천당제약), 039030.KQ (이오테크닉스), 298380.KQ (에이비엘바이오), 087010.KQ (펩트론), 240810.KQ (원익IPS), 440110.KQ (파두), 141080.KQ (리가켐바이오), 222800.KQ (심텍), 108490.KQ (로보티즈), 310210.KQ (보로노이), 095340.KQ (ISC), 178320.KQ (서진시스템)
- KR rows with market_cap_usd_b < 5 and foreign_ownership_pct filled:
| ticker | name | market | market_cap_usd_b | foreign_ownership_pct |
| --- | --- | --- | ---: | ---: |
| 097950.KS | CJ제일제당 | KR | 2.3 | 15 |
| 241560.KS | 두산밥캣 | KR | 4.7 | 40 |
| 336260.KS | 두산퓨얼셀 | KR | 4.7 | 10 |
| 088980.KS | 맥쿼리인프라 | KR | 3.8 | 30 |
| 000100.KS | 유한양행 | KR | 4.9 | 18 |
| 004020.KS | 현대제철 | KR | 4.0 | 18 |
| 032640.KS | LG유플러스 | KR | 4.8 | 25 |
| 139480.KS | 이마트 | KR | 1.8 | 12 |
| 251270.KS | 넷마블 | KR | 2.5 | 18 |
| 004990.KS | 롯데지주 | KR | 1.9 | 10 |
| 018880.KS | 한온시스템 | KR | 3.8 | 25 |
| 128940.KS | 한미약품 | KR | 4.3 | 15 |
- KR rows with market_cap_usd_b < 5 and foreign_ownership_pct empty:
009450.KS (경동나비엔), 039030.KQ (이오테크닉스), 298380.KQ (에이비엘바이오), 087010.KQ (펩트론), 240810.KQ (원익IPS), 440110.KQ (파두), 141080.KQ (리가켐바이오), 222800.KQ (심텍), 108490.KQ (로보티즈), 310210.KQ (보로노이), 095340.KQ (ISC), 178320.KQ (서진시스템)
- KR rows with market_cap_usd_b < 10 and foreign_ownership_pct filled:
| ticker | name | market | market_cap_usd_b | foreign_ownership_pct |
| --- | --- | --- | ---: | ---: |
| 259960.KS | 크래프톤 | KR | 8.6 | 30 |
| 352820.KS | 하이브 | KR | 7.3 | 18 |
| 003230.KS | 삼양식품 | KR | 7.0 | 18 |
| 010950.KS | S-Oil | KR | 8.9 | 63 |
| 090430.KS | 아모레퍼시픽 | KR | 5.0 | 25 |
| 097950.KS | CJ제일제당 | KR | 2.3 | 15 |
| 030200.KS | KT | KR | 9.8 | 49 |
| 241560.KS | 두산밥캣 | KR | 4.7 | 40 |
| 009830.KS | 한화솔루션 | KR | 5.5 | 25 |
| 336260.KS | 두산퓨얼셀 | KR | 4.7 | 10 |
| 180640.KS | 한진칼 | KR | 5.5 | 18 |
| 088980.KS | 맥쿼리인프라 | KR | 3.8 | 30 |
| 000100.KS | 유한양행 | KR | 4.9 | 18 |
| 004020.KS | 현대제철 | KR | 4.0 | 18 |
| 032640.KS | LG유플러스 | KR | 4.8 | 25 |
| 139480.KS | 이마트 | KR | 1.8 | 12 |
| 251270.KS | 넷마블 | KR | 2.5 | 18 |
| 004990.KS | 롯데지주 | KR | 1.9 | 10 |
| 005830.KS | DB손해보험 | KR | 7.0 | 35 |
| 001440.KS | 대한전선 | KR | 7.5 | 8 |
| 018880.KS | 한온시스템 | KR | 3.8 | 25 |
| 078930.KS | GS | KR | 5.1 | 20 |
| 128940.KS | 한미약품 | KR | 4.3 | 15 |
| 058470.KQ | 리노공업 | KR | 6.0 | 30 |
| 028300.KQ | HLB | KR | 5.0 | 5 |
- KR rows with market_cap_usd_b < 10 and foreign_ownership_pct empty:
009450.KS (경동나비엔), 036930.KQ (주성엔지니어링), 950160.KQ (코오롱티슈진), 000250.KQ (삼천당제약), 039030.KQ (이오테크닉스), 298380.KQ (에이비엘바이오), 087010.KQ (펩트론), 240810.KQ (원익IPS), 440110.KQ (파두), 141080.KQ (리가켐바이오), 222800.KQ (심텍), 108490.KQ (로보티즈), 310210.KQ (보로노이), 095340.KQ (ISC), 178320.KQ (서진시스템)

## 9. US / ADR Coverage
- US total rows: 554
- US filled rows: 0
- US empty rows: 554
- US fill rate: 0.0%
- US ADR rows with foreign_ownership_pct values: none
- ADR-related filled rows below are KR rows with ADR_AVAILABLE source markers, not US ADR listings.
- ADR-related rows with foreign_ownership_pct values if any: 005490.KS (POSCO홀딩스, 40), 015760.KS (한국전력, 15), 316140.KS (우리금융지주, 45), 017670.KS (SK텔레콤, 45), 030200.KS (KT, 49)
- ADR-related rows with empty foreign_ownership_pct: ASML (ASML Holding N.V.), ARM (Arm Holdings plc), PDD (PDD Holdings Inc.), SHOP (Shopify Inc.), MELI (MercadoLibre Inc.), FER (Ferrovial N.V.), CCEP (Coca-Cola Europacific Partners PLC), TRI (Thomson Reuters Corporation), TEAM (Atlassian Corporation), TSM (Taiwan Semiconductor Manufacturing Company Limited), NVO (Novo Nordisk A/S), NVS (Novartis AG), AZN (AstraZeneca PLC), SAP (SAP SE), BABA (Alibaba Group Holding Limited), TM (Toyota Motor Corporation), SHEL (Shell plc), TTE (TotalEnergies SE), HSBC (HSBC Holdings plc), MUFG (Mitsubishi UFJ Financial Group Inc.), BHP (BHP Group Limited), RIO (Rio Tinto Group), UL (Unilever PLC), BTI (British American Tobacco p.l.c.), BUD (Anheuser-Busch InBev SA/NV), DEO (Diageo plc), SONY (Sony Group Corporation), HMC (Honda Motor Co. Ltd.), BP (BP p.l.c.), E (Eni S.p.A.), RELX (RELX PLC), ASR (Grupo Aeroportuario del Sureste), BSAC (Banco Santander-Chile), ABEV (Ambev S.A.), VALE (Vale S.A.), ITUB (Itaú Unibanco Holding S.A.), BBD (Banco Bradesco S.A.), PBR (Petróleo Brasileiro S.A.), CPNG (Coupang Inc.), PKX (POSCO Holdings Inc. ADR), KB (KB Financial Group Inc. ADR), LPL (LG Display Co. Ltd. ADR), SHG (Shinhan Financial Group Co. Ltd. ADR), KEP (Korea Electric Power Corp. ADR), SKM (SK Telecom Co. Ltd. ADR), WF (Woori Financial Group Inc. ADR)
- ASR foreign_ownership_pct:
  - empty
- ASR: empty
- CPNG: empty
- PKX: empty
- KB: empty
- KEP: empty
- SKM: empty
- SHG: empty
- LPL: empty

## 10. Step 3-F Key Ticker Check
| ticker | name | market | role | risk_level | market_cap_usd_b | foreign_ownership_pct | source |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| 032640.KS | LG유플러스 | KR | DISCOVERY_ONLY | HIGH | 4.8 | 25 | KOSPI_TELECOM; JUDAL_2026_05_26 |
| 088980.KS | 맥쿼리인프라 | KR | DISCOVERY_ONLY | HIGH | 3.8 | 30 | KOSPI_INFRA_REIT; JUDAL_2026_05_26 |
| 030200.KS | KT | KR | EXTENDED | MEDIUM | 9.8 | 49 | KOSPI_TOP_ADR_AVAILABLE_FOREIGN_HIGH; JUDAL_2026_05_26 |
| 017670.KS | SK텔레콤 | KR | EXTENDED | MEDIUM | 15.7 | 45 | KOSPI_TOP_ADR_AVAILABLE_FOREIGN_HIGH; JUDAL_2026_05_26 |
| 015760.KS | 한국전력 | KR | EXTENDED | MEDIUM | 18.5 | 15 | KOSPI_TOP_ADR_AVAILABLE; JUDAL_2026_05_26 |
| 033780.KS | KT&G | KR | EXTENDED | MEDIUM | 13.5 | 45 | KOSPI_TOP_FOREIGN_HIGH; JUDAL_2026_05_26 |
| 105560.KS | KB금융 | KR | EXTENDED | MEDIUM | 41.9 | 75 | KOSPI_TOP_FOREIGN_HIGH; JUDAL_2026_05_26; holding_classification_v0_2 |
| 032830.KS | 삼성생명 | KR | EXTENDED | MEDIUM | 49.7 | 30 | KOSPI_TOP; JUDAL_2026_05_26 |
| ASR | Grupo Aeroportuario del Sureste | US | EXTENDED | MEDIUM | 8.0 |  | ADR |

## 11. Diagnostic Interpretation
- Is foreign_ownership_pct broadly populated or sparse? foreign_ownership_pct is sparse across the full universe.
- Is it mostly KR-only? The populated values are mostly KR-only, while US/ADR rows are mostly empty.
- Is it missing for US/ADR rows? US filled rows=0; ADR filled rows=5.
- Can it currently support a global rule? It cannot currently support a global rule without additional coverage checks.
- Can it support a KR-only diagnostic tag? It can support a KR-only diagnostic tag or review note if GPT/Claude accepts the coverage limits.
- What data gaps remain? trading_liquidity, dividend_history, and comparable foreign ownership or listing-risk fields for US/ADR rows remain unavailable in these files.

## 12. Cause / Risk Notes
- risk of using foreign_ownership_pct if KR-only: it may encode market-specific coverage instead of a comparable global signal.
- risk of comparing KR foreign ownership to US ADR rows: US ADR rows mostly lack the same field, so direct comparison may mix availability effects with classification effects.
- risk of arbitrary thresholds: 10/20/30/50/70 buckets are distribution checks only and are not validated cutoffs.
- need for trading_liquidity/dividend_history: Step 3-F asymmetry cases cannot be separated from liquidity and income-profile questions using this column alone.

## 13. Recommended Next Step
- GPT/Claude review required.
- v0.3 hard filter design still prohibited.
- If fill rate is high enough, next step may be threshold simulation.
- If fill rate is sparse, next step should be data acquisition or use as annotate-only diagnostic.
- Do not modify universe_master.csv.
- Do not modify audit CSV.
- Do not modify operating code.

## 14. Git Status
- git status -sb:
```text
## main...origin/main
?? backups/
?? reports/step3g_foreign_ownership_fillrate_v0_1.md
```
- git status --short:
```text
?? backups/
?? reports/step3g_foreign_ownership_fillrate_v0_1.md
```
- git add status: NO
- commit status: NO
- push status: NO
