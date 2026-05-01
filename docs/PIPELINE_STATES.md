# Pipeline State Machine

> 변경(코드 또는 설정)이 운영에 도달하기까지 거치는 상태 머신.
> 오케스트레이터의 **승인 게이트(Layer 4, 5)** 의 형식 스펙이다.

## 1. 상태

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ created  ├──▶│ verified ├──▶│ approved ├──▶│ deployed ├──▶│ observed │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  rejected       rejected       rejected       rolled-back    archived
```

| 상태 | 의미 | 진입 조건 |
|---|---|---|
| `created` | Claude Code가 PR 생성 완료 | PR이 GitHub에 push됨 |
| `verified` | Antigravity 검증 통과 | 검증 리포트 + 통과 표식 존재 |
| `approved` | 사용자 승인 | 사용자가 명시적 승인 (PR 라벨/코멘트/UI 액션) |
| `deployed` | 스테이징/운영 배포 완료 | 헬스체크 통과 |
| `observed` | 배포 후 N분 메트릭 안정 | 정해진 SLI 기준 충족 |
| `rejected` | 거절됨 | 액터 중 하나가 거절 (어느 단계에서든) |
| `rolled-back` | 배포 후 자동/수동 롤백 | 헬스체크 실패 또는 사용자 트리거 |
| `archived` | observed 후 N일 경과 | 정상 종료 |

## 2. 전이 규칙

### created → verified
- **트리거**: Claude Code가 "검증 요청" 신호 (PR 라벨 `needs-verification` 등)
- **가드**:
  - PR이 main 직접 푸시가 아닌가? (전역 CLAUDE.md 룰)
  - 변경 파일에 `.env` / 시크릿이 없는가?
  - 빌드/CI 통과했는가?
- **아티팩트**: 컨텍스트 패키지 (변경 파일 + 영향 테스트 + 과거 회귀 사례) → Antigravity로 전달
- **실패 시**: `rejected` (가드 위반 사유 기록)

### verified → approved
- **트리거**: Antigravity 검증 리포트 작성됨
- **가드**:
  - 검증 리포트가 "통과"인가?
  - 검증된 커밋 SHA == 현재 PR HEAD SHA인가? (검증 후 추가 커밋 차단)
  - 사용자가 명시적 승인 액션을 취했는가?
- **아티팩트**: 승인 기록 (누가, 언제, 어떤 SHA를)
- **실패 시**:
  - 검증 실패 → `rejected`
  - SHA 변경 → 자동으로 `created`로 되돌림 (재검증 강제)

### approved → deployed
- **트리거**: 사용자 승인 직후 자동
- **가드**:
  - 스테이징 우선 배포 룰 준수 (운영 직접 배포 차단)
  - 운영 배포는 `v*.*.*` 태그 푸시로만 (전역 CLAUDE.md 룰)
- **아티팩트**: 배포 SHA, 환경, 시작/종료 시각, 헬스체크 결과
- **실패 시**: `rolled-back` (자동 롤백 트리거)

### deployed → observed
- **트리거**: 배포 후 관찰 기간(기본 30분) 경과
- **가드**:
  - 에러율 < 임계값
  - p95 레이턴시 < 임계값
  - 사용자 정의 SLI 충족
- **아티팩트**: 관찰 기간 메트릭 스냅샷
- **실패 시**: `rolled-back`

### observed → archived
- **트리거**: N일(기본 7일) 경과
- **가드**: 그동안 롤백/사고 없음
- **아티팩트**: ChromaDB에 "성공 사례" 인덱싱

## 3. 메타데이터 (각 변경마다 추적)

```yaml
change_id: <PR번호 or 변경 식별자>
project: gwangcheon-shop
state: verified
history:
  - state: created
    at: 2026-05-01T10:00:00Z
    actor: claude-code
    sha: abc123
  - state: verified
    at: 2026-05-01T10:15:00Z
    actor: antigravity
    sha: abc123
    report: <antigravity report URL or content>
context_bundle:
  files_changed: [...]
  affected_tests: [...]
  past_incidents: [case-005, case-012]
guards_passed: [no-main-push, no-secrets, ci-green]
```

## 4. 게이트 차단 사례 (실제 발생 시 케이스로 기록)

오케스트레이터의 게이트가 차단해야 할 시나리오들:

- **G1**: main에 직접 푸시된 변경 → `created` 진입 거부
- **G2**: Antigravity 검증 없이 사용자 승인 시도 → `approved` 진입 거부
- **G3**: 검증 후 새 커밋 추가 → 자동으로 `created`로 되돌림
- **G4**: 운영 직접 배포 시도 (스테이징 우회) → `deployed` 진입 거부
- **G5**: 배포 후 SLI 위반 → `rolled-back` 자동 트리거

각 차단 사례가 실제 발생하면 `cases/`에 기록하고, 그 케이스가 게이트 구현의 근거가 된다.

## 5. 미정 사항 (케이스 발생 시 결정)

- 승인 액션의 구체적 형식 (PR 라벨? 코멘트? 별도 UI?)
- 관찰 기간/임계값의 환경별 기본값
- 핫픽스 경로 (검증 단계 단축 가능 여부)
- 다중 승인자 정책 (필요 시점에 도입)

> **원칙**: 추측으로 결정하지 않는다. 실제 케이스가 강제할 때 결정한다.

## 6. GitHub/Antigravity 매핑 출발점

위의 추상 상태가 GitHub PR 라벨/체크/이벤트와 어떻게 매핑되는지의 가정은 [`INTEGRATIONS.md`](./INTEGRATIONS.md)에 따로 박제했다. 첫 케이스가 그 가정을 강제할 때 같이 수정한다.
