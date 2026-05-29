# 매수사냥개 설계 봉인 문서

이 폴더는 매수사냥개 시스템의 **설계 봉인 문서**를 보관한다.

## 정체성

- **코드가 아니라 설계 동결 문서**
- Codex가 자동 생성하지 않음 (수동 작성)
- 한 번 봉인되면 구조 수정 금지 (봉인 원칙 1)
- 다음 작업의 근거 문서

## 보관 방식

### 권장: repo 내 `docs/sealed/` 폴더
```
finviz_bot/
├── docs/
│   └── sealed/
│       ├── gate2_recovery_profile_v0_1_2.md
│       ├── standard_gate2_v0_1_2.md
│       └── README.md
├── gate2_recovery_profile.py
├── tier_classification.py
├── trap_classification.py
└── ...
```

### 이유
1. 코드와 같은 repo에 있어 추적 쉬움
2. git history로 봉인 시점 영구 기록
3. 다음 세션에서 GPT/Claude가 자동 참조 가능
4. Codex 프롬프트에서 봉인 메모 path 지정 가능

## 현재 봉인된 문서

| 문서 | 봉인 일자 | 관련 코드 | 상태 |
|---|---|---|---|
| gate2_recovery_profile_v0_1_2.md | 2026-05-29 | gate2_recovery_profile.py (8d79c51) | 봉인 + 코드 머지 완료 |
| standard_gate2_v0_1_2.md | 2026-05-29 | (PR 1~4 대기) | 봉인 + 코드 PR 진입 직전 |

## 봉인 후 작업 순서

1. 봉인 문서 생성 → 작은 PR로 commit/push
2. 봉인된 산식 기준 Codex 프롬프트 작성
3. Codex 작업 → GPT/Claude 검수 → 머지
4. 산식 의문 발생 시 봉인 문서 참조 (수정 금지)
5. 봉인 수정이 필요하면 새 버전 봉인 (v0.1.2 → v0.1.3 등)

## 절대 금지

- 봉인 후 산식 임의 수정 금지
- 코드와 봉인 문서 어긋남 방치 금지
- "이참에 살짝 수정" 금지
- 봉인 문서 없이 코드 PR 진입 금지

## 커밋 방식

```bash
git add docs/sealed/
git commit -m "Seal Gate2-Recovery-profile v0.1.2 and standard Gate2 v0.1.2 design"
git push
```

`git add .` 금지. docs/sealed/만 명시.
