# standard Gate2 final formula v0.1.2 — 설계 봉인 문서

**봉인 일자:** 2026-05-29
**상태:** 설계 PASS (Claude 3라운드 적대적 검증 + GPT 합의)
**범위:** PASS_FULL을 산출하는 표준 Gate2 산식
**상위 봉인 문서:** maesoo_v2_paradigm_v1_5_1_RC_FULL.md
**연결 봉인 문서:** gate2_recovery_profile_v0_1_2.md

---

## 1. 정체성

standard Gate2는 매수사냥개 4대 게이트 중 게이트 2(검증 가능한 상승 촉매)의 표준 판정식이다. **PASS_FULL을 산출하는 유일한 경로**이며, Gate2-Recovery-profile은 별도의 제한 판정 경로다.

### 관계
- **standard Gate2** → PASS_FULL 또는 MANUAL_REVIEW_DEFERRED_RECOVERY 산출
- **Gate2-Recovery-profile** → PASS_RECOVERY_PROFILE 산출 (deferred handoff 후속)
- **tier_classification**: 1군 = PASS_FULL only / 2군 = 둘 다 허용

---

## 2. 검증 이력

| 버전 | 잔여 | 결과 |
|---|---|---|
| v0.1 | 7개 잔여 (라우팅 모순, Recovery dead code 등) | CONDITIONAL |
| v0.1.1 | 6개 닫힘, 3개 잔여 (deferred 순서, data_unit_error 출처, 보조 FAIL 비대칭) | CONDITIONAL |
| v0.1.2 | 잔여 3개 닫힘, 새 누수 없음, 상태기계 폐포 확보 | **PASS** |

### v0.1.2에서 마지막으로 닫힌 3개
1. deferred recovery handoff를 generic INSUFFICIENT_DATA 앞으로 이동 (dead code 차단)
2. `data_unit_error` bool 폐기 → `data_unit_validation_status` enum 도입
3. PASS_FULL AND 체인에 `earnings_trend_status != FAIL AND analyst_estimate_status != FAIL` 추가 (보조 컴포넌트 FAIL 비대칭 차단)

---

## 3. standard Gate2 Output Enum

```
standard_gate2_output ∈ {
  PASS_FULL,
  FAIL,
  INSUFFICIENT_DATA,
  MANUAL_REVIEW,
  MANUAL_REVIEW_DEFERRED_RECOVERY
}
```

**주의:**
- `PASS_RECOVERY_PROFILE`은 standard Gate2 output이 아니다 (Gate2-Recovery-profile output)
- `MANUAL_REVIEW_DEFERRED_RECOVERY`는 PASS가 아니라 Recovery-profile 호출 후보 상태

---

## 4. PASS_FULL 공식

다음 14개 조건이 모두 AND로 충족되어야 한다.

```
PASS_FULL only if all are true:

1.  step1_exclusion_required == False
2.  mna_manual_review_required == False
3.  data_unit_validation_status == PASS
4.  source_validation_status == PASS
5.  catalyst_component_status == PASS
6.  cumulative_catalyst_score >= 3.0
7.  positive_component_pass_count >= 2
8.  negative_status == CLEAR_VERIFIED
9.  negative_pressure_ratio < 0.5
10. earnings_trend_status in {PASS, MANUAL_REVIEW}
11. analyst_estimate_status in {PASS, MANUAL_REVIEW}
12. earnings_trend_status != FAIL
13. analyst_estimate_status != FAIL
14. at least one of earnings_trend_status or analyst_estimate_status == PASS
```

### 보조 컴포넌트 조합 매트릭스

| earnings | analyst | PASS_FULL |
|---|---|---|
| PASS | PASS | 가능 |
| PASS | MANUAL_REVIEW | 가능 |
| MANUAL_REVIEW | PASS | 가능 |
| MANUAL_REVIEW | MANUAL_REVIEW | 불가 |
| PASS | FAIL | 불가 |
| FAIL | PASS | 불가 |
| FAIL | MANUAL_REVIEW | 불가 |
| MANUAL_REVIEW | FAIL | 불가 |
| FAIL | FAIL | 불가 (non-pass routing에서 FAIL 처리) |

---

## 5. catalyst mandatory + 2-of-3 원칙

봉인 문서 Part 4 "검증 가능한 상승 촉매" 원칙을 코드로 강제하기 위해 **의도된 보수 강화**를 채택한다.

### 공식
```
positive_component_pass_count =
  count(
    catalyst_component_status == PASS,
    earnings_trend_status == PASS,
    analyst_estimate_status == PASS
  )

PASS_FULL requires:
  catalyst_component_status == PASS
  cumulative_catalyst_score >= 3.0
  positive_component_pass_count >= 2
```

### 강화 이유
- catalyst 없이 earnings + analyst만으로 PASS_FULL은 함정 G(목표가 함정), 함정 D(고점 추격), 함정 F(실적 착시)를 충분히 차단하지 못함
- Gate2의 정체성은 "좋은 실적"이 아니라 "검증 가능한 상승 촉매"
- 따라서 catalyst 필수는 봉인 문서보다 느슨한 해석이 아니라, **봉인 문서 의도의 코드화된 보수 강화**

---

## 6. catalyst_score 이중 출력

catalyst_score_calculator는 두 점수를 동시 산출한다.

### cumulative_catalyst_score
- **용도:** standard Gate2 PASS_FULL 평가
- **정의:** 최근 90일 내 valid positive event의 가중 누적 점수
- **임계값:** 3.0 이상이면 `catalyst_component_status = PASS`

### independent_catalyst_score
- **용도:** Gate2-Recovery-profile 입력
- **정의:** earnings event의 underlying cause와 다른 근원의 material external catalyst 중 가장 강한 단일 event score
- **임계값:** Recovery-profile 측에서 `>= 1.5` 조건

### independent로 인정 가능한 예
- 대형 정부 계약
- 대형 공급 계약
- 공식 정책 직접 수혜
- FDA 승인 + 출시
- 대형 외부 투자
- 명확한 외부 파트너십 + 금액/계약 구조 확인

### independent로 인정하지 않는 예
- earnings beat
- guidance raise 자체
- analyst upgrade
- target price 상향
- estimate revision
- 실적 발표 안의 일반적 경영진 코멘트

**핵심:** 두 점수는 같은 calculator에서 나오지만 정의와 용도가 다르다.

---

## 7. positive event 가중치

### positive_event_category enum
```
IMMEDIATE_REVENUE_CATALYST    base_weight = 2.0
FUNDAMENTAL_CATALYST          base_weight = 1.5
STRATEGIC_CATALYST            base_weight = 1.0
SHAREHOLDER_RETURN_CATALYST   base_weight = 0.5
NOISE                         base_weight = 0.0
```

### source_tier multiplier
```
OFFICIAL       multiplier = 1.0  (SEC, DART, 회사 공시, 공식 IR)
MAJOR_MEDIA    multiplier = 0.8  (Reuters, Bloomberg, WSJ)
GENERAL_NEWS   multiplier = 0.5  (일반 뉴스)
BLOG_SOCIAL    multiplier = 0.3 또는 ignored
```

**BLOG_SOCIAL 단독으로 Gate2 PASS 근거 금지.**

### event_score 계산
```
event_score = base_weight * source_multiplier
```

### valid positive event 조건
- `event_date` 최근 90일 이내
- `event_category != NOISE`
- `source_tier`가 허용 enum 안
- LLM classification 사용 시 enum 안
- LLM `unclear` → ignored
- LLM-only event → ignored
- 최소 1개 OFFICIAL source 또는 2개 independent non-blog sources

### 중복 이벤트
- 같은 사건은 동일 `event_id`로 묶음
- 동일 `event_id`는 **1회만** 점수화
- 여러 출처는 source validation에만 사용
- 중복 보도로 catalyst_score 부풀리기 금지

---

## 8. negative_pressure_ratio

### 공식
```
negative_pressure_ratio = negative_pressure_score / cumulative_catalyst_score
```

### PASS_FULL 조건
```
negative_pressure_ratio < 0.5
```

### 해석
- 부정 이벤트 점수가 호재 누적 점수의 절반 미만이어야 함
- **`negative / (positive + negative)`가 아님**
- 더 보수적인 해석을 채택

### 예시
| cumulative | negative | ratio | 결과 |
|---|---|---|---|
| 3.0 | 1.4 | 0.466 | 허용 가능 |
| 3.0 | 1.5 | 0.500 | FAIL |
| 3.0 | 2.0 | 0.666 | FAIL |

### 주의
- `cumulative_catalyst_score == 0`이면 PASS_FULL 불가능
- ratio 계산은 PASS_FULL 후보에서만 의미 있음
- coverage 부족으로 ratio 계산 불가능 → INSUFFICIENT_DATA 또는 MANUAL_REVIEW

---

## 9. negative event 평가

### negative_status enum
```
CLEAR_VERIFIED         최소 커버리지 충족 + active/material/unresolved 없음
ACTIVE_NEGATIVE        3조건 충족 (FAIL)
MATERIALITY_UNKNOWN    부정 이벤트는 있으나 중요도 불명 (MR)
COVERAGE_UNKNOWN       탐지 커버리지 부족 (MR)
```

### Hard Negative 3조건
```
active == True AND material == True AND unresolved == True
→ negative_status = ACTIVE_NEGATIVE
```

### negative event category 가중치
```
HARD_NEGATIVE              weight = 2.0
  (정부 가격 인하 명령, Medicare 협상, 가이던스 cut, 경쟁사 압도적 성장)
REGULATORY_LITIGATION      weight = 1.5
  (FDA 경고, 반독점 조사, 행정 제재, 환경/안전 소송)
FUNDAMENTAL_NEGATIVE       weight = 1.5
  (어닝 미스, 가이던스 미달, 조정 기준 -5%+)
NOISE_NEGATIVE             weight = 0.5
  (일반 우려, 단순 의견 하향)
```

### negative_pressure_score
최근 90일 내 valid negative event의 weighted score 합산

---

## 10. data_unit_validation_status

### enum
```
data_unit_validation_status ∈ {
  PASS,
  INVALID,
  INSUFFICIENT_DATA,
  MANUAL_REVIEW
}
```

### 산출 위치
- 1차 구현: `catalyst_score_calculator.py`의 event input validation 단계
- 향후 별도 `data_unit_validator.py`로 분리 가능

### 검증 대상
- ADR vs 본주 혼동
- 통화 단위 혼동 (USD / DKK / EUR / JPY / KRW 등)
- 분기 EPS vs 연간 EPS 혼동
- GAAP vs Non-GAAP 혼동
- 이벤트 날짜와 평가 컷오프 불일치
- 회사/티커/시장 단위 불일치
- 한국/미국 market adapter 단위 혼동

### 처리
| 상태 | standard Gate2 output |
|---|---|
| PASS | Gate2 평가 가능 (PASS_FULL/deferred handoff 모두 가능) |
| INVALID | INSUFFICIENT_DATA (회사 자체 FAIL이 아니라 데이터 판정 불가) |
| INSUFFICIENT_DATA | INSUFFICIENT_DATA |
| MANUAL_REVIEW | MANUAL_REVIEW |

### trap J와의 관계
- **trap J**: 이미 식별된 ADR/환율 함정 라벨 (정적)
- **data_unit_validation_status**: Gate2 계산 입력 데이터의 단위 신뢰성 검증 (동적)
- 둘은 같은 것이 아님

---

## 11. earnings_trend_status

### enum
```
earnings_trend_status ∈ {PASS, FAIL, INSUFFICIENT_DATA, MANUAL_REVIEW}
```

### 입력 후보
```
latest_earnings_result      ∈ {BEAT, INLINE, MIXED, MISS, UNKNOWN}
guidance_change             ∈ {RAISED, MAINTAINED, CUT, NO_GUIDANCE, UNKNOWN}
recent_earnings_quality     ∈ {CLEAN, ONE_TIME_GAIN_SUSPECTED, GAAP_NON_GAAP_GAP_HIGH, UNKNOWN}
```

### PASS 조건
PASS only if 둘 중 하나:

**조건 1:**
- `latest_earnings_result == BEAT`
- `guidance_change in {RAISED, MAINTAINED}`
- `recent_earnings_quality == CLEAN`

**조건 2:**
- `latest_earnings_result in {BEAT, INLINE}`
- `guidance_change == RAISED`
- `recent_earnings_quality == CLEAN`

### FAIL 조건
- `guidance_change == CUT`
- OR `latest_earnings_result == MISS`
- OR `recent_earnings_quality == ONE_TIME_GAIN_SUSPECTED` AND earnings beat의 핵심 근거가 일회성 이익

### INSUFFICIENT_DATA 조건
- `latest_earnings_result == UNKNOWN`
- OR `guidance_change == UNKNOWN`
- OR earnings date / report source 없음

### MANUAL_REVIEW 조건
- `latest_earnings_result == BEAT and guidance_change == NO_GUIDANCE`
- OR `latest_earnings_result == INLINE and guidance_change == NO_GUIDANCE`
- OR `latest_earnings_result == MIXED`
- OR `recent_earnings_quality == GAAP_NON_GAAP_GAP_HIGH`
- OR 실적은 좋으나 일회성 가능성이 배제되지 않음

**핵심:** BEAT + NO_GUIDANCE는 PASS가 아니라 MANUAL_REVIEW (보수 처리)

---

## 12. analyst_estimate_status

### enum
```
analyst_estimate_status ∈ {PASS, FAIL, INSUFFICIENT_DATA, MANUAL_REVIEW}
```

### 입력 후보
```
analyst_rating_trend        ∈ {UPGRADE, STABLE_POSITIVE, STABLE_NEUTRAL, DOWNGRADE, UNKNOWN}
eps_revision_trend          ∈ {UP, FLAT, DOWN, UNKNOWN}
revenue_revision_trend      ∈ {UP, FLAT, DOWN, UNKNOWN}
target_price_trap_flag      ∈ {TRUE, FALSE, UNKNOWN}
```

### PASS 조건
- `eps_revision_trend == UP` 또는 `revenue_revision_trend == UP`
- AND `analyst_rating_trend in {UPGRADE, STABLE_POSITIVE}`
- AND `target_price_trap_flag == FALSE`

### FAIL 조건
- `eps_revision_trend == DOWN` AND `revenue_revision_trend == DOWN`
- OR `analyst_rating_trend == DOWNGRADE`
- OR `target_price_trap_flag == TRUE`

### INSUFFICIENT_DATA 조건
- `analyst_rating_trend == UNKNOWN`
- OR `eps_revision_trend == UNKNOWN` AND `revenue_revision_trend == UNKNOWN`

### MANUAL_REVIEW 조건
- analyst 긍정인데 eps/revenue revision DOWN
- OR `target_price_trap_flag == UNKNOWN`
- OR 애널리스트 수 부족
- OR ADR/본주 단위 혼동 가능성

**핵심:** 목표가 자체는 PASS 근거가 아니다. 목표가 상승만으로 PASS 금지.

---

## 13. target_price_trap_flag

### 산출 위치
`analyst_estimate_evaluator` 내부

### TRUE 조건
- `analyst_rating_trend in {UPGRADE, STABLE_POSITIVE}`
- AND target price 또는 consensus sentiment 긍정
- AND `eps_revision_trend == DOWN` 또는 `revenue_revision_trend == DOWN`
- AND 추정치 하향이 일시적 데이터 오류가 아님

### FALSE 조건
- `eps_revision_trend in {UP, FLAT}`
- AND `revenue_revision_trend in {UP, FLAT}`
- AND analyst_rating_trend과 추정치 방향이 충돌하지 않음

### UNKNOWN 조건
- analyst data 부족
- estimate revision data 부족
- ADR/본주/통화 단위 혼동 가능성
- 애널리스트 수 부족

### 관계
- target_price_trap_flag는 함정 G 방어용
- trap_classification.py의 G는 이미 식별된 trap_code 분류일 뿐, target_price_trap_flag를 산출하지 않음

---

## 14. LLM 봉인 규칙

### 허용 LLM classification enum
```
positive
negative
neutral
unclear
```

### 처리
- `positive`: source validation 통과 시 positive event 후보
- `negative`: negative_event_evaluator 후보
- `neutral`: ignored
- `unclear`: ignored
- enum 외 값: ValueError
- LLM-only event: ignored

### 금지
- LLM 단독 PASS 근거 금지
- LLM이 종목 추천 생성 금지
- LLM이 투자 판단 생성 금지
- LLM이 목표가/매수/매도 판단 생성 금지

**핵심:** LLM은 catalyst_score를 직접 올리는 변수가 아니다. LLM은 event 인정 여부를 제한하는 안전장치다.

---

## 15. M&A 처리

### mna_role enum
```
ACQUIRER     인수기업
TARGET       피인수기업
UNCLEAR      역할 불명확
NOT_MNA      일반 event
```

### 처리
| role | 처리 |
|---|---|
| ACQUIRER | catalyst 후보 가능 (단 자동 PASS 금지, source validation + materiality 확인 필요) |
| TARGET | Step 1 manual_exclusion + trap C 대상. Gate2 PASS 근거 금지 |
| UNCLEAR | score 반영 금지, MANUAL_REVIEW |
| NOT_MNA | 일반 event 처리 |

### 공식
```
if event.category == MNA and mna_role == TARGET:
  do not score as catalyst
  mark step1_exclusion_required

if event.category == MNA and mna_role == UNCLEAR:
  ignore event for score
  mark mna_manual_review_required

if event.category == MNA and mna_role == ACQUIRER:
  evaluate as catalyst candidate
```

---

## 16. non-pass routing 순서 (코드 실행 순서 강제)

PASS_FULL AND 체인을 **먼저** 평가한다. PASS_FULL이 아니면 아래 순서로 non-pass routing 적용.

```
Step 0. enum validation (위반 시 ValueError)

Step 1. PASS_FULL AND chain 평가 (충족 시 즉시 PASS_FULL 반환)

Step 2. non-pass routing (코드 if 블록 실행 순서로 강제):

2-1. step1_exclusion_required == True
     → FAIL

2-2. negative_status == ACTIVE_NEGATIVE
     → FAIL

2-3. source_validation_status == FAIL
     → FAIL

2-4. catalyst_component_status == FAIL
     → FAIL

2-5. negative_pressure_ratio is known and >= 0.5
     → FAIL

2-6. earnings_trend_status == FAIL and analyst_estimate_status == FAIL
     → FAIL

2-7. deferred_recovery_conditions all true
     → MANUAL_REVIEW_DEFERRED_RECOVERY
     ★ 핵심: generic INSUFFICIENT_DATA 앞에 둠
     ★ 이유: PIT 데이터 한계로 INSUFFICIENT가 되는 Recovery 후보를
              Gate2-Recovery-profile로 넘기는 경로 보장

2-8. generic coverage / data missing
     - data_unit_validation_status in {INVALID, INSUFFICIENT_DATA}
     - OR negative_status == COVERAGE_UNKNOWN
     - OR source_validation_status == INSUFFICIENT_DATA
     - OR catalyst_component_status == INSUFFICIENT_DATA
     → INSUFFICIENT_DATA

2-9. materiality / interpretation unclear
     - negative_status == MATERIALITY_UNKNOWN
     - OR data_unit_validation_status == MANUAL_REVIEW
     - OR mna_manual_review_required == True
     - OR support_component_conflict == True
     - OR earnings_trend_status == MANUAL_REVIEW
     - OR analyst_estimate_status == MANUAL_REVIEW
     → MANUAL_REVIEW

2-10. fallback
      → MANUAL_REVIEW
```

### 우선순위 핵심
- **FAIL > MANUAL_REVIEW_DEFERRED_RECOVERY > INSUFFICIENT_DATA > MANUAL_REVIEW**
- 라우팅 우선순위는 산문 선언이 아니라 코드 if 블록 실행 순서로 강제

---

## 17. MANUAL_REVIEW_DEFERRED_RECOVERY

### 의미
PASS_FULL은 아니지만, 결함 없는 회복주가 PIT 데이터 한계 때문에 full PASS를 못 받은 경우 Gate2-Recovery-profile로 넘기는 handoff 상태.

- 이 상태 자체는 PASS가 아니다
- 1군 자격이 아니다
- 이 상태만으로 2군 자격도 아니다
- 이후 Gate2-Recovery-profile이 PASS_RECOVERY_PROFILE을 반환해야만 tier_classification에서 2군 후보로 평가

### deferred_recovery_conditions (모두 true 충족)
```
1.  PASS_FULL AND chain은 실패했다
2.  step1_exclusion_required == False
3.  negative_status == CLEAR_VERIFIED
4.  source_validation_status == PASS
5.  data_unit_validation_status == PASS
6.  mna_manual_review_required == False
7.  earnings_trend_status == PASS
8.  independent_catalyst_score >= 1.5
9.  independent_catalyst_score는 earnings/guidance/analyst와 같은 underlying cause가 아니다
10. cumulative_catalyst_score < 3.0 또는 analyst_estimate_status == INSUFFICIENT_DATA due to PIT analyst revision unavailable
11. 단일 earnings beat만으로는 handoff 금지
12. 2.02-only 유형 (어닝 하나만으로 모든 것을 설명하는 케이스) handoff 금지
13. catalyst event source validation 통과
14. negative_pressure_ratio가 known이면 < 0.5
15. earnings_trend_status != FAIL
16. analyst_estimate_status != FAIL (단 PIT analyst revision unavailable로 인한 INSUFFICIENT_DATA는 허용)
```

### 금지
- ACTIVE_NEGATIVE 있으면 handoff 금지
- COVERAGE_UNKNOWN이면 handoff 금지
- source_validation_status가 FAIL/INSUFFICIENT_DATA이면 handoff 금지
- data_unit_validation_status가 PASS 아니면 handoff 금지
- independent_catalyst_score가 earnings beat 자체에서 나온 것이면 handoff 금지
- support_component_conflict 있으면 handoff 금지

---

## 18. support_component_conflict

### 정의
```
support_component_conflict == True if:
  exactly one of earnings_trend_status or analyst_estimate_status == FAIL
```

### 처리
한쪽만 FAIL이고 다른 한쪽이 PASS 또는 MANUAL_REVIEW인 경우:
- PASS_FULL 금지
- 명확한 보조 신호 충돌이므로 사람 검토 필요
- → MANUAL_REVIEW

### 이유
catalyst가 강하더라도 보조 컴포넌트 한쪽이 명확히 FAIL인 상태는 자동 PASS 위험. 그러나 완전 탈락(FAIL)으로 보내기엔 다른 한쪽 신호가 살아있음. 절충으로 MANUAL_REVIEW.

---

## 19. FAIL / INSUFFICIENT_DATA / MANUAL_REVIEW 구분 원칙

### FAIL
명확한 탈락
- active + material + unresolved Hard Negative
- source validation 실패
- catalyst score 명확히 부족
- negative_pressure_ratio >= 0.5
- Step 1 exclusion 대상이 Gate2로 들어온 경우
- earnings + analyst 둘 다 FAIL

### INSUFFICIENT_DATA
필수 데이터 자체가 없어 판정 불가
- source coverage 부족
- negative event coverage 부족
- catalyst event date/source 불명확
- data_unit_validation_status가 INVALID 또는 INSUFFICIENT_DATA

### MANUAL_REVIEW
데이터는 있으나 해석이 모호
- materiality 판단 불명확
- M&A role 불명확
- earnings mixed
- analyst와 estimate 방향 충돌
- GAAP/non-GAAP 갭 등 정성 검토 필요
- support_component_conflict

---

## 20. 3개 산식 구조적 연결

```
                    [표준 Gate2 1차 평가]
                            ↓
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
          PASS_FULL    DEFERRED      FAIL/MR/IDS
              │       _RECOVERY           │
              │             ↓             │
              │      [Gate2-Recovery-     │
              │       profile 평가]       │
              │             ↓             │
              │   PASS_RECOVERY_PROFILE   │
              │             │             │
              ↓             ↓             ↓
        [tier_classification 평가]
              ↓             ↓
       1군 (PASS_FULL    2군 (PASS_FULL OR
        only)             PASS_RECOVERY_PROFILE)
```

### 산식별 정체성
- **standard Gate2**: 강한 full catalyst 구조, cumulative_catalyst_score >= 3.0, PASS_FULL 산출
- **Gate2-Recovery-profile**: 회복주 전용 제한 profile, independent_catalyst_score >= 1.5, PASS_RECOVERY_PROFILE 산출 (1군 금지, 2군만 허용)

### catalyst_score_calculator 출력 연결
- `cumulative_catalyst_score` → standard Gate2 PASS_FULL 평가
- `independent_catalyst_score` → Gate2-Recovery-profile 입력

### tier_classification cross-field invariant
```
PASS_RECOVERY_PROFILE + negative_status != CLEAR_VERIFIED → ValueError
```

---

## 21. 코드 PR 분할 봉인 순서

설계 봉인 후 코드 PR은 아래 순서로 분할한다. 각 PR은 **순수함수 + 단위테스트만**.

### PR 1: catalyst_score_calculator.py
- positive event scoring
- source validation
- LLM enum validation
- cumulative_catalyst_score
- independent_catalyst_score
- duplicate event_id 1회 점수화
- data_unit_validation_status 산출

### PR 2: negative_event_evaluator.py
- active/material/unresolved 판정
- negative_status 산출
- negative_pressure_score
- negative_pressure_ratio

### PR 3: earnings_trend_evaluator.py
- earnings/guidance trend status
- analyst/estimate trend status
- target_price_trap_flag 산출

### PR 4: standard_gate2_router.py
- PASS_FULL AND chain
- MANUAL_REVIEW_DEFERRED_RECOVERY handoff
- support_component_conflict 처리
- FAIL / INSUFFICIENT_DATA / MANUAL_REVIEW 라우팅

### 각 PR 원칙
- 순수함수 + 단위테스트만
- 외부 I/O 금지 (yfinance / requests / urllib / open / csv / pandas / read_csv / to_csv)
- scorer.py 수정 금지
- Telegram 수정 금지
- watchlist_log 수정 금지
- 파이프라인 연결 금지
- 커밋 전 GPT 검수
- 주요 PR은 Claude 재검증 후 머지

---

## 22. 설계로 못 닫는 잔여 (정상)

다음 변수들은 변수 주입 함수의 임계값 캘리브레이션 문제다. **live forward-only 로그 단계에서 검증**한다.

- catalyst event 가중치 임계값 (2.0 / 1.5 / 1.0 / 0.5)
- cumulative 3.0 / independent 1.5 / ratio 0.5 임계값
- `positive_component_pass_count >= 2` vs `>= 3`
- earnings/analyst PASS 조건 세부 임계값
- LLM 분류 결과 처리 일관성

**이는 설계 미완이 아니다. 설계의 정상적 끝.**

---

## 23. 봉인 후 금지

- 구조 수정 금지
- 산문 패치 추가 금지
- PASS_FULL 14개 AND 조건 변경 금지
- non-pass routing 10단계 우선순위 변경 금지
- catalyst mandatory + 2-of-3 구조 완화 금지
- BEAT + NO_GUIDANCE를 PASS로 격상 금지
- target_price_trap_flag를 PASS 근거로 사용 금지
- LLM 단독 판단으로 PASS 처리 금지
- 동일 event_id를 중복 점수화 금지
- BLOG_SOCIAL 단독으로 catalyst PASS 근거 사용 금지
- M&A TARGET을 Gate2 catalyst로 평가 금지
- deferred handoff를 generic INSUFFICIENT_DATA 뒤로 이동 금지 (dead code 재발)

---

## 24. 봉인 결론

**standard Gate2 final formula v0.1.2는 봉인 가능 상태로 확정한다.**

### 봉인 상태
- PASS_FULL 공식 확정 (14개 AND 조건)
- non-pass routing 순서 확정 (10단계)
- deferred recovery handoff 확정
- data unit validation status 확정 (enum 4상태)
- catalyst score 이중 출력 확정
- LLM 봉인 내부화 확정
- M&A role 처리 확정 (4상태)
- target price trap flag 산출 위치 확정
- 코드 PR 분할 순서 확정

### 3개 산식 구조적 연결 완성
standard Gate2 + Gate2-Recovery-profile + tier_classification 세 산식이 처음으로 구조적으로 연결됨.

### 다음 단계
PR 1: `catalyst_score_calculator.py` 순수함수 + 단위테스트 프롬프트 작성

---

**봉인 완료. 2026-05-29.**
**Claude 3라운드 적대적 검증 + GPT 합의.**
**다음 단계: PR 1 (catalyst_score_calculator.py) Codex 프롬프트 작성.**
