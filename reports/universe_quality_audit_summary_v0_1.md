# universe_quality_audit v0.1

## 1. 작업 목적
현재 universe_master.csv v0.2의 전체 종목을 같은 core 후보로 보지 않도록 메타데이터 기반 1차 위험 분류를 생성한다.

## 2. 입력 파일 정보
- 입력 파일: universe_master.csv
- 입력 row 수: 656
- 출력 CSV: C:/Users/yy225/OneDrive/문서/finviz_bot/reports/universe_quality_audit_v0_1.csv

## 3. 전체 종목 수
- 656

## 4. market별 종목 수
| market | count |
| --- | --- |
| KR | 102 |
| US | 554 |

## 5. universe_role별 종목 수
| universe_role | count |
| --- | --- |
| CORE | 255 |
| DISCOVERY_ONLY | 16 |
| EXCLUDE_CANDIDATE | 1 |
| EXTENDED | 343 |
| HIGH_RISK_REVIEW | 41 |

## 6. quality_risk_level별 종목 수
| quality_risk_level | count |
| --- | --- |
| LOW | 255 |
| MEDIUM | 343 |
| HIGH | 57 |
| VERY_HIGH | 1 |

## 7. HIGH_RISK_REVIEW 상위 30개 목록
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | 543.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| DIS | The Walt Disney Company | 180.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BA | The Boeing Company | 173.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PFE | Pfizer Inc. | 144.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| CVS | CVS Health Corporation | 122.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| SBUX | Starbucks Corporation | 121.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| WBD | Warner Bros. Discovery Inc. | 67.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| GM | General Motors Company | 65.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| REGN | Regeneron Pharmaceuticals Inc. | 64.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; METADATA_ONLY_AUDIT; mid-large biotechnology row needs review before scoring |
| NKE | NIKE Inc. | 63.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| TGT | Target Corporation | 56.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| F | Ford Motor Company | 51.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PYPL | PayPal Holdings Inc. | 39.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| ALNY | Alnylam Pharmaceuticals Inc. | 38.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; METADATA_ONLY_AUDIT; mid-large biotechnology row needs review before scoring |
| EL | The Estée Lauder Companies Inc. | 28.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BIIB | Biogen Inc. | 28.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| INSM | Insmed Incorporated | 25.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; biotechnology row below 30B metadata threshold |
| MRNA | Moderna Inc. | 19.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| INCY | Incyte Corporation | 19.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; biotechnology row below 30B metadata threshold |
| SMCI | Super Micro Computer Inc. | 18.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| 247540.KQ | 에코프로비엠 | 15.4 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 086520.KQ | 에코프로 | 14.3 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;HOLDING_COMPANY;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 196170.KQ | 알테오젠 | 14.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 277810.KQ | 레인보우로보틱스 | 10.7 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| HSIC | Henry Schein Inc. | 8.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| 036930.KQ | 주성엔지니어링 | 7.8 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| CRL | Charles River Laboratories International Inc. | 7.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| TECH | Bio-Techne Corporation | 7.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| 950160.KQ | 코오롱티슈진 | 6.6 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 000250.KQ | 삼천당제약 | 6.1 | HIGH_RISK_REVIEW | HIGH | PHARMA_EVENT_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | PHARMA_EVENT_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |

## 8. DISCOVERY_ONLY 목록
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| 032640.KS | LG유플러스 | 4.8 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 241560.KS | 두산밥캣 | 4.7 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 336260.KS | 두산퓨얼셀 | 4.7 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 004020.KS | 현대제철 | 4.0 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 088980.KS | 맥쿼리인프라 | 3.8 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 018880.KS | 한온시스템 | 3.8 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 222800.KQ | 심텍 | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 095340.KQ | ISC | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 178320.KQ | 서진시스템 | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 108490.KQ | 로보티즈 | 3.3 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| LPL | LG Display Co. Ltd. ADR | 3 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK;ADR_FOREIGN_LISTING | MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 251270.KS | 넷마블 | 2.5 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 097950.KS | CJ제일제당 | 2.3 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 004990.KS | 롯데지주 | 1.9 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK;HOLDING_COMPANY | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 139480.KS | 이마트 | 1.8 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |
| 009450.KS | 경동나비엔 | 0.7 | DISCOVERY_ONLY | HIGH | SMALL_CAP_RISK | SMALL_CAP_KOREA; METADATA_ONLY_AUDIT; market cap metadata below core threshold |

## 9. EXCLUDE_CANDIDATE 목록
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| BAX | Baxter International Inc. | 9.0 | EXCLUDE_CANDIDATE | VERY_HIGH | TURNAROUND_RISK;SMALL_CAP_RISK;DATA_LIMITATION;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |

## 10. 한국 KOSDAQ 종목 분류 결과
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| 247540.KQ | 에코프로비엠 | 15.4 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 086520.KQ | 에코프로 | 14.3 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;HOLDING_COMPANY;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 196170.KQ | 알테오젠 | 14.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 277810.KQ | 레인보우로보틱스 | 10.7 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 036930.KQ | 주성엔지니어링 | 7.8 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 950160.KQ | 코오롱티슈진 | 6.6 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 000250.KQ | 삼천당제약 | 6.1 | HIGH_RISK_REVIEW | HIGH | PHARMA_EVENT_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | PHARMA_EVENT_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 058470.KQ | 리노공업 | 6.0 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 028300.KQ | HLB | 5.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 039030.KQ | 이오테크닉스 | 4.8 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 298380.KQ | 에이비엘바이오 | 4.7 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 087010.KQ | 펩트론 | 4.5 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 240810.KQ | 원익IPS | 4.3 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 440110.KQ | 파두 | 4.2 | HIGH_RISK_REVIEW | HIGH | KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_TOP15_RISK; SECTOR_VOLATILITY; METADATA_ONLY_AUDIT; KOSDAQ top15 sector-volatility marker prevents core classification |
| 141080.KQ | 리가켐바이오 | 4.1 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 222800.KQ | 심텍 | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 108490.KQ | 로보티즈 | 3.3 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 310210.KQ | 보로노이 | 3.6 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_THEME_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_THEME_SLOT; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 095340.KQ | ISC | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |
| 178320.KQ | 서진시스템 | 3.6 | DISCOVERY_ONLY | HIGH | KOSDAQ_THEME_RISK;SMALL_CAP_RISK;SECTOR_VOLATILITY | KOSDAQ_THEME_SLOT; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; theme-slot row retained for discovery monitoring only |

## 11. 바이오/제약 리스크 종목 목록
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| PFE | Pfizer Inc. | 144.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| CVS | CVS Health Corporation | 122.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| REGN | Regeneron Pharmaceuticals Inc. | 64.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; METADATA_ONLY_AUDIT; mid-large biotechnology row needs review before scoring |
| ALNY | Alnylam Pharmaceuticals Inc. | 38.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; METADATA_ONLY_AUDIT; mid-large biotechnology row needs review before scoring |
| BIIB | Biogen Inc. | 28.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| INSM | Insmed Incorporated | 25.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; biotechnology row below 30B metadata threshold |
| MRNA | Moderna Inc. | 19.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| INCY | Incyte Corporation | 19.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; biotechnology row below 30B metadata threshold |
| 196170.KQ | 알테오젠 | 14.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| BAX | Baxter International Inc. | 9.0 | EXCLUDE_CANDIDATE | VERY_HIGH | TURNAROUND_RISK;SMALL_CAP_RISK;DATA_LIMITATION;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |
| HSIC | Henry Schein Inc. | 8.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| CRL | Charles River Laboratories International Inc. | 7.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| TECH | Bio-Techne Corporation | 7.0 | HIGH_RISK_REVIEW | HIGH | HEALTHCARE_EVENT_RISK | SECTOR_VOLATILITY; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; sub-10B metadata row needs review before scoring |
| 950160.KQ | 코오롱티슈진 | 6.6 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 000250.KQ | 삼천당제약 | 6.1 | HIGH_RISK_REVIEW | HIGH | PHARMA_EVENT_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | PHARMA_EVENT_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 028300.KQ | HLB | 5.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 000100.KS | 유한양행 | 4.9 | HIGH_RISK_REVIEW | HIGH | PHARMA_EVENT_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | PHARMA_EVENT_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; pharmaceutical row below 10B metadata threshold |
| 298380.KQ | 에이비엘바이오 | 4.7 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 087010.KQ | 펩트론 | 4.5 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 128940.KS | 한미약품 | 4.3 | HIGH_RISK_REVIEW | HIGH | PHARMA_EVENT_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | PHARMA_EVENT_RISK; MARKET_CAP_BELOW_THRESHOLD; METADATA_ONLY_AUDIT; pharmaceutical row below 10B metadata threshold |
| 141080.KQ | 리가켐바이오 | 4.1 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_TOP15_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_TOP15_RISK; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |
| 310210.KQ | 보로노이 | 3.6 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;KOSDAQ_THEME_RISK;SMALL_CAP_RISK;HEALTHCARE_EVENT_RISK | BIOTECH_CLINICAL_RISK; KOSDAQ_THEME_SLOT; METADATA_ONLY_AUDIT; KOSDAQ healthcare row requires event-risk review |

## 12. turnaround_flag == Y 종목 분류 결과
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | 543.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| DIS | The Walt Disney Company | 180.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BA | The Boeing Company | 173.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PFE | Pfizer Inc. | 144.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| CVS | CVS Health Corporation | 122.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| SBUX | Starbucks Corporation | 121.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| WBD | Warner Bros. Discovery Inc. | 67.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| GM | General Motors Company | 65.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| NKE | NIKE Inc. | 63.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| TGT | Target Corporation | 56.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| F | Ford Motor Company | 51.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| PYPL | PayPal Holdings Inc. | 39.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| EL | The Estée Lauder Companies Inc. | 28.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BIIB | Biogen Inc. | 28.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| MRNA | Moderna Inc. | 19.0 | HIGH_RISK_REVIEW | HIGH | BIOTECH_RISK;TURNAROUND_RISK;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| SMCI | Super Micro Computer Inc. | 18.0 | HIGH_RISK_REVIEW | HIGH | TURNAROUND_RISK | TURNAROUND_IN_PROGRESS; METADATA_ONLY_AUDIT; turnaround flag prevents core classification |
| BAX | Baxter International Inc. | 9.0 | EXCLUDE_CANDIDATE | VERY_HIGH | TURNAROUND_RISK;SMALL_CAP_RISK;DATA_LIMITATION;HEALTHCARE_EVENT_RISK | TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |

## 13. CORE로 분류된 종목 수
- 255

## 14. 대형 제약사 중 자동 HIGH_RISK_REVIEW로 보내지 않은 종목 목록
| ticker | name | market_cap_usd_b | role | risk | flags | reason |
| --- | --- | --- | --- | --- | --- | --- |
| LLY | Eli Lilly and Company | 881.0 | CORE | LOW | NONE | METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| JNJ | Johnson & Johnson | 551.0 | CORE | LOW | NONE | METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| MRK | Merck & Co. Inc. | 278.0 | CORE | LOW | NONE | METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| NVS | Novartis AG | 250.0 | CORE | LOW | ADR_FOREIGN_LISTING | ADR_LISTING_RISK; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| AZN | AstraZeneca PLC | 230.0 | CORE | LOW | ADR_FOREIGN_LISTING | ADR_LISTING_RISK; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| NVO | Novo Nordisk A/S | 180.0 | CORE | LOW | ADR_FOREIGN_LISTING | ADR_LISTING_RISK; METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |
| BMY | Bristol-Myers Squibb Company | 117.0 | CORE | LOW | NONE | METADATA_ONLY_AUDIT; large-cap metadata row without forced review marker |

## 15. 주의 문구
- 이 audit은 재무 데이터 기반 최종 검증이 아니다.
- 메타데이터 기반 1차 위험 분류다.
- 매수/추천 판단이 아니다.
- Step 3 이전 선별 보조 자료다.

## 16. 생성 기준 메모
- 외부 데이터 조회 없이 universe_master.csv의 기존 컬럼만 사용했다.
- EXCLUDE_CANDIDATE는 삭제가 아니라 별도 검토 대상으로 표시한 것이다.
- audit row 수와 입력 row 수 일치: True
