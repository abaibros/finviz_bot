# Step 3-C Metadata Diagnosis v0.1

## 0. Purpose
- This report diagnoses suspected market_cap_usd_b metadata issues for SNDK and INTC.
- It does not change universe_master.csv.
- It does not change audit CSV.
- It does not change step3 sample CSV.
- It does not create v0.3 hard filter rules.
- SNDK and INTC are NOT confirmed as metadata errors. They remain verification targets.

## 1. Input File Check
- universe_master.csv existence: True
- audit csv existence: True
- step3 sample csv existence: True
- universe rows: 656
- audit rows: 656
- sample rows: 52
- ticker duplicates: universe=[]; audit=[]; sample=[]
- merge status: True

## 2. SNDK Row Comparison
- universe_master row:
```json
{
  "ticker": "SNDK",
  "name": "Sandisk Corporation",
  "market": "US",
  "sector": "Information Technology",
  "sub_industry": "Technology Hardware, Storage & Peripherals",
  "market_cap_local": "197.0",
  "market_cap_local_unit": "USD_B",
  "market_cap_usd_b": "197.0",
  "fx_rate_used": "",
  "exchange": "NASDAQ",
  "adr_flag": "N",
  "foreign_ownership_pct": "",
  "company_type": "",
  "turnaround_flag": "N",
  "updated_at": "2026-05-26",
  "source": "SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2"
}
```
- audit row:
```json
{
  "ticker": "SNDK",
  "name": "Sandisk Corporation",
  "market": "US",
  "sector": "Information Technology",
  "sub_industry": "Technology Hardware, Storage & Peripherals",
  "market_cap_usd_b": "197.0",
  "source": "SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2",
  "company_type": "",
  "turnaround_flag": "N",
  "universe_role": "CORE",
  "quality_risk_level": "LOW",
  "risk_flags": "RECENT_INDEX_INCLUSION",
  "review_reason": "RECENT_INDEX_INCLUSION; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker",
  "recommended_next_action": "KEEP_CORE"
}
```
- sample row:
```json
{
  "sample_id": "S3V01-007",
  "sample_reason_code": "INFORMATION_TECHNOLOGY",
  "sample_reason_note": "IT sector coverage; sector=Information Technology",
  "ticker": "SNDK",
  "name": "Sandisk Corporation",
  "market": "US",
  "exchange": "NASDAQ",
  "sector": "Information Technology",
  "sub_industry": "Technology Hardware, Storage & Peripherals",
  "market_cap_usd_b": "197.0",
  "turnaround_flag": "N",
  "source": "SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2",
  "role": "CORE",
  "risk_level": "LOW",
  "risk_flags": "RECENT_INDEX_INCLUSION",
  "action": "KEEP_CORE",
  "review_reason": "RECENT_INDEX_INCLUSION; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker",
  "adr_flag": "N",
  "foreign_ownership_pct": ""
}
```
- market_cap_usd_b in all 3 files: universe=197.0; audit=197.0; sample=197.0
- source: SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2
- updated_at if exists: 2026-05-26
- risk_flags: RECENT_INDEX_INCLUSION
- review_reason: RECENT_INDEX_INCLUSION; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker
- consistency across 3 files: True
- sanity-check note: SNDK 197.0B is NOT confirmed as a metadata error. External reference conflict exists. Do not modify universe_master.csv based only on this report.

## 3. INTC Row Comparison
- universe_master row:
```json
{
  "ticker": "INTC",
  "name": "Intel Corporation",
  "market": "US",
  "sector": "Information Technology",
  "sub_industry": "Semiconductors",
  "market_cap_local": "543.0",
  "market_cap_local_unit": "USD_B",
  "market_cap_usd_b": "543.0",
  "fx_rate_used": "",
  "exchange": "NASDAQ",
  "adr_flag": "N",
  "foreign_ownership_pct": "",
  "company_type": "",
  "turnaround_flag": "Y",
  "updated_at": "2026-05-26",
  "source": "SP500+NDX"
}
```
- audit row:
```json
{
  "ticker": "INTC",
  "name": "Intel Corporation",
  "market": "US",
  "sector": "Information Technology",
  "sub_industry": "Semiconductors",
  "market_cap_usd_b": "543.0",
  "source": "SP500+NDX",
  "company_type": "",
  "turnaround_flag": "Y",
  "universe_role": "HIGH_RISK_REVIEW",
  "quality_risk_level": "HIGH",
  "risk_flags": "TURNAROUND_RISK",
  "review_reason": "TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification",
  "recommended_next_action": "REVIEW_BEFORE_SCORING"
}
```
- sample row:
```json
{
  "sample_id": "S3V01-008",
  "sample_reason_code": "INFORMATION_TECHNOLOGY",
  "sample_reason_note": "IT sector coverage; sector=Information Technology",
  "ticker": "INTC",
  "name": "Intel Corporation",
  "market": "US",
  "exchange": "NASDAQ",
  "sector": "Information Technology",
  "sub_industry": "Semiconductors",
  "market_cap_usd_b": "543.0",
  "turnaround_flag": "Y",
  "source": "SP500+NDX",
  "role": "HIGH_RISK_REVIEW",
  "risk_level": "HIGH",
  "risk_flags": "TURNAROUND_RISK",
  "action": "REVIEW_BEFORE_SCORING",
  "review_reason": "TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification",
  "adr_flag": "N",
  "foreign_ownership_pct": ""
}
```
- market_cap_usd_b in all 3 files: universe=543.0; audit=543.0; sample=543.0
- source: SP500+NDX
- updated_at if exists: 2026-05-26
- turnaround_flag: Y
- risk_flags: TURNAROUND_RISK
- review_reason: TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification
- consistency across 3 files: True
- sanity-check note: INTC 543.0B is NOT confirmed as a metadata error. External reference conflict exists. Do not modify universe_master.csv based only on this report.

## 4. Market Cap Distribution
### Top 30 rows by market_cap_usd_b
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| NVDA | NVIDIA Corporation | US | Information Technology | Semiconductors | 5380.0 | SP500+NDX |
| GOOGL | Alphabet Inc. Class A | US | Communication Services | Interactive Media & Services | 4810.0 | SP500+NDX |
| GOOG | Alphabet Inc. Class C | US | Communication Services | Interactive Media & Services | 4790.0 | SP500+NDX |
| AAPL | Apple Inc. | US | Information Technology | Technology Hardware | 4370.0 | SP500+NDX |
| MSFT | Microsoft Corporation | US | Information Technology | Software | 3150.0 | SP500+NDX |
| AMZN | Amazon.com Inc. | US | Consumer Discretionary | Broadline Retail | 2850.0 | SP500+NDX |
| AVGO | Broadcom Inc. | US | Information Technology | Semiconductors | 1990.0 | SP500+NDX |
| META | Meta Platforms Inc. | US | Communication Services | Interactive Media & Services | 1550.0 | SP500+NDX |
| TSLA | Tesla Inc. | US | Consumer Discretionary | Automobiles | 1540.0 | SP500+NDX |
| 005930.KS | 삼성전자 | KR | Information Technology | Semiconductors | 1248.6 | KOSPI_TOP_AI_INFRA; JUDAL_2026_05_26 |
| TSM | Taiwan Semiconductor Manufacturing Company Limited | US | Information Technology | Semiconductors | 1100.0 | ADR_50B+ |
| WMT | Walmart Inc. | US | Consumer Staples | Consumer Staples Distribution | 1060.0 | SP500 |
| BRK.B | Berkshire Hathaway Inc. | US | Financials | Financial Services | 1050.0 | SP500 |
| 000660.KS | SK하이닉스 | KR | Information Technology | Semiconductors | 1044.6 | KOSPI_TOP_HBM; JUDAL_2026_05_26 |
| LLY | Eli Lilly and Company | US | Health Care | Pharmaceuticals | 881.0 | SP500 |
| JPM | JPMorgan Chase & Co. | US | Financials | Banks | 805.0 | SP500 |
| MU | Micron Technology Inc. | US | Information Technology | Semiconductors | 768.0 | SP500+NDX |
| AMD | Advanced Micro Devices Inc. | US | Information Technology | Semiconductors | 686.0 | SP500+NDX |
| XOM | Exxon Mobil Corporation | US | Energy | Oil Gas & Consumable Fuels | 665.0 | SP500 |
| V | Visa Inc. | US | Financials | Financial Services | 626.0 | SP500 |
| ASML | ASML Holding N.V. | US | Information Technology | Semiconductor Equipment | 597.0 | NDX_ADR |
| JNJ | Johnson & Johnson | US | Health Care | Pharmaceuticals | 551.0 | SP500 |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX |
| ORCL | Oracle Corporation | US | Information Technology | Software | 536.0 | SP500 |
| COST | Costco Wholesale Corporation | US | Consumer Staples | Consumer Staples Distribution | 477.0 | SP500+NDX |
| CSCO | Cisco Systems Inc. | US | Information Technology | Communications Equipment | 469.0 | SP500+NDX |
| MA | Mastercard Incorporated | US | Financials | Financial Services | 446.0 | SP500 |
| CAT | Caterpillar Inc. | US | Industrials | Machinery | 397.0 | SP500 |
| CVX | Chevron Corporation | US | Energy | Oil Gas & Consumable Fuels | 387.0 | SP500 |
| NFLX | Netflix Inc. | US | Communication Services | Entertainment | 377.0 | SP500+NDX |

### Bottom 30 rows by market_cap_usd_b
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| 009450.KS | 경동나비엔 | KR | Industrials | Building Products | 0.7 | KOSPI_HVAC; JUDAL_2026_05_26; ticker_corrected_from_267290_to_009450_v0_2; USER_APPROVED_TICKER_CORRECTION_20260526 |
| 139480.KS | 이마트 | KR | Consumer Staples | Consumer Staples Distribution | 1.8 | KOSPI_RETAIL; JUDAL_2026_05_26 |
| 004990.KS | 롯데지주 | KR | Consumer Discretionary | Multi-line Retail | 1.9 | KOSPI_HOLDING; JUDAL_2026_05_26; holding_classification_v0_2 |
| 097950.KS | CJ제일제당 | KR | Consumer Staples | Food Products | 2.3 | KOSPI_TOP; JUDAL_2026_05_26 |
| 251270.KS | 넷마블 | KR | Communication Services | Entertainment | 2.5 | KOSPI_GAME; JUDAL_2026_05_26 |
| LPL | LG Display Co. Ltd. ADR | US | Information Technology | Electronic Components | 3 | US_ADR_KR_COMPANY |
| 108490.KQ | 로보티즈 | KR | Industrials | Machinery | 3.3 | JUDAL_2026_05_26; KOSDAQ_THEME_ROBOTICS_TOP |
| 222800.KQ | 심텍 | KR | Information Technology | Electronic Components | 3.6 | JUDAL_2026_05_26; KOSDAQ_THEME_AI_TOP |
| 310210.KQ | 보로노이 | KR | Health Care | Biotechnology | 3.6 | JUDAL_2026_05_26; KOSDAQ_THEME_BIO_TOP_EX_TOP15 |
| 095340.KQ | ISC | KR | Information Technology | Semiconductor Equipment | 3.6 | JUDAL_2026_05_26; KOSDAQ_THEME_SEMICON_EQUIPMENT_TOP_EX_TOP15 |
| 178320.KQ | 서진시스템 | KR | Industrials | Electrical Equipment | 3.6 | JUDAL_2026_05_26; KOSDAQ_THEME_BATTERY_TOP_EX_TOP15 |
| 088980.KS | 맥쿼리인프라 | KR | Utilities | Multi-Utilities | 3.8 | KOSPI_INFRA_REIT; JUDAL_2026_05_26 |
| 018880.KS | 한온시스템 | KR | Consumer Discretionary | Automobile Components | 3.8 | KOSPI_AUTO_PARTS; JUDAL_2026_05_26 |
| 004020.KS | 현대제철 | KR | Materials | Metals & Mining | 4.0 | KOSPI_STEEL; JUDAL_2026_05_26 |
| 141080.KQ | 리가켐바이오 | KR | Health Care | Biotechnology | 4.1 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 440110.KQ | 파두 | KR | Information Technology | Semiconductors | 4.2 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 128940.KS | 한미약품 | KR | Health Care | Pharmaceuticals | 4.3 | KOSPI_PHARMA; JUDAL_2026_05_26 |
| 240810.KQ | 원익IPS | KR | Information Technology | Semiconductor Equipment | 4.3 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 087010.KQ | 펩트론 | KR | Health Care | Biotechnology | 4.5 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 241560.KS | 두산밥캣 | KR | Industrials | Machinery | 4.7 | KOSPI_TOP; JUDAL_2026_05_26 |
| 336260.KS | 두산퓨얼셀 | KR | Industrials | Electrical Equipment | 4.7 | KOSPI_TOP_FUELCELL; JUDAL_2026_05_26 |
| 298380.KQ | 에이비엘바이오 | KR | Health Care | Biotechnology | 4.7 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 032640.KS | LG유플러스 | KR | Communication Services | Wireless Telecommunication | 4.8 | KOSPI_TELECOM; JUDAL_2026_05_26 |
| 039030.KQ | 이오테크닉스 | KR | Information Technology | Semiconductor Equipment | 4.8 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 000100.KS | 유한양행 | KR | Health Care | Pharmaceuticals | 4.9 | KOSPI_PHARMA; JUDAL_2026_05_26 |
| EPAM | EPAM Systems Inc. | US | Information Technology | IT Services | 5.0 | SP500 |
| 090430.KS | 아모레퍼시픽 | KR | Consumer Staples | Personal Care Products | 5.0 | KOSPI_TOP_KBEAUTY; JUDAL_2026_05_26 |
| 028300.KQ | HLB | KR | Health Care | Biotechnology | 5.0 | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 078930.KS | GS | KR | Industrials | Industrial Conglomerates | 5.1 | KOSPI_HOLDING; JUDAL_2026_05_26; holding_classification_v0_2 |
| 009830.KS | 한화솔루션 | KR | Materials | Chemicals | 5.5 | KOSPI_TOP_SOLAR; JUDAL_2026_05_26 |

### Rows with market_cap_usd_b >= 300
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| NVDA | NVIDIA Corporation | US | Information Technology | Semiconductors | 5380.0 | SP500+NDX |
| GOOGL | Alphabet Inc. Class A | US | Communication Services | Interactive Media & Services | 4810.0 | SP500+NDX |
| GOOG | Alphabet Inc. Class C | US | Communication Services | Interactive Media & Services | 4790.0 | SP500+NDX |
| AAPL | Apple Inc. | US | Information Technology | Technology Hardware | 4370.0 | SP500+NDX |
| MSFT | Microsoft Corporation | US | Information Technology | Software | 3150.0 | SP500+NDX |
| AMZN | Amazon.com Inc. | US | Consumer Discretionary | Broadline Retail | 2850.0 | SP500+NDX |
| AVGO | Broadcom Inc. | US | Information Technology | Semiconductors | 1990.0 | SP500+NDX |
| META | Meta Platforms Inc. | US | Communication Services | Interactive Media & Services | 1550.0 | SP500+NDX |
| TSLA | Tesla Inc. | US | Consumer Discretionary | Automobiles | 1540.0 | SP500+NDX |
| 005930.KS | 삼성전자 | KR | Information Technology | Semiconductors | 1248.6 | KOSPI_TOP_AI_INFRA; JUDAL_2026_05_26 |
| TSM | Taiwan Semiconductor Manufacturing Company Limited | US | Information Technology | Semiconductors | 1100.0 | ADR_50B+ |
| WMT | Walmart Inc. | US | Consumer Staples | Consumer Staples Distribution | 1060.0 | SP500 |
| BRK.B | Berkshire Hathaway Inc. | US | Financials | Financial Services | 1050.0 | SP500 |
| 000660.KS | SK하이닉스 | KR | Information Technology | Semiconductors | 1044.6 | KOSPI_TOP_HBM; JUDAL_2026_05_26 |
| LLY | Eli Lilly and Company | US | Health Care | Pharmaceuticals | 881.0 | SP500 |
| JPM | JPMorgan Chase & Co. | US | Financials | Banks | 805.0 | SP500 |
| MU | Micron Technology Inc. | US | Information Technology | Semiconductors | 768.0 | SP500+NDX |
| AMD | Advanced Micro Devices Inc. | US | Information Technology | Semiconductors | 686.0 | SP500+NDX |
| XOM | Exxon Mobil Corporation | US | Energy | Oil Gas & Consumable Fuels | 665.0 | SP500 |
| V | Visa Inc. | US | Financials | Financial Services | 626.0 | SP500 |
| ASML | ASML Holding N.V. | US | Information Technology | Semiconductor Equipment | 597.0 | NDX_ADR |
| JNJ | Johnson & Johnson | US | Health Care | Pharmaceuticals | 551.0 | SP500 |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX |
| ORCL | Oracle Corporation | US | Information Technology | Software | 536.0 | SP500 |
| COST | Costco Wholesale Corporation | US | Consumer Staples | Consumer Staples Distribution | 477.0 | SP500+NDX |
| CSCO | Cisco Systems Inc. | US | Information Technology | Communications Equipment | 469.0 | SP500+NDX |
| MA | Mastercard Incorporated | US | Financials | Financial Services | 446.0 | SP500 |
| CAT | Caterpillar Inc. | US | Industrials | Machinery | 397.0 | SP500 |
| CVX | Chevron Corporation | US | Energy | Oil Gas & Consumable Fuels | 387.0 | SP500 |
| NFLX | Netflix Inc. | US | Communication Services | Entertainment | 377.0 | SP500+NDX |
| ABBV | AbbVie Inc. | US | Health Care | Biotechnology | 369.0 | SP500 |
| BAC | Bank of America Corporation | US | Financials | Banks | 359.0 | SP500 |
| UNH | UnitedHealth Group Incorporated | US | Health Care | Health Care Providers | 355.0 | SP500 |
| KO | The Coca-Cola Company | US | Consumer Staples | Beverages | 349.0 | SP500 |
| LRCX | Lam Research Corporation | US | Information Technology | Semiconductor Equipment | 347.0 | SP500+NDX |
| PG | The Procter & Gamble Company | US | Consumer Staples | Household Products | 331.0 | SP500 |
| AMAT | Applied Materials Inc. | US | Information Technology | Semiconductor Equipment | 328.0 | SP500+NDX |
| PLTR | Palantir Technologies Inc. | US | Information Technology | Software | 323.0 | SP500+NDX |
| SAP | SAP SE | US | Information Technology | Software | 320.0 | ADR_50B+ |
| MS | Morgan Stanley | US | Financials | Capital Markets | 303.0 | SP500 |

### Rows with market_cap_usd_b >= 100 and source suggesting NEW/corrected/manual/USER_APPROVED/RECENT_INDEX_INCLUSION
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| SNDK | Sandisk Corporation | US | Information Technology | Technology Hardware, Storage & Peripherals | 197.0 | SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2 |

### Top 20 Information Technology rows
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| NVDA | NVIDIA Corporation | US | Information Technology | Semiconductors | 5380.0 | SP500+NDX |
| AAPL | Apple Inc. | US | Information Technology | Technology Hardware | 4370.0 | SP500+NDX |
| MSFT | Microsoft Corporation | US | Information Technology | Software | 3150.0 | SP500+NDX |
| AVGO | Broadcom Inc. | US | Information Technology | Semiconductors | 1990.0 | SP500+NDX |
| 005930.KS | 삼성전자 | KR | Information Technology | Semiconductors | 1248.6 | KOSPI_TOP_AI_INFRA; JUDAL_2026_05_26 |
| TSM | Taiwan Semiconductor Manufacturing Company Limited | US | Information Technology | Semiconductors | 1100.0 | ADR_50B+ |
| 000660.KS | SK하이닉스 | KR | Information Technology | Semiconductors | 1044.6 | KOSPI_TOP_HBM; JUDAL_2026_05_26 |
| MU | Micron Technology Inc. | US | Information Technology | Semiconductors | 768.0 | SP500+NDX |
| AMD | Advanced Micro Devices Inc. | US | Information Technology | Semiconductors | 686.0 | SP500+NDX |
| ASML | ASML Holding N.V. | US | Information Technology | Semiconductor Equipment | 597.0 | NDX_ADR |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX |
| ORCL | Oracle Corporation | US | Information Technology | Software | 536.0 | SP500 |
| CSCO | Cisco Systems Inc. | US | Information Technology | Communications Equipment | 469.0 | SP500+NDX |
| LRCX | Lam Research Corporation | US | Information Technology | Semiconductor Equipment | 347.0 | SP500+NDX |
| AMAT | Applied Materials Inc. | US | Information Technology | Semiconductor Equipment | 328.0 | SP500+NDX |
| PLTR | Palantir Technologies Inc. | US | Information Technology | Software | 323.0 | SP500+NDX |
| SAP | SAP SE | US | Information Technology | Software | 320.0 | ADR_50B+ |
| TXN | Texas Instruments Incorporated | US | Information Technology | Semiconductors | 273.0 | SP500+NDX |
| ARM | Arm Holdings plc | US | Information Technology | Semiconductors | 235.0 | NDX_ADR |
| KLAC | KLA Corporation | US | Information Technology | Semiconductor Equipment | 229.0 | SP500+NDX |

### turnaround_flag == Y rows
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source | turnaround_flag | role | risk_flags | review_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| DIS | The Walt Disney Company | US | Communication Services | Entertainment | 180.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BA | The Boeing Company | US | Industrials | Aerospace & Defense | 173.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PFE | Pfizer Inc. | US | Health Care | Pharmaceuticals | 144.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| CVS | CVS Health Corporation | US | Health Care | Health Care Providers | 122.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| SBUX | Starbucks Corporation | US | Consumer Discretionary | Hotels Restaurants | 121.0 | SP500+NDX | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| WBD | Warner Bros. Discovery Inc. | US | Communication Services | Entertainment | 67.0 | SP500+NDX | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| GM | General Motors Company | US | Consumer Discretionary | Automobiles | 65.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| NKE | NIKE Inc. | US | Consumer Discretionary | Textiles & Apparel | 63.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| TGT | Target Corporation | US | Consumer Staples | Consumer Staples Distribution | 56.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| F | Ford Motor Company | US | Consumer Discretionary | Automobiles | 51.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PYPL | PayPal Holdings Inc. | US | Financials | Financial Services | 39.0 | SP500+NDX | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| EL | The Estée Lauder Companies Inc. | US | Consumer Staples | Personal Care Products | 28.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BIIB | Biogen Inc. | US | Health Care | Biotechnology | 28.0 | SP500 | Y | HIGH_RISK_REVIEW | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| MRNA | Moderna Inc. | US | Health Care | Biotechnology | 19.0 | SP500 | Y | HIGH_RISK_REVIEW | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| SMCI | Super Micro Computer Inc. | US | Information Technology | Technology Hardware | 18.0 | SP500 | Y | HIGH_RISK_REVIEW | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BAX | Baxter International Inc. | US | Health Care | Health Care Equipment | 9.0 | SP500 | Y | EXCLUDE_CANDIDATE | TURNAROUND_RISK;SMALL_CAP_RISK;DATA_LIMITATION;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |


## 5. Outlier / Rounding Pattern Check
### Rows > 5x sector+sub_industry median
| ticker | name | sector | sub_industry | market_cap_usd_b | group_median | group_n | ratio | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | Apple Inc. | Information Technology | Technology Hardware | 4370.0 | 98.50 | 8 | 44.37x | SP500+NDX |
| MSFT | Microsoft Corporation | Information Technology | Software | 3150.0 | 92.00 | 29 | 34.24x | SP500+NDX |
| BRK.B | Berkshire Hathaway Inc. | Financials | Financial Services | 1050.0 | 34.50 | 10 | 30.43x | SP500 |
| WMT | Walmart Inc. | Consumer Staples | Consumer Staples Distribution | 1060.0 | 35.00 | 9 | 30.29x | SP500 |
| ASML | ASML Holding N.V. | Information Technology | Semiconductor Equipment | 597.0 | 22.40 | 11 | 26.65x | NDX_ADR |
| AMZN | Amazon.com Inc. | Consumer Discretionary | Broadline Retail | 2850.0 | 110.00 | 6 | 25.91x | SP500+NDX |
| NVDA | NVIDIA Corporation | Information Technology | Semiconductors | 5380.0 | 214.00 | 21 | 25.14x | SP500+NDX |
| JPM | JPMorgan Chase & Co. | Financials | Banks | 805.0 | 32.25 | 26 | 24.96x | SP500 |
| TSLA | Tesla Inc. | Consumer Discretionary | Automobiles | 1540.0 | 65.00 | 7 | 23.69x | SP500+NDX |
| V | Visa Inc. | Financials | Financial Services | 626.0 | 34.50 | 10 | 18.14x | SP500 |
| TMUS | T-Mobile US Inc. | Communication Services | Wireless Telecommunication | 206.0 | 12.75 | 6 | 16.16x | SP500+NDX |
| LRCX | Lam Research Corporation | Information Technology | Semiconductor Equipment | 347.0 | 22.40 | 11 | 15.49x | SP500+NDX |
| CAT | Caterpillar Inc. | Industrials | Machinery | 397.0 | 26.00 | 24 | 15.27x | SP500 |
| ABBV | AbbVie Inc. | Health Care | Biotechnology | 369.0 | 25.00 | 19 | 14.76x | SP500 |
| AMAT | Applied Materials Inc. | Information Technology | Semiconductor Equipment | 328.0 | 22.40 | 11 | 14.64x | SP500+NDX |
| COST | Costco Wholesale Corporation | Consumer Staples | Consumer Staples Distribution | 477.0 | 35.00 | 9 | 13.63x | SP500+NDX |
| MA | Mastercard Incorporated | Financials | Financial Services | 446.0 | 34.50 | 10 | 12.93x | SP500 |
| LIN | Linde plc | Materials | Chemicals | 236.0 | 20.00 | 17 | 11.80x | SP500+NDX |
| BAC | Bank of America Corporation | Financials | Banks | 359.0 | 32.25 | 26 | 11.13x | SP500 |
| PG | The Procter & Gamble Company | Consumer Staples | Household Products | 331.0 | 32.00 | 6 | 10.34x | SP500 |
| KLAC | KLA Corporation | Information Technology | Semiconductor Equipment | 229.0 | 22.40 | 11 | 10.22x | SP500+NDX |
| NFLX | Netflix Inc. | Communication Services | Entertainment | 377.0 | 38.00 | 11 | 9.92x | SP500+NDX |
| AVGO | Broadcom Inc. | Information Technology | Semiconductors | 1990.0 | 214.00 | 21 | 9.30x | SP500+NDX |
| IBM | IBM Corporation | Information Technology | IT Services | 209.0 | 22.50 | 8 | 9.29x | SP500 |
| XOM | Exxon Mobil Corporation | Energy | Oil Gas & Consumable Fuels | 665.0 | 72.00 | 25 | 9.24x | SP500 |
| KO | The Coca-Cola Company | Consumer Staples | Beverages | 349.0 | 40.00 | 11 | 8.72x | SP500 |
| GEV | GE Vernova Inc. | Industrials | Electrical Equipment | 272.0 | 33.75 | 18 | 8.06x | SP500 |
| TT | Trane Technologies plc | Industrials | Building Products | 101.0 | 13.00 | 9 | 7.77x | SP500 |
| UNH | UnitedHealth Group Incorporated | Health Care | Health Care Providers | 355.0 | 46.00 | 15 | 7.72x | SP500 |
| HON | Honeywell International Inc. | Industrials | Industrial Conglomerates | 137.0 | 18.45 | 10 | 7.43x | SP500+NDX |
| WFC | Wells Fargo & Company | Financials | Banks | 227.0 | 32.25 | 26 | 7.04x | SP500 |
| AMGN | Amgen Inc. | Health Care | Biotechnology | 175.0 | 25.00 | 19 | 7.00x | SP500+NDX |
| CSCO | Cisco Systems Inc. | Information Technology | Communications Equipment | 469.0 | 70.00 | 7 | 6.70x | SP500+NDX |
| TMO | Thermo Fisher Scientific Inc. | Health Care | Life Sciences Tools | 164.0 | 24.50 | 10 | 6.69x | SP500 |
| C | Citigroup Inc. | Financials | Banks | 208.0 | 32.25 | 26 | 6.45x | SP500 |
| GILD | Gilead Sciences Inc. | Health Care | Biotechnology | 160.0 | 25.00 | 19 | 6.40x | SP500+NDX |
| JCI | Johnson Controls International plc | Industrials | Building Products | 83.0 | 13.00 | 9 | 6.38x | SP500 |
| LLY | Eli Lilly and Company | Health Care | Pharmaceuticals | 881.0 | 144.00 | 13 | 6.12x | SP500 |
| MS | Morgan Stanley | Financials | Capital Markets | 303.0 | 50.50 | 28 | 6.00x | SP500 |
| DE | Deere & Company | Industrials | Machinery | 152.0 | 26.00 | 24 | 5.85x | SP500 |
| 005930.KS | 삼성전자 | Information Technology | Semiconductors | 1248.6 | 214.00 | 21 | 5.83x | KOSPI_TOP_AI_INFRA; JUDAL_2026_05_26 |
| ORCL | Oracle Corporation | Information Technology | Software | 536.0 | 92.00 | 29 | 5.83x | SP500 |
| GS | The Goldman Sachs Group Inc. | Financials | Capital Markets | 290.0 | 50.50 | 28 | 5.74x | SP500 |
| HSBC | HSBC Holdings plc | Financials | Banks | 180.0 | 32.25 | 26 | 5.58x | ADR_50B+ |
| ISRG | Intuitive Surgical Inc. | Health Care | Health Care Equipment | 155.0 | 28.00 | 18 | 5.54x | SP500+NDX |
| ABT | Abbott Laboratories | Health Care | Health Care Equipment | 153.0 | 28.00 | 18 | 5.46x | SP500 |
| MDLZ | Mondelez International Inc. | Consumer Staples | Food Products | 79.0 | 14.50 | 14 | 5.45x | SP500+NDX |
| NEE | NextEra Energy Inc. | Utilities | Electric Utilities | 185.0 | 34.00 | 19 | 5.44x | SP500 |
| CVX | Chevron Corporation | Energy | Oil Gas & Consumable Fuels | 387.0 | 72.00 | 25 | 5.38x | SP500 |
| GE | GE Aerospace | Industrials | Aerospace & Defense | 298.0 | 57.00 | 17 | 5.23x | SP500 |
| TSM | Taiwan Semiconductor Manufacturing Company Limited | Information Technology | Semiconductors | 1100.0 | 214.00 | 21 | 5.14x | ADR_50B+ |
| PEP | PepsiCo Inc. | Consumer Staples | Beverages | 203.0 | 40.00 | 11 | 5.08x | SP500+NDX |
| SPG | Simon Property Group Inc. | Real Estate | Retail REITs | 76.0 | 15.00 | 5 | 5.07x | SP500 |
| UL | Unilever PLC | Consumer Staples | Personal Care Products | 140.0 | 28.00 | 3 | 5.00x | ADR_50B+ |

### Rows < 0.2x sector+sub_industry median
| ticker | name | sector | sub_industry | market_cap_usd_b | group_median | group_n | ratio | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 440110.KQ | 파두 | Information Technology | Semiconductors | 4.2 | 214.00 | 21 | 0.020x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 128940.KS | 한미약품 | Health Care | Pharmaceuticals | 4.3 | 144.00 | 13 | 0.030x | KOSPI_PHARMA; JUDAL_2026_05_26 |
| 000100.KS | 유한양행 | Health Care | Pharmaceuticals | 4.9 | 144.00 | 13 | 0.034x | KOSPI_PHARMA; JUDAL_2026_05_26 |
| 000250.KQ | 삼천당제약 | Health Care | Pharmaceuticals | 6.1 | 144.00 | 13 | 0.042x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| SWKS | Skyworks Solutions Inc. | Information Technology | Semiconductors | 10.0 | 214.00 | 21 | 0.047x | SP500 |
| 139480.KS | 이마트 | Consumer Staples | Consumer Staples Distribution | 1.8 | 35.00 | 9 | 0.051x | KOSPI_RETAIL; JUDAL_2026_05_26 |
| 009450.KS | 경동나비엔 | Industrials | Building Products | 0.7 | 13.00 | 9 | 0.054x | KOSPI_HVAC; JUDAL_2026_05_26; ticker_corrected_from_267290_to_009450_v0_2; USER_APPROVED_TICKER_CORRECTION_20260526 |
| 251270.KS | 넷마블 | Communication Services | Entertainment | 2.5 | 38.00 | 11 | 0.066x | KOSPI_GAME; JUDAL_2026_05_26 |
| 004020.KS | 현대제철 | Materials | Metals & Mining | 4.0 | 50.00 | 11 | 0.080x | KOSPI_STEEL; JUDAL_2026_05_26 |
| LPL | LG Display Co. Ltd. ADR | Information Technology | Electronic Components | 3 | 35.00 | 9 | 0.086x | US_ADR_KR_COMPANY |
| 222800.KQ | 심텍 | Information Technology | Electronic Components | 3.6 | 35.00 | 9 | 0.103x | JUDAL_2026_05_26; KOSDAQ_THEME_AI_TOP |
| 178320.KQ | 서진시스템 | Industrials | Electrical Equipment | 3.6 | 33.75 | 18 | 0.107x | JUDAL_2026_05_26; KOSDAQ_THEME_BATTERY_TOP_EX_TOP15 |
| TTD | The Trade Desk Inc. | Information Technology | Software | 10.0 | 92.00 | 29 | 0.109x | SP500 |
| FSLR | First Solar Inc. | Information Technology | Semiconductors | 25.0 | 214.00 | 21 | 0.117x | SP500 |
| 010950.KS | S-Oil | Energy | Oil Gas & Consumable Fuels | 8.9 | 72.00 | 25 | 0.124x | KOSPI_TOP_FOREIGN_HIGH; JUDAL_2026_05_26 |
| 108490.KQ | 로보티즈 | Industrials | Machinery | 3.3 | 26.00 | 24 | 0.127x | JUDAL_2026_05_26; KOSDAQ_THEME_ROBOTICS_TOP |
| 033780.KS | KT&G | Consumer Staples | Tobacco | 13.5 | 105.50 | 4 | 0.128x | KOSPI_TOP_FOREIGN_HIGH; JUDAL_2026_05_26 |
| GDDY | GoDaddy Inc. | Information Technology | Software | 12.0 | 92.00 | 29 | 0.130x | SP500 |
| 088980.KS | 맥쿼리인프라 | Utilities | Multi-Utilities | 3.8 | 29.00 | 10 | 0.131x | KOSPI_INFRA_REIT; JUDAL_2026_05_26 |
| VTRS | Viatris Inc. | Health Care | Pharmaceuticals | 19.0 | 144.00 | 13 | 0.132x | SP500 |
| 307950.KS | 현대오토에버 | Information Technology | Software | 12.5 | 92.00 | 29 | 0.136x | KOSPI_TOP_AUTO_IT; JUDAL_2026_05_26 |
| 336260.KS | 두산퓨얼셀 | Industrials | Electrical Equipment | 4.7 | 33.75 | 18 | 0.139x | KOSPI_TOP_FUELCELL; JUDAL_2026_05_26 |
| TYL | Tyler Technologies Inc. | Information Technology | Software | 13.0 | 92.00 | 29 | 0.141x | SP500 |
| 310210.KQ | 보로노이 | Health Care | Biotechnology | 3.6 | 25.00 | 19 | 0.144x | JUDAL_2026_05_26; KOSDAQ_THEME_BIO_TOP_EX_TOP15 |
| GEN | Gen Digital Inc. | Information Technology | Software | 14.0 | 92.00 | 29 | 0.152x | SP500 |
| FDS | FactSet Research Systems Inc. | Financials | Capital Markets | 8.0 | 50.50 | 28 | 0.158x | SP500 |
| 097950.KS | CJ제일제당 | Consumer Staples | Food Products | 2.3 | 14.50 | 14 | 0.159x | KOSPI_TOP; JUDAL_2026_05_26 |
| 095340.KQ | ISC | Information Technology | Semiconductor Equipment | 3.6 | 22.40 | 11 | 0.161x | JUDAL_2026_05_26; KOSDAQ_THEME_SEMICON_EQUIPMENT_TOP_EX_TOP15 |
| 141080.KQ | 리가켐바이오 | Health Care | Biotechnology | 4.1 | 25.00 | 19 | 0.164x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| NCLH | Norwegian Cruise Line Holdings Ltd. | Consumer Discretionary | Hotels Restaurants | 7.0 | 42.00 | 18 | 0.167x | SP500 |
| PTC | PTC Inc. | Information Technology | Software | 16.0 | 92.00 | 29 | 0.174x | SP500 |
| HSIC | Henry Schein Inc. | Health Care | Health Care Providers | 8.0 | 46.00 | 15 | 0.174x | SP500 |
| BBY | Best Buy Co. Inc. | Consumer Discretionary | Specialty Retail | 12.0 | 68.00 | 11 | 0.176x | SP500 |
| 090430.KS | 아모레퍼시픽 | Consumer Staples | Personal Care Products | 5.0 | 28.00 | 3 | 0.179x | KOSPI_TOP_KBEAUTY; JUDAL_2026_05_26 |
| 087010.KQ | 펩트론 | Health Care | Biotechnology | 4.5 | 25.00 | 19 | 0.180x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 241560.KS | 두산밥캣 | Industrials | Machinery | 4.7 | 26.00 | 24 | 0.181x | KOSPI_TOP; JUDAL_2026_05_26 |
| SMCI | Super Micro Computer Inc. | Information Technology | Technology Hardware | 18.0 | 98.50 | 8 | 0.183x | SP500 |
| WF | Woori Financial Group Inc. ADR | Financials | Banks | 6 | 32.25 | 26 | 0.186x | US_ADR_KR_COMPANY |
| 298380.KQ | 에이비엘바이오 | Health Care | Biotechnology | 4.7 | 25.00 | 19 | 0.188x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 240810.KQ | 원익IPS | Information Technology | Semiconductor Equipment | 4.3 | 22.40 | 11 | 0.192x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| 352820.KS | 하이브 | Communication Services | Entertainment | 7.3 | 38.00 | 11 | 0.192x | KOSPI_TOP_KPOP; JUDAL_2026_05_26 |
| HPQ | HP Inc. | Information Technology | Technology Hardware | 19.0 | 98.50 | 8 | 0.193x | SP500 |
| APA | APA Corporation | Energy | Oil Gas & Consumable Fuels | 14.0 | 72.00 | 25 | 0.194x | SP500 |
| ON | ON Semiconductor Corporation | Information Technology | Semiconductors | 42.0 | 214.00 | 21 | 0.196x | SP500 |
| SYF | Synchrony Financial | Financials | Consumer Finance | 23.0 | 116.00 | 3 | 0.198x | SP500 |
| 028300.KQ | HLB | Health Care | Biotechnology | 5.0 | 25.00 | 19 | 0.200x | JUDAL_2026_05_26; KOSDAQ_TOP15 |
| TAP | Molson Coors Beverage Company | Consumer Staples | Beverages | 8.0 | 40.00 | 11 | 0.200x | SP500 |

### Repeated market_cap_usd_b groups
| market_cap_usd_b | count | tickers |
| --- | --- | --- |
| 12.0 | 14 | HII, TRMB, GPC, DVA, AIZ, MKC, ZBRA, GL, BBY, IVZ, GDDY, PNW, BF.B, AVY |
| 25.0 | 13 | CINF, AVB, CFG, EXPE, XYL, FE, ES, STZ, EQR, DXCM, FSLR, INSM, 005490.KS |
| 10.0 | 13 | CPT, BXP, RVTY, SWKS, PODD, TTD, IT, AES, UHS, DPZ, FRT, JKHY, WYNN |
| 19.0 | 12 | DD, WSM, BRO, RL, SW, CHTR, EFX, CF, VTRS, HPQ, MRNA, INCY |
| 13.0 | 11 | LULU, DOC, CSGP, TYL, DECK, J, UDR, CDW, HAS, SOLV, MAS |
| 11.0 | 11 | COO, PNR, SWK, ERIE, ALGN, CLX, APTV, HRL, SJM, ALLE, PSKY |
| 50.0 | 10 | COR, EBAY, FAST, EA, TER, MCHP, ETR, HMC, E, VALE |
| 22.0 | 10 | CHD, KEY, CPAY, VRSK, FIS, NI, CMS, L, DRI, PFG |
| 38.0 | 9 | DHI, EME, LYV, HSY, IBKR, CBOE, PEG, CBRE, ALNY |
| 32.0 | 9 | KVUE, STLD, WAT, ZTS, CPRT, AXON, WDAY, KMB, BBD |
| 27.0 | 9 | GEHC, VRSN, DOW, KHC, FOXA, FICO, IR, OTIS, CNP |
| 21.0 | 9 | TROW, AKAM, MTD, SBAC, WST, FFIV, VLTO, PHM, DGX |
| 20.0 | 9 | LH, ULTA, STE, OMC, ALB, LEN, EXPD, CHRW, TEAM |
| 18.0 | 9 | EVRG, SNA, IFF, GPN, LUV, PKG, LNT, SMCI, ESS |
| 15.0 | 9 | KIM, TXT, LDOS, IEX, NDSN, NVR, MAA, HST, NWS |
| 35.0 | 8 | EQT, PRU, HAL, JBL, WEC, SYY, TRI, ABEV |
| 26.0 | 8 | WRB, TPL, TPR, NRG, EIX, ROL, PPL, FOX |
| 23.0 | 8 | LYB, SYF, NTAP, EXE, TSN, DG, PPG, RF |
| 14.0 | 8 | GNRC, BALL, GEN, REG, NWSA, APA, EG, 196170.KQ |
| 8.0 | 8 | HSIC, FDS, ARE, TAP, AOS, BLDR, ASR, BSAC |
| 7.0 | 8 | CRL, NCLH, TECH, MOS, POOL, CAG, 003230.KS, 005830.KS |
| 43.0 | 7 | HPE, GRMN, FITB, CMG, VTR, IDXX, 012330.KS |
| 24.0 | 7 | HUBB, JBHT, AWK, CTSH, WTW, BG, ZS |
| 17.0 | 7 | FTV, GIS, DLTR, LII, BR, AMCR, INVH |
| 58.0 | 6 | SRE, TRGP, PCAR, TFC, TEL, KEYS |
| 42.0 | 6 | ON, STT, MSCI, ODFL, AMP, XYZ |
| 39.0 | 6 | SATS, ED, CCI, BDX, PYPL, ADM |
| 30.0 | 6 | EXR, NTRS, FISV, MTB, RJF, UAL |
| 28.0 | 6 | EL, IQV, CNC, TDY, DOV, BIIB |
| 16.0 | 6 | PTC, TSCO, BEN, WY, ZBH, IP |
| 95.0 | 5 | DUK, SNPS, CDNS, WMB, PBR |
| 79.0 | 5 | MMC, ABNB, MMM, MDLZ, MELI |
| 69.0 | 5 | CTAS, AON, HOOD, AEP, CRH |
| 65.0 | 5 | GM, BKR, APD, FIX, TRV |
| 59.0 | 5 | GWW, D, OXY, URI, OKE |
| 33.0 | 5 | PAYX, ROP, MLM, ACGL, LVS |
| 31.0 | 5 | A, CASY, HBAN, Q, VICI |
| 93.0 | 4 | HCA, BK, CMI, MCK |
| 85.0 | 4 | CSX, PNC, ELV, SLB |
| 76.0 | 4 | VLO, SPG, EOG, ORLY |
| 75.0 | 4 | CI, MPC, KMI, DEO |
| 74.0 | 4 | DDOG, SHW, CIEN, EMR |
| 70.0 | 4 | COHR, DASH, ECL, ITUB |
| 57.0 | 4 | LHX, FANG, O, DVN |
| 51.0 | 4 | F, AME, NUE, ADSK |
| 34.0 | 4 | PCG, VMC, CCL, 034730.KS |
| 29.0 | 4 | ATO, AEE, RMD, DTE |
| 3.6 | 4 | 222800.KQ, 310210.KQ, 095340.KQ, 178320.KQ |
| 298.0 | 3 | HD, PM, GE |
| 180.0 | 3 | DIS, NVO, HSBC |
| 130.0 | 3 | VRT, MUFG, BHP |
| 123.0 | 3 | SPGI, MO, SHOP |
| 110.0 | 3 | VRTX, CME, SONY |
| 89.0 | 3 | WM, ADP, CMCSA |
| 88.0 | 3 | ICE, FDX, BTI |
| 86.0 | 3 | FCX, MNST, KKR |
| 72.0 | 3 | CVNA, HLT, PSX |
| 71.0 | 3 | CL, NSC, ITW |
| 67.0 | 3 | WBD, RCL, DLR |
| 52.0 | 3 | MET, NDAQ, PSA |
| 48.0 | 3 | XEL, ROK, FER |
| 44.0 | 3 | EXC, TTWO, WAB |
| 41.0 | 3 | YUM, KR, AIG |
| 40.0 | 3 | ARES, KDP, CCEP |
| 37.0 | 3 | HIG, TKO, 006400.KS |
| 5.0 | 3 | EPAM, 090430.KS, 028300.KQ |
| 4.7 | 3 | 241560.KS, 336260.KS, 298380.KQ |

### Decimal pattern counts
| pattern | count |
| --- | --- |
| .0 | 556 |
| .1dp_nonzero | 92 |
| integer_string | 8 |

- Note: These are diagnostic signals only. Mega-cap companies and rounded USD_B values can create false positives.

## 6. IT Large-Cap Reference Set
- NVDA: market_cap_usd_b=5380.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- MSFT: market_cap_usd_b=3150.0; sector=Information Technology; sub_industry=Software; source=SP500+NDX
- AAPL: market_cap_usd_b=4370.0; sector=Information Technology; sub_industry=Technology Hardware; source=SP500+NDX
- GOOGL: market_cap_usd_b=4810.0; sector=Communication Services; sub_industry=Interactive Media & Services; source=SP500+NDX
- META: market_cap_usd_b=1550.0; sector=Communication Services; sub_industry=Interactive Media & Services; source=SP500+NDX
- AMZN: market_cap_usd_b=2850.0; sector=Consumer Discretionary; sub_industry=Broadline Retail; source=SP500+NDX
- ORCL: market_cap_usd_b=536.0; sector=Information Technology; sub_industry=Software; source=SP500
- AVGO: market_cap_usd_b=1990.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- AMD: market_cap_usd_b=686.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- QCOM: market_cap_usd_b=214.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- TXN: market_cap_usd_b=273.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- CSCO: market_cap_usd_b=469.0; sector=Information Technology; sub_industry=Communications Equipment; source=SP500+NDX
- IBM: market_cap_usd_b=209.0; sector=Information Technology; sub_industry=IT Services; source=SP500
- SNDK: market_cap_usd_b=197.0; sector=Information Technology; sub_industry=Technology Hardware, Storage & Peripherals; source=SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2
- INTC: market_cap_usd_b=543.0; sector=Information Technology; sub_industry=Semiconductors; source=SP500+NDX
- This section lists values only.
- It does not decide whether a value is right or wrong.

## 7. Same-Batch Candidate Check
### Rows with source similar to SNDK
- SNDK source: SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2
- exact source match count: 1
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| SNDK | Sandisk Corporation | US | Information Technology | Technology Hardware, Storage & Peripherals | 197.0 | SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2 |

- SNDK updated_at: 2026-05-26; same updated_at count: 656
### Rows with source similar to INTC
- INTC source: SP500+NDX
- exact source match with market_cap_usd_b >= 100 count: 41
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| NVDA | NVIDIA Corporation | US | Information Technology | Semiconductors | 5380.0 | SP500+NDX |
| GOOGL | Alphabet Inc. Class A | US | Communication Services | Interactive Media & Services | 4810.0 | SP500+NDX |
| GOOG | Alphabet Inc. Class C | US | Communication Services | Interactive Media & Services | 4790.0 | SP500+NDX |
| AAPL | Apple Inc. | US | Information Technology | Technology Hardware | 4370.0 | SP500+NDX |
| MSFT | Microsoft Corporation | US | Information Technology | Software | 3150.0 | SP500+NDX |
| AMZN | Amazon.com Inc. | US | Consumer Discretionary | Broadline Retail | 2850.0 | SP500+NDX |
| AVGO | Broadcom Inc. | US | Information Technology | Semiconductors | 1990.0 | SP500+NDX |
| META | Meta Platforms Inc. | US | Communication Services | Interactive Media & Services | 1550.0 | SP500+NDX |
| TSLA | Tesla Inc. | US | Consumer Discretionary | Automobiles | 1540.0 | SP500+NDX |
| MU | Micron Technology Inc. | US | Information Technology | Semiconductors | 768.0 | SP500+NDX |
| AMD | Advanced Micro Devices Inc. | US | Information Technology | Semiconductors | 686.0 | SP500+NDX |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX |
| COST | Costco Wholesale Corporation | US | Consumer Staples | Consumer Staples Distribution | 477.0 | SP500+NDX |
| CSCO | Cisco Systems Inc. | US | Information Technology | Communications Equipment | 469.0 | SP500+NDX |
| NFLX | Netflix Inc. | US | Communication Services | Entertainment | 377.0 | SP500+NDX |
| LRCX | Lam Research Corporation | US | Information Technology | Semiconductor Equipment | 347.0 | SP500+NDX |
| AMAT | Applied Materials Inc. | US | Information Technology | Semiconductor Equipment | 328.0 | SP500+NDX |
| PLTR | Palantir Technologies Inc. | US | Information Technology | Software | 323.0 | SP500+NDX |
| TXN | Texas Instruments Incorporated | US | Information Technology | Semiconductors | 273.0 | SP500+NDX |
| LIN | Linde plc | US | Materials | Chemicals | 236.0 | SP500+NDX |
| KLAC | KLA Corporation | US | Information Technology | Semiconductor Equipment | 229.0 | SP500+NDX |
| QCOM | QUALCOMM Incorporated | US | Information Technology | Semiconductors | 214.0 | SP500+NDX |
| TMUS | T-Mobile US Inc. | US | Communication Services | Wireless Telecommunication | 206.0 | SP500+NDX |
| ADI | Analog Devices Inc. | US | Information Technology | Semiconductors | 204.0 | SP500+NDX |
| PEP | PepsiCo Inc. | US | Consumer Staples | Beverages | 203.0 | SP500+NDX |
| PANW | Palo Alto Networks Inc. | US | Information Technology | Software | 200.0 | SP500+NDX |
| AMGN | Amgen Inc. | US | Health Care | Biotechnology | 175.0 | SP500+NDX |
| STX | Seagate Technology Holdings plc | US | Information Technology | Technology Hardware | 166.0 | SP500+NDX |
| APP | AppLovin Corporation | US | Information Technology | Software | 165.0 | SP500+NDX |
| GILD | Gilead Sciences Inc. | US | Health Care | Biotechnology | 160.0 | SP500+NDX |
| WDC | Western Digital Corporation | US | Information Technology | Technology Hardware | 158.0 | SP500+NDX |
| CRWD | CrowdStrike Holdings Inc. | US | Information Technology | Software | 157.0 | SP500+NDX |
| ISRG | Intuitive Surgical Inc. | US | Health Care | Health Care Equipment | 155.0 | SP500+NDX |
| HON | Honeywell International Inc. | US | Industrials | Industrial Conglomerates | 137.0 | SP500+NDX |
| SBUX | Starbucks Corporation | US | Consumer Discretionary | Hotels Restaurants | 121.0 | SP500+NDX |
| BKNG | Booking Holdings Inc. | US | Consumer Discretionary | Hotels Restaurants | 120.0 | SP500+NDX |
| INTU | Intuit Inc. | US | Information Technology | Software | 111.0 | SP500+NDX |
| VRTX | Vertex Pharmaceuticals Incorporated | US | Health Care | Biotechnology | 110.0 | SP500+NDX |
| CME | CME Group Inc. | US | Financials | Capital Markets | 110.0 | SP500+NDX |
| EQIX | Equinix Inc. | US | Real Estate | Specialized REITs | 104.0 | SP500+NDX |
| ADBE | Adobe Inc. | US | Information Technology | Software | 103.0 | SP500+NDX |

- INTC updated_at: 2026-05-26; same updated_at count: 656
### Rows containing APR2026 / NEW / corrected / manual / USER_APPROVED / RECENT_INDEX_INCLUSION
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source | risk_flags | review_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 009450.KS | 경동나비엔 | KR | Industrials | Building Products | 0.7 | KOSPI_HVAC; JUDAL_2026_05_26; ticker_corrected_from_267290_to_009450_v0_2; USER_APPROVED_TICKER_CORRECTION_20260526 | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| SNDK | Sandisk Corporation | US | Information Technology | Technology Hardware, Storage & Peripherals | 197.0 | SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2 | RECENT_INDEX_INCLUSION | RECENT_INDEX_INCLUSION; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| VEEV | Veeva Systems Inc. | US | Health Care | Health Care Technology | 26.1 | SP500_NEW_MAY2026; market_cap_stockanalysis_2026_05_26 | HEALTHCARE_EVENT_RISK;RECENT_INDEX_INCLUSION | RECENT_INDEX_INCLUSION; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; below core threshold but retained for extended monitoring |

### SP500 / NDX / SP500+NDX rows with market_cap_usd_b >= 100
| ticker | name | market | sector | sub_industry | market_cap_usd_b | source |
| --- | --- | --- | --- | --- | --- | --- |
| NVDA | NVIDIA Corporation | US | Information Technology | Semiconductors | 5380.0 | SP500+NDX |
| GOOGL | Alphabet Inc. Class A | US | Communication Services | Interactive Media & Services | 4810.0 | SP500+NDX |
| GOOG | Alphabet Inc. Class C | US | Communication Services | Interactive Media & Services | 4790.0 | SP500+NDX |
| AAPL | Apple Inc. | US | Information Technology | Technology Hardware | 4370.0 | SP500+NDX |
| MSFT | Microsoft Corporation | US | Information Technology | Software | 3150.0 | SP500+NDX |
| AMZN | Amazon.com Inc. | US | Consumer Discretionary | Broadline Retail | 2850.0 | SP500+NDX |
| AVGO | Broadcom Inc. | US | Information Technology | Semiconductors | 1990.0 | SP500+NDX |
| META | Meta Platforms Inc. | US | Communication Services | Interactive Media & Services | 1550.0 | SP500+NDX |
| TSLA | Tesla Inc. | US | Consumer Discretionary | Automobiles | 1540.0 | SP500+NDX |
| WMT | Walmart Inc. | US | Consumer Staples | Consumer Staples Distribution | 1060.0 | SP500 |
| BRK.B | Berkshire Hathaway Inc. | US | Financials | Financial Services | 1050.0 | SP500 |
| LLY | Eli Lilly and Company | US | Health Care | Pharmaceuticals | 881.0 | SP500 |
| JPM | JPMorgan Chase & Co. | US | Financials | Banks | 805.0 | SP500 |
| MU | Micron Technology Inc. | US | Information Technology | Semiconductors | 768.0 | SP500+NDX |
| AMD | Advanced Micro Devices Inc. | US | Information Technology | Semiconductors | 686.0 | SP500+NDX |
| XOM | Exxon Mobil Corporation | US | Energy | Oil Gas & Consumable Fuels | 665.0 | SP500 |
| V | Visa Inc. | US | Financials | Financial Services | 626.0 | SP500 |
| ASML | ASML Holding N.V. | US | Information Technology | Semiconductor Equipment | 597.0 | NDX_ADR |
| JNJ | Johnson & Johnson | US | Health Care | Pharmaceuticals | 551.0 | SP500 |
| INTC | Intel Corporation | US | Information Technology | Semiconductors | 543.0 | SP500+NDX |
| ORCL | Oracle Corporation | US | Information Technology | Software | 536.0 | SP500 |
| COST | Costco Wholesale Corporation | US | Consumer Staples | Consumer Staples Distribution | 477.0 | SP500+NDX |
| CSCO | Cisco Systems Inc. | US | Information Technology | Communications Equipment | 469.0 | SP500+NDX |
| MA | Mastercard Incorporated | US | Financials | Financial Services | 446.0 | SP500 |
| CAT | Caterpillar Inc. | US | Industrials | Machinery | 397.0 | SP500 |
| CVX | Chevron Corporation | US | Energy | Oil Gas & Consumable Fuels | 387.0 | SP500 |
| NFLX | Netflix Inc. | US | Communication Services | Entertainment | 377.0 | SP500+NDX |
| ABBV | AbbVie Inc. | US | Health Care | Biotechnology | 369.0 | SP500 |
| BAC | Bank of America Corporation | US | Financials | Banks | 359.0 | SP500 |
| UNH | UnitedHealth Group Incorporated | US | Health Care | Health Care Providers | 355.0 | SP500 |
| KO | The Coca-Cola Company | US | Consumer Staples | Beverages | 349.0 | SP500 |
| LRCX | Lam Research Corporation | US | Information Technology | Semiconductor Equipment | 347.0 | SP500+NDX |
| PG | The Procter & Gamble Company | US | Consumer Staples | Household Products | 331.0 | SP500 |
| AMAT | Applied Materials Inc. | US | Information Technology | Semiconductor Equipment | 328.0 | SP500+NDX |
| PLTR | Palantir Technologies Inc. | US | Information Technology | Software | 323.0 | SP500+NDX |
| MS | Morgan Stanley | US | Financials | Capital Markets | 303.0 | SP500 |
| HD | The Home Depot Inc. | US | Consumer Discretionary | Specialty Retail | 298.0 | SP500 |
| PM | Philip Morris International Inc. | US | Consumer Staples | Tobacco | 298.0 | SP500 |
| GE | GE Aerospace | US | Industrials | Aerospace & Defense | 298.0 | SP500 |
| GS | The Goldman Sachs Group Inc. | US | Financials | Capital Markets | 290.0 | SP500 |
| MRK | Merck & Co. Inc. | US | Health Care | Pharmaceuticals | 278.0 | SP500 |
| TXN | Texas Instruments Incorporated | US | Information Technology | Semiconductors | 273.0 | SP500+NDX |
| GEV | GE Vernova Inc. | US | Industrials | Electrical Equipment | 272.0 | SP500 |
| RTX | RTX Corporation | US | Industrials | Aerospace & Defense | 236.0 | SP500 |
| LIN | Linde plc | US | Materials | Chemicals | 236.0 | SP500+NDX |
| ARM | Arm Holdings plc | US | Information Technology | Semiconductors | 235.0 | NDX_ADR |
| KLAC | KLA Corporation | US | Information Technology | Semiconductor Equipment | 229.0 | SP500+NDX |
| WFC | Wells Fargo & Company | US | Financials | Banks | 227.0 | SP500 |
| QCOM | QUALCOMM Incorporated | US | Information Technology | Semiconductors | 214.0 | SP500+NDX |
| AXP | American Express Company | US | Financials | Consumer Finance | 213.0 | SP500 |
| IBM | IBM Corporation | US | Information Technology | IT Services | 209.0 | SP500 |
| C | Citigroup Inc. | US | Financials | Banks | 208.0 | SP500 |
| TMUS | T-Mobile US Inc. | US | Communication Services | Wireless Telecommunication | 206.0 | SP500+NDX |
| ADI | Analog Devices Inc. | US | Information Technology | Semiconductors | 204.0 | SP500+NDX |
| PEP | PepsiCo Inc. | US | Consumer Staples | Beverages | 203.0 | SP500+NDX |
| PANW | Palo Alto Networks Inc. | US | Information Technology | Software | 200.0 | SP500+NDX |
| MCD | McDonald's Corporation | US | Consumer Discretionary | Hotels Restaurants | 200.0 | SP500 |
| SNDK | Sandisk Corporation | US | Information Technology | Technology Hardware, Storage & Peripherals | 197.0 | SP500+NDX_NEW_APR2026; sub_industry_corrected_v0_2 |
| VZ | Verizon Communications Inc. | US | Communication Services | Diversified Telecommunication | 195.0 | SP500 |
| NEE | NextEra Energy Inc. | US | Utilities | Electric Utilities | 185.0 | SP500 |
| DIS | The Walt Disney Company | US | Communication Services | Entertainment | 180.0 | SP500 |
| ANET | Arista Networks Inc. | US | Information Technology | Communications Equipment | 178.0 | SP500 |
| BLK | BlackRock Inc. | US | Financials | Capital Markets | 176.0 | SP500 |
| AMGN | Amgen Inc. | US | Health Care | Biotechnology | 175.0 | SP500+NDX |
| BA | The Boeing Company | US | Industrials | Aerospace & Defense | 173.0 | SP500 |
| T | AT&T Inc. | US | Communication Services | Diversified Telecommunication | 169.0 | SP500 |
| TJX | The TJX Companies Inc. | US | Consumer Discretionary | Specialty Retail | 166.0 | SP500 |
| STX | Seagate Technology Holdings plc | US | Information Technology | Technology Hardware | 166.0 | SP500+NDX |
| APP | AppLovin Corporation | US | Information Technology | Software | 165.0 | SP500+NDX |
| TMO | Thermo Fisher Scientific Inc. | US | Health Care | Life Sciences Tools | 164.0 | SP500 |
| UNP | Union Pacific Corporation | US | Industrials | Ground Transportation | 163.0 | SP500 |
| GILD | Gilead Sciences Inc. | US | Health Care | Biotechnology | 160.0 | SP500+NDX |
| SCHW | The Charles Schwab Corporation | US | Financials | Capital Markets | 160.0 | SP500 |
| WDC | Western Digital Corporation | US | Information Technology | Technology Hardware | 158.0 | SP500+NDX |
| CRWD | CrowdStrike Holdings Inc. | US | Information Technology | Software | 157.0 | SP500+NDX |
| ISRG | Intuitive Surgical Inc. | US | Health Care | Health Care Equipment | 155.0 | SP500+NDX |
| MRVL | Marvell Technology Inc. | US | Information Technology | Semiconductors | 155.0 | NDX |
| DELL | Dell Technologies Inc. | US | Information Technology | Technology Hardware | 154.0 | SP500 |
| GLW | Corning Incorporated | US | Information Technology | Electronic Components | 153.0 | SP500 |
| ABT | Abbott Laboratories | US | Health Care | Health Care Equipment | 153.0 | SP500 |
| UBER | Uber Technologies Inc. | US | Industrials | Ground Transportation | 152.0 | SP500 |
| DE | Deere & Company | US | Industrials | Machinery | 152.0 | SP500 |
| COP | ConocoPhillips | US | Energy | Oil Gas & Consumable Fuels | 151.0 | SP500 |
| WELL | Welltower Inc. | US | Real Estate | Health Care REITs | 150.0 | SP500 |
| APH | Amphenol Corporation | US | Information Technology | Electronic Components | 149.0 | SP500 |
| ETN | Eaton Corporation plc | US | Industrials | Electrical Equipment | 148.0 | SP500 |
| CRM | Salesforce Inc. | US | Information Technology | Software | 146.0 | SP500 |
| PFE | Pfizer Inc. | US | Health Care | Pharmaceuticals | 144.0 | SP500 |
| BX | Blackstone Inc. | US | Financials | Capital Markets | 143.0 | SP500 |
| PDD | PDD Holdings Inc. | US | Consumer Discretionary | Broadline Retail | 141.0 | NDX_ADR |
| HON | Honeywell International Inc. | US | Industrials | Industrial Conglomerates | 137.0 | SP500+NDX |
| PLD | Prologis Inc. | US | Real Estate | Industrial REITs | 135.0 | SP500 |
| VRT | Vertiv Holdings Co | US | Industrials | Electrical Equipment | 130.0 | SP500 |
| CB | Chubb Limited | US | Financials | Insurance | 128.0 | SP500 |
| SPGI | S&P Global Inc. | US | Financials | Capital Markets | 123.0 | SP500 |
| MO | Altria Group Inc. | US | Consumer Staples | Tobacco | 123.0 | SP500 |
| SHOP | Shopify Inc. | US | Information Technology | Software | 123.0 | NDX_ADR |
| CVS | CVS Health Corporation | US | Health Care | Health Care Providers | 122.0 | SP500 |
| LOW | Lowe's Companies Inc. | US | Consumer Discretionary | Specialty Retail | 122.0 | SP500 |
| LMT | Lockheed Martin Corporation | US | Industrials | Aerospace & Defense | 121.0 | SP500 |
| SBUX | Starbucks Corporation | US | Consumer Discretionary | Hotels Restaurants | 121.0 | SP500+NDX |
| BKNG | Booking Holdings Inc. | US | Consumer Discretionary | Hotels Restaurants | 120.0 | SP500+NDX |
| SYK | Stryker Corporation | US | Health Care | Health Care Equipment | 120.0 | SP500 |
| PGR | The Progressive Corporation | US | Financials | Insurance | 119.0 | SP500 |
| NEM | Newmont Corporation | US | Materials | Metals & Mining | 117.0 | SP500 |
| BMY | Bristol-Myers Squibb Company | US | Health Care | Pharmaceuticals | 117.0 | SP500 |
| COF | Capital One Financial Corporation | US | Financials | Consumer Finance | 116.0 | SP500 |
| DHR | Danaher Corporation | US | Health Care | Life Sciences Tools | 115.0 | SP500 |
| INTU | Intuit Inc. | US | Information Technology | Software | 111.0 | SP500+NDX |
| VRTX | Vertex Pharmaceuticals Incorporated | US | Health Care | Biotechnology | 110.0 | SP500+NDX |
| CME | CME Group Inc. | US | Financials | Capital Markets | 110.0 | SP500+NDX |
| ACN | Accenture plc | US | Information Technology | IT Services | 109.0 | SP500 |
| PWR | Quanta Services Inc. | US | Industrials | Construction & Engineering | 108.0 | SP500 |
| PH | Parker-Hannifin Corporation | US | Industrials | Machinery | 108.0 | SP500 |
| NOW | ServiceNow Inc. | US | Information Technology | Software | 106.0 | SP500 |
| SO | The Southern Company | US | Utilities | Electric Utilities | 105.0 | SP500 |
| EQIX | Equinix Inc. | US | Real Estate | Specialized REITs | 104.0 | SP500+NDX |
| ADBE | Adobe Inc. | US | Information Technology | Software | 103.0 | SP500+NDX |
| HWM | Howmet Aerospace Inc. | US | Industrials | Aerospace & Defense | 102.0 | SP500 |
| TT | Trane Technologies plc | US | Industrials | Building Products | 101.0 | SP500 |

- Note: Shared source alone is not proof of batch error.

## 8. Cause Candidates
- A. Single-row input issue: evidence=the SNDK and INTC values are consistent across universe/audit/sample; likelihood=Medium
- B. Unit conversion issue: evidence=US rows generally use USD_B and no broad KRW-style conversion pattern is visible here; likelihood=Low
- C. Source batch issue: evidence=SNDK has recent/corrected source text and INTC belongs to a broad SP500+NDX source group; likelihood=Medium
- D. Sample extraction issue: evidence=sample values match source rows; likelihood=Low
- E. Audit calculation issue: evidence=audit values match universe values; likelihood=Low
- F. External data timing/reference conflict: evidence=this report uses only local CSV metadata plus stated sanity references; likelihood=Unclear
- G. Unclear: evidence=external source/date comparison is still needed; likelihood=Medium
- Final decision belongs to user/GPT/Claude review.

## 9. Impact Scope
- SNDK/INTC only or broader: SNDK and INTC are the named targets; outlier tables show additional metadata review candidates.
- Impact on CORE/EXTENDED classification: possible for cap-threshold-sensitive rows, especially SNDK.
- Impact on HIGH_RISK_REVIEW classification: possible for ordering and priority; INTC role is also tied to turnaround_flag=Y.
- Impact on Step 3 sample confidence: sample extraction logic remains consistent, but cap metadata review remains open.
- Impact on universe_quality_audit v0.1 confidence: role/risk output remains traceable to input metadata; cap-dependent boundary cases need review.

## 10. Recommended Next Step
- Do not modify universe_master.csv yet.
- Do not modify audit CSV.
- Do not modify step3_samples_v0_1.csv.
- Commit should be delayed until GPT/Claude review.
- External reference conflict for SNDK/INTC should be treated as NEED_DATA, not confirmed error.
- Next review should decide whether this report and step3_samples_v0_1.csv are commit-ready.

## 11. Git Status
- git status -sb:
```text
## main...origin/main
?? backups/
?? reports/step3_samples_v0_1.csv
?? reports/step3c_metadata_diagnosis_v0_1.md
```
- git status --short:
```text
?? backups/
?? reports/step3_samples_v0_1.csv
?? reports/step3c_metadata_diagnosis_v0_1.md
```
- git add status: NO
- commit status: NO
- push status: NO
