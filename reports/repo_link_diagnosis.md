# repo_link_diagnosis

## 0. 봉인 기준 확인

- GPT 프로젝트 소스 기준 봉인 문서: `maesoo_v2_paradigm_v1_5_1_RC_FULL.md`
- repo 내부 동일 문서 존재: YES
- repo 경로: `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md`
- 핵심 문구 근거:
  - `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:1` - `# 매수사냥개 v1.5.1-RC FULL (통합 봉인 문서)`
  - `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:3` - `봉인 일자: 2026-05-26`
  - `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:8` - `문서 목적: v1.5 기본 구조 + v1.5.1-RC 패치 통합 단일 봉인 문서`
  - `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:9` - `참조 우선순위: 본 문서가 v1.5 및 v1.5.1-RC를 대체한다.`
  - `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:16` - `v1.5.1-RC 봉인 후 구조 수정 금지`

## 1. 요약 판정

`audit_universe_quality.py` = **독립 분석**

근거:

- 운영 workflow는 `python run_daily_report.py`만 실행한다: `.github/workflows/main.yml:33-35`
- `run_daily_report.py`의 운영 PIPELINE은 `finviz_parser.py`, `yfinance_validator.py`, `scorer.py`, `telegram_reporter.py`만 포함한다: `run_daily_report.py:28-32`
- `scorer.py`는 `finviz_yfinance_validated.csv`를 읽고 `finviz_scored.csv`를 쓴다: `scorer.py:27-28`, `scorer.py:409`, `scorer.py:471-472`
- Telegram 후보 선정은 `finviz_scored.csv`와 `total_score` 기준만 사용한다: `telegram_reporter.py:25`, `telegram_reporter.py:75`, `telegram_reporter.py:109-111`, `telegram_reporter.py:225-232`
- audit 스크립트는 `reports/universe_quality_audit_v0_1.csv`를 자체 산출물로 정의하고 쓴다: `scripts/audit_universe_quality.py:18`, `scripts/audit_universe_quality.py:437-442`

## 2. 항목별 YES/NO 표

| 확인 항목 | YES/NO | 근거 파일 | 근거 줄번호 | 짧은 설명 |
|---|---|---|---|---|
| 1. `scorer.py`가 `reports/universe_quality_audit_v0_1.csv`를 읽거나 import하는가 | NO | `scorer.py` | 27-28, 409, 471-472 | `scorer.py`는 `finviz_yfinance_validated.csv`를 읽고 `finviz_scored.csv`를 쓴다. audit CSV 문자열은 `scorer.py`에서 발견되지 않았다. |
| 2. `scorer.py`가 audit의 `universe_role` / `audit_class` / `HIGH_RISK_REVIEW` 분류를 사용하는가 | NO | `scorer.py` | 450-467 | 점수 계산 후 `total_score`로 정렬한다. `universe_role`, `audit_class`, `HIGH_RISK_REVIEW`는 `scorer.py`에서 발견되지 않았다. |
| 3. `scorer.py`가 `turnaround_flag`를 직접 사용하는가 | NO | `scorer.py` | 27-28, 409, 450-467 | `scorer.py` 입력/계산 흐름에서 `turnaround_flag` 검색 결과가 없다. |
| 4. Telegram 알림 코드가 audit 결과 또는 `HIGH_RISK_REVIEW` 분류를 참조하는가 | NO | `telegram_reporter.py` | 25, 75, 109-111, 225-232 | Telegram은 `finviz_scored.csv`를 읽고 `total_score >= SCORE_CANDIDATE` 기준으로 후보를 만든다. audit/HIGH_RISK 문자열은 발견되지 않았다. |
| 5. GitHub Actions workflow가 `audit_universe_quality.py`를 직접 또는 간접 호출하는가 | NO | `.github/workflows/main.yml`; `run_daily_report.py` | 33-35; 28-32 | workflow는 `run_daily_report.py`만 실행하고, 운영 PIPELINE에는 audit 스크립트가 없다. |
| 6. GitHub Actions workflow가 `reports/universe_quality_audit_v0_1.csv`를 읽거나 생성하는가 | NO | `.github/workflows/main.yml` | 33-35 | workflow 검색에서 audit CSV 문자열은 발견되지 않았다. 실행 대상은 `run_daily_report.py`뿐이다. |
| 7. audit 결과가 실제 알림 후보 선정에 영향을 주는가, 아니면 `reports/` 보관용 산출물인가 | NO, 후보 선정 영향 없음 | `telegram_reporter.py`; `scripts/audit_universe_quality.py` | 109-111, 225-232; 18, 437-442 | 알림 후보는 `total_score` 기준으로만 선정된다. audit은 `reports/` 아래 CSV/summary를 쓰는 별도 산출물로만 확인된다. |
| 8. `tests/` 폴더에서 `turnaround == Y` 이면서 CORE 금지를 강제하는 테스트가 있는가 | NO | `tests/*.py`; `scripts/audit_universe_quality.py` | -; 596-597 | `tests/*.py`에서는 `turnaround`, `CORE`, `turnaround CORE violation` 관련 강제 테스트가 발견되지 않았다. 해당 검증 문구는 audit 스크립트 내부 validation에만 있다. |
| 9. `tests/` 폴더에서 `audit_universe_quality.py` 또는 `universe_quality_audit_v0_1.csv`를 운영 로직처럼 참조하는가 | NO | `tests/*.py` | - | `tests/*.py`에서 audit 스크립트명/audit CSV명 검색 결과가 없다. |
| 10. 지정 문자열 전역 검색을 수행했는가 | YES | repo 전체 텍스트 파일 | 아래 3장 | `.git`, `__pycache__`, `.pyc`, `.xlsx` 제외 후 줄번호 검색. 파일명 검색은 별도 확인했다. |

## 3. 전역 검색 결과 요약

검색 방식:

- 내용 검색: `rg --hidden -u -n -g "!.git/**" -g "!__pycache__/**" -g "!*.pyc" <검색어> .`
- 파일명 확인: `rg --files -uu | rg <검색어>`
- 줄번호가 의미 없는 binary/cache 산출물은 제외했다.

| 검색어 | 발견 파일/줄번호 |
|---|---|
| `universe_quality_audit_v0_1.csv` | `scripts/audit_universe_quality.py:18`; `reports/universe_quality_audit_summary_v0_1.md:9`; `reports/backtest_it_2026q1_summary_v0_1.md:30`; 파일명 `reports/universe_quality_audit_v0_1.csv` |
| `audit_universe_quality` | 내용 검색 NO MATCH; 파일명 `scripts/audit_universe_quality.py` |
| `HIGH_RISK_REVIEW` | `scripts/audit_universe_quality.py:42,211,293,300,309,316,325,332,339,389,451,460,471,510,525,584,585,587,590,652,658`; `reports/universe_quality_audit_v0_1.csv:20,60,64,86,94,97,183,188,193,195,213,221,263,314,319,399,400,408,490,496,498,512,514,618,629,638,639,640,641,642 (+11 more)`; `reports/universe_quality_audit_summary_v0_1.md:27,37,40-67 (+56 more)`; `reports/step3c_metadata_diagnosis_v0_1.md:128,150,313-328,744`; `reports/step3_samples_v0_1.csv:9,10,11,13,14,15,16,23,24,25`; `reports/backtest_it_2026q1_data_v0_1.csv:37,67`; `reports/backtest_it_2026q1_summary_v0_1.md:76,92`; `reports/step3f_additional_samples_v0_1.csv:27`; `reports/step3g_foreign_ownership_fillrate_v0_1.md:49`; `reports/track_c_session_001_template.csv:6,7,8,9` |
| `turnaround_flag` | `scripts/audit_universe_quality.py:31,232,412,463,520,596,660,671`; `universe_master.csv:1`; `backups/universe_master_pre_v0_2_repair_20260526.csv:1`; `docs/paradigm/maesoo_v2_paradigm_v1_5_1_RC_FULL.md:1011,1574`; `reports/universe_quality_audit_v0_1.csv:1`; `reports/universe_quality_audit_summary_v0_1.md:146`; `reports/step3c_metadata_diagnosis_v0_1.md:38,54,75,111,127,148,162,310,311,744`; `reports/step3f_additional_samples_v0_1.csv:1`; `reports/step3_samples_v0_1.csv:1,23,24,25` |
| `turnaround CORE violation` | `scripts/audit_universe_quality.py:597` |
| `universe_role` | `scripts/audit_universe_quality.py:32,413,447,451,452,453,460,471,482,506,507,569,570,584,587,596,598,600,603,612,646,652,658`; `reports/universe_quality_audit_v0_1.csv:1`; `reports/universe_quality_audit_summary_v0_1.md:20,21`; `reports/step3c_metadata_diagnosis_v0_1.md:55,128`; `reports/step3g_foreign_ownership_fillrate_v0_1.md:25` |
| `REVIEW_BEFORE_SCORING` | `scripts/audit_universe_quality.py:83,214`; `reports/universe_quality_audit_v0_1.csv:20,60,64,86,94,97,183,188,193,195,213,221,263,314,319,399,400,408,490,496,498,512,514,618,629,638,639,640,641,642 (+11 more)`; `reports/step3_samples_v0_1.csv:9,10,11,13,14,15,16,23,24,25`; `reports/backtest_it_2026q1_data_v0_1.csv:37,67`; `reports/backtest_it_2026q1_summary_v0_1.md:76`; `reports/step3c_metadata_diagnosis_v0_1.md:132,153`; `reports/step3f_additional_samples_v0_1.csv:27` |

추가 확인:

- `audit_class`는 `scorer.py`에서 발견되지 않았다. 발견 위치는 report 산출물 계열뿐이다: `reports/backtest_it_2026q1_data_v0_1.csv:1`, `reports/backtest_it_2026q1_summary_v0_1.md:73,91`
- `scorer.py`, `telegram_reporter.py`, `.github/workflows/main.yml`, `run_daily_report.py`에는 audit CSV명, `HIGH_RISK_REVIEW`, `REVIEW_BEFORE_SCORING`, `universe_role` 운영 참조가 발견되지 않았다.

## 4. 운영 영향 판정

- audit 결과가 실제 Telegram 후보 선정에 영향을 주는지: **NO**
  - 후보 리스트 생성은 `df["total_score"] >= SCORE_CANDIDATE` 기준이다: `telegram_reporter.py:109-111`
  - 메시지 후보/강한 후보 분리도 `total_score` 기준이다: `telegram_reporter.py:225-232`
- `scorer.py`와 연결되는지: **NO**
  - `scorer.py` 입력은 `finviz_yfinance_validated.csv`, 출력은 `finviz_scored.csv`다: `scorer.py:27-28`
  - 실제 read/write도 같은 상수만 사용한다: `scorer.py:409`, `scorer.py:471-472`
- GitHub Actions에서 실행되는지: **NO**
  - workflow 실행 명령은 `python run_daily_report.py`다: `.github/workflows/main.yml:33-35`
  - `run_daily_report.py` PIPELINE은 audit 스크립트를 포함하지 않는다: `run_daily_report.py:28-32`

판정: 현재 파일/줄번호 근거 기준으로 audit 결과는 운영 알림 후보 선정에 연결되지 않고, `reports/` 계열 분석/보관 산출물로만 확인된다.

## 5. v0.3 작업 가능 여부

- audit이 독립 분석으로 판정되므로: **v0.3 audit 재설계 가능**
- 단, `reports/step3*`, `reports/backtest*`, `reports/track_c*` 산출물에 기존 audit 분류 문자열이 남아 있으므로, v0.3 재설계 시 운영 코드가 아니라 report/분석 산출물 호환성 범위를 별도 확인하는 것이 필요하다.

## 6. git status -sb 출력

```text
## main...origin/main
?? backups/
?? reports/backtest_it_2026q1_data_v0_1.csv
?? reports/backtest_it_2026q1_summary_v0_1.md
?? reports/repo_link_diagnosis.md
?? reports/track_c_session_001_ai_assisted_review.xlsx
```

## 7. git diff --stat 출력

```text

```
