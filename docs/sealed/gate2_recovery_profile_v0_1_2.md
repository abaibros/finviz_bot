# Gate2-Recovery-profile v0.1.2 — 설계 봉인 문서

**봉인 일자:** 2026-05-29
**상태:** 설계 PASS (Claude 3라운드 적대적 검증 + GPT 합의)
**범위:** Gate2 내부 Recovery 후보 전용 제한 판정 프로파일
**상위 봉인 문서:** maesoo_v2_paradigm_v1_5_1_RC_FULL.md

---

## 1. 정체성

Gate2-Recovery-profile v0.1.2는 Gate2 내부에서 Recovery 후보만 제한 판정하는 보조 프로파일이다.

### 이것은 ___이 아니다
- Gate2 전체 구현 X
- Gate3 Recovery Track R-A~R-D 수정 X
- Continuation C-E 약화 X
- 표준 Gate2 PASS_FULL의 대체 X

### 적용 범위
- Gate3에서 Recovery Track으로 평가될 후보
- standard Gate2가 MANUAL_REVIEW_DEFERRED_RECOVERY로 핸드오프한 후보
- 2군 또는 MANUAL_REVIEW 전용 (1군 적용 금지)

---

## 2. 검증 이력

| 버전 | 잔여 | 결과 |
|---|---|---|
| v0.1 | 7개 반례 중 2 심각·4 부분·1 닫힘 | CONDITIONAL |
| v0.1.1 | 상태기계 닫힘, 판별함수 5개 공백 | CONDITIONAL |
| v0.1.2 | 판별함수 + 라우팅 + 산식 매핑 완료 | **PASS** |

### v0.1.2에서 마지막으로 닫힌 4개
1. 2군 산식에 Gate1 조건 추가 (`MANUAL_REVIEW_2G_ELIGIBLE`)
2. DEFERRED 가격 조건 삭제 (Gate3 전방참조 제거)
3. 판정식 ↔ 라우팅 테이블 2단 분리
4. source_confidence를 catalyst용/negative-scan용으로 분리

---

## 3. 상태값 정의

### 표준 Gate2 1차 라우팅 상태

```
standard_gate2_status ∈ {
  PASS_FULL,
  FAIL_HARD_DROP,
  MANUAL_REVIEW_DEFERRED_RECOVERY,
  MANUAL_REVIEW_STOP,
  INSUFFICIENT_DATA_STOP
}
```

| 상태 | 의미 | Gate3 핸드오프 |
|---|---|---|
| PASS_FULL | 기존 Gate2 전체 기준 통과 | YES |
| FAIL_HARD_DROP | 명확한 탈락 (되살릴 수 없음) | NO |
| MANUAL_REVIEW_DEFERRED_RECOVERY | Recovery 후속 평가로 보류 | YES |
| MANUAL_REVIEW_STOP | 사람 검토 필요, 자동 중단 | NO |
| INSUFFICIENT_DATA_STOP | 핵심 데이터 부족, 중단 | NO |

### Gate2 최종 결과

```
gate2_result ∈ {
  PASS_FULL,
  PASS_RECOVERY_PROFILE,
  MANUAL_REVIEW,
  INSUFFICIENT_DATA,
  FAIL
}
```

### Negative Status

```
negative_status ∈ {
  CLEAR_VERIFIED,
  ACTIVE_NEGATIVE,
  MATERIALITY_UNKNOWN,
  COVERAGE_UNKNOWN
}
```

- **CLEAR_VERIFIED**: 최소 커버리지 충족 + active/material/unresolved 없음
- **ACTIVE_NEGATIVE**: 3조건 충족 (FAIL)
- **MATERIALITY_UNKNOWN**: 부정 이벤트는 있으나 중요도 불명 (MR)
- **COVERAGE_UNKNOWN**: 탐지 커버리지 부족 (MR)

**핵심 원칙:** 미탐지 ≠ CLEAR. 조용함은 CLEAR가 아니다.

### Trap F Status

```
trap_f_status ∈ {
  F_CLEAR,
  F_MAJOR,
  F_MINOR,
  F_UNKNOWN_DATA_MISSING
}
```

| 상태 | 처리 |
|---|---|
| F_CLEAR | PASS 조건에 사용 가능 |
| F_MAJOR | FAIL_HARD_DROP |
| F_MINOR | MANUAL_REVIEW_STOP |
| F_UNKNOWN_DATA_MISSING | INSUFFICIENT_DATA_STOP |

---

## 4. PASS_RECOVERY_PROFILE 최종 판정식

다음 11개 조건이 모두 AND로 충족되어야 한다.

```
PASS_RECOVERY_PROFILE =
  standard_gate2_status == MANUAL_REVIEW_DEFERRED_RECOVERY
  AND gate3_recovery_status == PASS
  AND earnings_condition == PASS
  AND independent_catalyst_score >= 1.5
  AND catalyst_underlying_cause != earnings_underlying_cause
  AND negative_status == CLEAR_VERIFIED
  AND catalyst_source_confidence == OK
  AND negative_scan_coverage == CLEAR_VERIFIED
  AND eps_basis_integrity == OK
  AND trap_f_status == F_CLEAR
  AND split_share_count_basis == OK
```

### 라우팅 우선순위 (코드 실행 순서 강제)

**FAIL > INSUFFICIENT_DATA > MANUAL_REVIEW** 순서로 평가하며, 이 순서는 산문 선언이 아니라 코드 if 블록 실행 순서로 강제한다.

#### FAIL 라우팅
- `negative_status == ACTIVE_NEGATIVE`
- OR `trap_f_status == F_MAJOR`
- OR `earnings_condition == FAIL`

#### INSUFFICIENT_DATA 라우팅
- `eps_basis_integrity == FAIL`
- OR `split_share_count_basis == UNRESOLVED`
- OR `trap_f_status == F_UNKNOWN_DATA_MISSING`
- OR `earnings_condition == INSUFFICIENT_DATA`
- OR `gate3_recovery_status == INSUFFICIENT_DATA`

#### MANUAL_REVIEW 라우팅
- `negative_status == MATERIALITY_UNKNOWN`
- OR `negative_status == COVERAGE_UNKNOWN`
- OR `trap_f_status == F_MINOR`
- OR `catalyst_source_confidence == NOT_OK`
- OR `negative_scan_coverage == COVERAGE_UNKNOWN`
- OR `gate3_recovery_status == MANUAL_REVIEW`
- OR `earnings_condition == MANUAL_REVIEW`
- OR `independent_catalyst_score < 1.5`
- OR `catalyst_underlying_cause == earnings_underlying_cause`

#### Fallback
- 위 조건 모두 미해당 → MANUAL_REVIEW

---

## 5. 핵심 봉인 원칙

### 원칙 1: negative clear는 양성 조건이 아니다
PASS_RECOVERY_PROFILE은 어닝 + 독립 catalyst의 **2개 양성 조건**으로 성립한다. negative_status == CLEAR_VERIFIED는 **차단 해제 게이트**일 뿐 양성 조건이 아니다.

### 원칙 2: 한 사건은 catalyst와 negative-clear를 동시에 충족할 수 없다
동일 underlying cause의 이벤트는 catalyst와 negative-clear 중 하나로만 카운트한다. 부정 이벤트 해소가 단독 catalyst가 되는 것은 금지 (MR로 분류).

### 원칙 3: 동일 어닝 사이클은 하나의 earnings event
같은 8-K 2.02 발표 내부의 EPS beat / 가이던스 상향 / 세그먼트 개선은 하나의 earnings event로 묶는다. 별도 filing이어도 동일 어닝 사이클이면 동일 사건. independent catalyst는 어닝과 다른 underlying cause여야 한다.

### 원칙 4: independent catalyst 강도 하한
PASS_RECOVERY_PROFILE용 independent catalyst는 최소 1.5 이상 필요.
- 2.0 즉시매출 호재: 인정
- 1.5 펀더멘털 호재: 인정
- 1.0 전략 호재: MANUAL_REVIEW
- 0.5 주주환원: 단독 catalyst 불가

### 원칙 5: 미탐지는 CLEAR가 아니다
negative_scan_coverage가 CLEAR_VERIFIED가 되려면 SEC EDGAR 최근 90일 확인 + Finviz 또는 동급 headline source 정상 확인 + source confidence 충족이 모두 필요. 하나라도 실패하면 COVERAGE_UNKNOWN → MR.

### 원칙 6: 파이프라인 순서
1. 표준 Gate2 1차 평가
2. Gate3 Recovery Track 평가
3. Gate3 Recovery PASS 또는 MR 후보에 한해 Gate2-Recovery-profile 보조 평가
4. 결과는 PASS_RECOVERY_PROFILE 또는 MR로만 저장
5. 1군 산식에는 절대 사용 금지

### 원칙 7: 표준 Gate2 1차 라우팅 분리
- `standard_gate2_status == PASS_FULL` → 즉시 PASS_FULL 반환
- `FAIL_HARD_DROP` → 즉시 FAIL 반환 (Recovery-profile로 되살릴 수 없음)
- `MANUAL_REVIEW_STOP` → 즉시 MANUAL_REVIEW
- `INSUFFICIENT_DATA_STOP` → 즉시 INSUFFICIENT_DATA
- `MANUAL_REVIEW_DEFERRED_RECOVERY` → 이때만 위 11개 AND 체인 적용

---

## 6. 1군/2군 산식 매핑

### 1군 자격
```
tier1_eligibility =
  gate1_status == PASS
  AND gate2_status == PASS_FULL
  AND gate3_status == PASS
  AND gate4_status == PASS
  AND fatal_trap_count == 0
  AND f3_strength == STRONG
  AND entry_block == FALSE
```

**핵심:** PASS_RECOVERY_PROFILE은 1군 자격에 절대 사용 불가.

### 2군 자격
```
tier2_eligibility =
  gate1_status in {PASS, MANUAL_REVIEW_2G_ELIGIBLE}
  AND gate2_status in {PASS_FULL, PASS_RECOVERY_PROFILE}
  AND gate3_status == PASS
  AND gate4_status in {PASS, MANUAL_REVIEW}
  AND filter_f1 == PASS
  AND filter_f2 == PASS
  AND filter_f3 == PASS
  AND filter_f4 == PASS
  AND filter_f5 == PASS
  AND negative_status != ACTIVE_NEGATIVE
  AND fatal_trap_count == 0
  AND entry_block == FALSE
```

### MANUAL_REVIEW_2G_ELIGIBLE 정의
```
MANUAL_REVIEW_2G_ELIGIBLE =
  market_cap_usd_b >= 50.0
  AND debt_to_equity_pct <= 300.0
  AND (
    non_gaap_profit_turnaround_recent_2q == True
    OR moving_toward_profitability == True
  )
```

**중요:** Gate1 FAIL이면 2군 불가. Generic MANUAL_REVIEW도 2군 불가. 2군에서 허용되는 Gate1 예외는 MANUAL_REVIEW_2G_ELIGIBLE뿐이다.

### Cross-field invariant (2군 산식)
```
if gate2_status == PASS_RECOVERY_PROFILE and negative_status != CLEAR_VERIFIED:
    raise ValueError(
        "Inconsistent input: gate2_status == PASS_RECOVERY_PROFILE "
        "requires negative_status == CLEAR_VERIFIED"
    )
```

PASS_RECOVERY_PROFILE은 정의상 negative_status == CLEAR_VERIFIED일 때만 나오는 상태이므로, 다른 값과 동시에 들어오는 것은 호출자 입력 불일치 → ValueError.

---

## 7. 7개 반례 폐쇄

| 반례 | v0.1.2 폐쇄 결과 |
|---|---|
| 1. 2.02 단독/확장판 자동 통과 | 닫힘 — 동일 어닝 사이클은 하나의 earnings event로 묶음 |
| 2. negative clear 양성화 | 닫힘 — clear는 blocker 해제일 뿐 |
| 3. 어닝+clear 자동 통과 | 닫힘 — independent catalyst 1.5+ 별도 필요 |
| 4. Continuation C-E 우회 | 닫힘 — profile은 Recovery 후속 평가 + 1군/C-E 사용 금지 |
| 5. 1군 암묵 누수 | 닫힘 — PASS_FULL / PASS_RECOVERY_PROFILE 분리 |
| 6. EPS 착시 | 대부분 닫힘 — split/share-count + 함정 F + basis integrity |
| 7. 미탐지 negative 통과 | 닫힘 — COVERAGE_UNKNOWN은 MANUAL_REVIEW |

---

## 8. 코드 구현 봉인

### 구현 위치
- 파일: `gate2_recovery_profile.py`
- 테스트: `tests/test_gate2_recovery_profile.py`
- commit: 8d79c51
- 테스트: 22 tests OK

### 함수 시그니처
```python
def evaluate_gate2_recovery_profile(
    *,
    standard_gate2_status: str,
    gate3_recovery_status: str,
    earnings_condition: str,
    independent_catalyst_score: float,
    catalyst_underlying_cause: str,
    earnings_underlying_cause: str,
    negative_status: str,
    catalyst_source_confidence: str,
    negative_scan_coverage: str,
    eps_basis_integrity: str,
    trap_f_status: str,
    split_share_count_basis: str,
) -> str
```

### 함수 특성
- 순수함수
- no network / no file I/O / no CSV
- no global mutable state
- deterministic output
- invalid enum → ValueError
- independent_catalyst_score 숫자 아니면 ValueError (bool도 거부)

---

## 9. 설계로 못 닫는 잔여 (정상)

다음 변수들은 봉인 산식이 아니라 변수 주입 함수의 임계값 캘리브레이션 문제다. live forward-only 로그 단계에서 본다.

- `independent_catalyst_score` 임계값 (1.5)
- EPS delta 임계값 (>$0.03, ≥estimate 절댓값의 5% 등)
- materiality 판정 기준
- catalyst 등급 판정 (2.0/1.5/1.0/0.5)

**이는 설계 미완이 아니다. 설계의 정상적 끝.** LLM 분류와 결합되는 변수 주입 함수의 임계값은 실전 로그에서만 검증 가능.

---

## 10. 봉인 후 금지

- 구조 수정 금지
- 산문 패치 추가 금지
- 1군 산식에 PASS_RECOVERY_PROFILE 사용 금지
- 동일 underlying cause를 catalyst + clear로 동시 카운트 금지
- 어닝 release 내부 가이던스/세그먼트를 별도 catalyst로 카운트 금지
- 미탐지를 CLEAR_VERIFIED로 처리 금지
- weak catalyst (1.0/0.5) 자동 PASS 처리 금지
- Continuation C-E 적용 금지
- standard Gate2 PASS_FULL 대체 금지

---

## 11. 후속 코드 PR

### Cross-field invariant micro-patch
- commit: 64030e9 (Tier classification PR에 포함)
- PASS_RECOVERY_PROFILE + non-CLEAR negative_status → ValueError 강제

### 호출 관계 봉인
- standard Gate2 → MANUAL_REVIEW_DEFERRED_RECOVERY → Gate2-Recovery-profile → PASS_RECOVERY_PROFILE
- tier_classification: 1군은 PASS_FULL만, 2군은 둘 다 허용

---

**봉인 완료. 2026-05-29.**
**Claude 3라운드 적대적 검증 + GPT 합의 + Codex 구현 + cross-field invariant 머지 완료.**
**다음 단계: standard Gate2 v0.1.2 산식 코드 PR 4개 분할 진입.**
