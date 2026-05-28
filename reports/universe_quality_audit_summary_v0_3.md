# universe_quality_audit v0.3

## 1. 작업 목적
2026-05-27 현재 시점에서 1군 / 2군 / MANUAL_REVIEW 후보군 분류의 전처리 필터를 Gate 3 기준으로 보정한다.

## 2. 작업 성격
전처리 필터 재설계이며, 백테스트가 아니다.

## 3. 평가 시점
- as_of_date: 2026-05-27
- yfinance 수집 기간: 2025-03-01 ~ 2026-05-27

## 4. 봉인 문서 기준 확인
- 기준 문서: docs\paradigm\maesoo_v2_paradigm_v1_5_1_RC_FULL.md
- Gate 3 Recovery Track / Continuation Track / 최종 판정 로직을 기준으로 사용했다.

## 5. v0.1 audit 문제 요약
- v0.1은 `turnaround_flag == Y`를 `HIGH_RISK_REVIEW`로 고정 매핑했다.
- v0.1 validation은 `turnaround_flag == Y and CORE`를 `turnaround CORE violation`으로 실패 처리했다.
- v0.3에서는 turnaround를 위험 딱지가 아니라 Recovery Track 검증 입력값으로 사용한다.

## 6. v0.3 변경 요약
- `turnaround_flag == Y` 고정 HIGH_RISK_REVIEW 매핑을 제거했다.
- turnaround CORE validation 실패 규칙을 제거했다.
- Gate 3 Recovery / Continuation 수치를 yfinance 가격/거래량으로 계산했다.
- 비-turnaround 종목은 Gate 3 수치만 기록하고 v0.3 role/action은 v0.1을 유지했다.
- 최소 패치: legacy EXCLUDE_CANDIDATE 중 turnaround와 독립적인 EXCLUDE 사유가 있는 종목은 EXCLUDE_CANDIDATE를 유지한다.
- 최소 패치: Gate3 final == FAIL인 turnaround 종목은 MANUAL_REVIEW가 아니라 GATE3_FAIL_REVIEW로 분리한다.

## 7. 파일럿 5종목 결과
- 파일럿 성공 수: 5 / 5
- 파일럿 통과 여부: PASS
| ticker | price_data_source | price_data_asof | recovery | continuation | final | ra | rb | rc | rd | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | yfinance | 2026-05-27 | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | Y |  |
| BA | yfinance | 2026-05-27 | FAIL | FAIL | FAIL | N | Y | N | N |  |
| SBUX | yfinance | 2026-05-27 | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | N |  |
| DIS | yfinance | 2026-05-27 | FAIL | FAIL | FAIL | N | N | N | N |  |
| F | yfinance | 2026-05-27 | FAIL | FAIL | FAIL | N | Y | N | Y |  |

## 8. 입력 파일 SHA256 before/after
| file | before | after | unchanged |
| --- | --- | --- | --- |
| .github\workflows\main.yml | 162deab006d33f669bbbcb74e07d1a66867ca86438617168a371308cfa82a78a | 162deab006d33f669bbbcb74e07d1a66867ca86438617168a371308cfa82a78a | True |
| docs\paradigm\maesoo_v2_paradigm_v1_5_1_RC_FULL.md | 236c617e85ece5607c2fca49182040bbdd14e38c611e7a80cf5e81e8e33216f9 | 236c617e85ece5607c2fca49182040bbdd14e38c611e7a80cf5e81e8e33216f9 | True |
| reports\backtest_it_2026q1_data_v0_1.csv | 4684644cd2fa29e689126665db39700f75f9561c1c55d47104515510e76f785b | 4684644cd2fa29e689126665db39700f75f9561c1c55d47104515510e76f785b | True |
| reports\universe_quality_audit_summary_v0_1.md | bd6cb3ba5ec5c657ebaf94338e67dfd0f40da531a38cc1c0cb7945aea003a20f | bd6cb3ba5ec5c657ebaf94338e67dfd0f40da531a38cc1c0cb7945aea003a20f | True |
| reports\universe_quality_audit_v0_1.csv | 19b282cfef8639eefcbe8c10a6563bd8591b590dde733fda4ce35ba889c6278c | 19b282cfef8639eefcbe8c10a6563bd8591b590dde733fda4ce35ba889c6278c | True |
| run_daily_report.py | 37e7bf854a8e1fc3a68abdf0dceb1fd398e8f39a55aedcac534c61fab95807f8 | 37e7bf854a8e1fc3a68abdf0dceb1fd398e8f39a55aedcac534c61fab95807f8 | True |
| scorer.py | 49a15e082d6b1fe4fc67b6a3dc72a8a7633d4e154364c4946b2e513b62b9d1d5 | 49a15e082d6b1fe4fc67b6a3dc72a8a7633d4e154364c4946b2e513b62b9d1d5 | True |
| scripts\audit_universe_quality.py | 84a1f621c3e109cc6331a079a12c8b97424e1e0dafd4aa6de2f14e428ef5c53a | 84a1f621c3e109cc6331a079a12c8b97424e1e0dafd4aa6de2f14e428ef5c53a | True |
| telegram_reporter.py | 496eea14d9782f8a00584ecdca99923b366df1fd9e5b031d8b341e2c0f2a8b6d | 496eea14d9782f8a00584ecdca99923b366df1fd9e5b031d8b341e2c0f2a8b6d | True |
| universe_master.csv | f63cb35738ae059d23de450f73c320a25b05cc4ebdd5553b41801181a480f499 | f63cb35738ae059d23de450f73c320a25b05cc4ebdd5553b41801181a480f499 | True |

- git HEAD unchanged during run: True

## 9. 기존 v0.1 산출물 미수정 확인
- v0.1 audit CSV/summary unchanged: True

## 9A. 최소 패치 결과
- BAX 같은 복합 EXCLUDE는 legacy EXCLUDE_CANDIDATE를 보존한다.
- Gate3 FAIL 종목은 MANUAL_REVIEW가 아니라 GATE3_FAIL_REVIEW로 분리한다.
| ticker | legacy_role | v0_3_role | v0_3_action | gate3_final | v0_3_reason |
| --- | --- | --- | --- | --- | --- |
| BAX | EXCLUDE_CANDIDATE | EXCLUDE_CANDIDATE | EXCLUSION_REVIEW | FAIL | legacy EXCLUDE preserved due to non-turnaround exclusion reasons; turnaround_flag used as Recovery Track input only; legacy_reason=TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |

### Gate3 FAIL turnaround role 분포
| v0_3_universe_role | count |
| --- | --- |
| EXCLUDE_CANDIDATE | 1 |
| GATE3_FAIL_REVIEW | 12 |


## 10. v0.3 생성 파일 목록
- scripts\audit_universe_quality_v0_3.py
- reports\universe_quality_audit_v0_3.csv
- reports\universe_quality_audit_summary_v0_3.md
- tests\test_audit_universe_quality_v0_3.py

## 11. 대상 종목 수
- universe_master rows: 656
- audit rows: 656
- turnaround_flag == Y rows: 17

## 12. 가격 데이터 성공/실패 수
- success: 654
- failure_or_insufficient: 2
| ticker | name | price_data_source | notes |
| --- | --- | --- | --- |
| MMC | Marsh & McLennan Companies Inc. | yfinance_failed | INSUFFICIENT_GATE3_DATA; empty price dataframe |
| Q | Qnity Electronics Inc. | yfinance_failed | INSUFFICIENT_GATE3_DATA; insufficient rows for 52w window: 146 |

## 13. Gate 3 Recovery 분포
| status | count |
| --- | --- |
| PASS | 15 |
| FAIL | 639 |
| MANUAL_REVIEW | 0 |
| INSUFFICIENT_DATA | 2 |

## 14. Gate 3 Continuation 분포
| status | count |
| --- | --- |
| PASS | 0 |
| FAIL | 615 |
| MANUAL_REVIEW | 0 |
| INSUFFICIENT_DATA | 41 |

## 15. Gate 3 Final 분포
| status | count |
| --- | --- |
| PASS | 15 |
| FAIL | 600 |
| MANUAL_REVIEW | 39 |
| INSUFFICIENT_DATA | 2 |

## 16. v0.1 대비 role/action 변경 종목 목록
| ticker | name | legacy_role | legacy_action | v0_3_role | v0_3_action | gate3_final | v0_3_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | MANUAL_REVIEW | MANUAL_REVIEW | MANUAL_REVIEW | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| DIS | The Walt Disney Company | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| BA | The Boeing Company | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| PFE | Pfizer Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| CVS | CVS Health Corporation | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | MANUAL_REVIEW | MANUAL_REVIEW | MANUAL_REVIEW | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| SBUX | Starbucks Corporation | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | MANUAL_REVIEW | MANUAL_REVIEW | MANUAL_REVIEW | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| WBD | Warner Bros. Discovery Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| GM | General Motors Company | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| NKE | NIKE Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| TGT | Target Corporation | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| F | Ford Motor Company | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| PYPL | PayPal Holdings Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| EL | The Estée Lauder Companies Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| BIIB | Biogen Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | MANUAL_REVIEW | MANUAL_REVIEW | MANUAL_REVIEW | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=HIGH_RISK_REVIEW; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| MRNA | Moderna Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=HIGH_RISK_REVIEW; recovery=FAIL; continuation=FAIL |
| SMCI | Super Micro Computer Inc. | HIGH_RISK_REVIEW | REVIEW_BEFORE_SCORING | GATE3_FAIL_REVIEW | REVIEW_BEFORE_SCORING | FAIL | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |

## 17. turnaround_flag == Y 종목 spotlight
| ticker | name | legacy_v0_1_universe_role | v0_3_universe_role | gate3_recovery_status | gate3_continuation_status | gate3_final_status | ra_pass | rb_pass | rc_pass | rd_pass | v0_3_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | Y | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| DIS | The Walt Disney Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | N | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| BA | The Boeing Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| PFE | Pfizer Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | N | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| CVS | CVS Health Corporation | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | Y | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| SBUX | Starbucks Corporation | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | N | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| WBD | Warner Bros. Discovery Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| GM | General Motors Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| NKE | NIKE Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | N | N | Y | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| TGT | Target Corporation | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| F | Ford Motor Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | N | Y | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| PYPL | PayPal Holdings Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | N | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| EL | The Estée Lauder Companies Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | Y | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| BIIB | Biogen Inc. | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | N | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=HIGH_RISK_REVIEW; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| MRNA | Moderna Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=HIGH_RISK_REVIEW; recovery=FAIL; continuation=FAIL |
| SMCI | Super Micro Computer Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | Y | N | Y | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| BAX | Baxter International Inc. | EXCLUDE_CANDIDATE | EXCLUDE_CANDIDATE | FAIL | FAIL | FAIL | Y | Y | N | N | legacy EXCLUDE preserved due to non-turnaround exclusion reasons; turnaround_flag used as Recovery Track input only; legacy_reason=TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |

## 18. 지정 spotlight
| ticker | name | legacy_v0_1_universe_role | v0_3_universe_role | gate3_recovery_status | gate3_continuation_status | gate3_final_status | ra_pass | rb_pass | rc_pass | rd_pass | v0_3_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTC | Intel Corporation | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | Y | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| BA | The Boeing Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| SBUX | Starbucks Corporation | HIGH_RISK_REVIEW | MANUAL_REVIEW | FAIL | INSUFFICIENT_DATA | MANUAL_REVIEW | N | Y | Y | N | Gate 3 MANUAL_REVIEW; no arbitrary classification; metadata_role=CORE; recovery=FAIL; continuation=INSUFFICIENT_DATA |
| PFE | Pfizer Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | N | Y | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| SMCI | Super Micro Computer Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | Y | N | Y | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| DIS | The Walt Disney Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | N | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| PYPL | PayPal Holdings Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | N | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| F | Ford Motor Company | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | N | Y | N | Y | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=CORE; recovery=FAIL; continuation=FAIL |
| EL | The Estée Lauder Companies Inc. | HIGH_RISK_REVIEW | GATE3_FAIL_REVIEW | FAIL | FAIL | FAIL | Y | Y | N | N | Gate3 FAIL; no recovery/continuation signal; preprocessing review only, not EXCLUDE; metadata_role=EXTENDED; recovery=FAIL; continuation=FAIL |
| BAX | Baxter International Inc. | EXCLUDE_CANDIDATE | EXCLUDE_CANDIDATE | FAIL | FAIL | FAIL | Y | Y | N | N | legacy EXCLUDE preserved due to non-turnaround exclusion reasons; turnaround_flag used as Recovery Track input only; legacy_reason=TURNAROUND_IN_PROGRESS; MARKET_CAP_BELOW_THRESHOLD; NO_FINANCIAL_DATA_AVAILABLE; turnaround healthcare row below 10B metadata threshold |

## 19. 비-turnaround 종목 Gate 3 수치 기록 여부
- non-turnaround rows: 639
- non-turnaround role changes: 0
- non-turnaround rows with yfinance price data: 637

## 20. 운영 코드 미수정 확인
- protected input hashes unchanged: True
- checked files: scorer.py, telegram_reporter.py, .github/workflows/main.yml, run_daily_report.py

## 21. 기존 reports 호환성 보존 확인
본 v0.3 audit은 2026-05-27 현재 시점 전처리 필터 재설계 결과다. 1월~4월 월별 백테스트 결과와 직접 비교할 때는 평가 시점 차이를 주의해야 한다. 기존 step3/backtest/track_c 산출물은 v0.1 기준 검증 기록으로 보존한다.

## 22. 테스트 결과 기록
- 명령: `python -m unittest tests.test_audit_universe_quality_v0_3`
- 결과: PASS

## 23. 다음 단계
Claude 반례 검증 + 사용자 판정
