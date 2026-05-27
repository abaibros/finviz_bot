# Track C Session 001 블라인드 검증 가이드

본 검증은 이 종목이 오를지 맞히는 작업이 아니라, 현재 universe 등급/분류가 맞는지 확인하는 작업입니다.

## 사용법
- CSV를 열고 사용자 입력 5개 컬럼만 채운다.
- 모르겠으면 NEED_MORE_INFO를 사용한다.
- 외부 자료를 억지로 찾지 않는다.
- 중간 저장 가능하다.
- AI 판단/사후 주가 결과를 보지 않는다.

## user_verdict
- KEEP_CURRENT: 현재 등급/역할이 대체로 맞다고 판단
- DEMOTE: 현재 등급/역할이 위험도 대비 너무 높다고 판단
- PROMOTE: 현재 등급/역할이 안정성 대비 너무 낮다고 판단
- EXCLUDE: 분류 조정이 아니라 universe 자체에서 제외해야 한다고 판단
- NEED_MORE_INFO: 현재 정보만으로 판단 불가

## event_risk_simple
- M_AND_A_RISK: 인수합병, 공개매수, 상장폐지 등 구조적 이벤트 의심
- LEGAL_RISK: 소송, 규제, 제재 등 법적/규제 리스크 의심
- SPECIAL_EVENT: 일회성 급등/정책/실적/테마 이벤트 의심
- NONE: 뚜렷한 이벤트 리스크 없음

## 중간 저장
10개를 다 못 채워도 중간 저장 가능하다.
완료본 파일명은 `reports/track_c_session_001_completed.csv` 권장.

## 회차 완료 후 처리 흐름
사용자는 completed CSV를 GPT에게 전달한다.
GPT는 사용자 verdict 분포, NEED_MORE_INFO 비율, 양식 피로도를 먼저 점검한다.
그 뒤 Claude 반례 검증을 거쳐 2회차 양식 수정 여부를 결정한다.

## 강한 경고
AI verdict, GPT/Claude 사전 판단, HARD_FILTER_CANDIDATE 여부, 사후 주가 결과를 보면 해당 회차는 블라인드 검증으로 인정하지 않는다.
