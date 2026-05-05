# Integrations & State Machine Mapping

> 이 문서는 **스펙 가정(spec assumptions)** 입니다. 코드는 아직 없습니다.
> 첫 케이스가 어느 가정을 강제할 때, 그 케이스가 그 가정을 바꿀 수 있습니다.
> 가정이 바뀌면 이 문서도 같은 PR에서 업데이트합니다.

## 1. 왜 이 문서가 필요한가

`docs/PIPELINE_STATES.md`는 추상 상태(`created → verified → approved → deployed → observed`)만 정의하고, GitHub/Antigravity와의 매핑은 "추후 결정"으로 비워뒀습니다. 첫 케이스가 발생하면 이 매핑을 즉석에서 결정해야 하고, 그 즉석 결정이 영구화될 위험이 큽니다. 이 문서는 그 즉석 결정의 **출발 지점**을 미리 박제해, 첫 케이스가 발생했을 때 토론할 표면을 제공합니다.

## 2. 외부 액터 인터페이스 가정

### 2.1 Claude Code

- **출력 형태**: GitHub PR (브랜치 `feature/#N-*`, `hotfix/#N-*`, `chore/*`)
- **메타데이터**: PR 본문에 작업 이슈 번호(`Closes #N`), 변경 요약, 테스트 체크리스트
- **트리거**: 수동(사용자 요청) — 오케스트레이터가 이슈를 자동 생성하지 않음 (액터 경계)
- **오케스트레이터가 읽는 신호**: PR open / push 이벤트, PR 라벨

### 2.2 Antigravity

> ⚠️ Antigravity의 실제 API/인터페이스는 외부 시스템의 결정에 따라 바뀔 수 있습니다.
> 아래는 **이 저장소가 가정하고 있는** 형태입니다.

- **호출 트리거**: PR이 `created` 상태로 진입 (PR open + 가드 통과)
- **입력 (오케스트레이터가 패킹해 전달)**:
  - 변경 파일 목록 + diff
  - 영향받는 테스트 목록
  - 관련 도메인의 과거 회귀 사례 (ChromaDB 조회 결과)
  - 의심 영역 메모 (예: "이 파일은 작년에 race condition")
- **출력 (오케스트레이터가 읽는)**:
  - **결과 게시 위치 (가정)**: PR comment 또는 GitHub status check `antigravity/verify`
  - **결과 스키마 (가정)**:
    ```yaml
    verified_sha: <SHA>          # 검증된 커밋 (이후 새 커밋이 추가되면 무효)
    status: pass | fail | partial
    findings:
      - severity: high | medium | low
        category: security | regression | quality | other
        message: <text>
        file: <path>
        line: <int>
    report_url: <optional URL to full report>
    ```
- **권한**: 오케스트레이터는 Antigravity 결과를 **읽기만** 함. 수정·재실행 트리거는 사용자 또는 Claude Code 측

### 2.3 사용자 (승인자)

- **승인 액션 후보** (case 발생 시 결정):
  - PR 라벨 `approved`
  - PR comment `/approve <verified_sha>` (sha 명시 필수, 검증 후 추가 커밋 차단용)
  - 별도 UI (현 단계 미고려)
- **권한**: 승인은 검증 통과 후에만 유효. 검증 실패 PR에 승인 라벨이 붙으면 오케스트레이터가 무시 + 경고

## 3. 상태머신 ↔ GitHub 매핑 (초안)

| 상태 | GitHub 표현 (가정) | 진입 가드 | 진입 신호 |
|------|-------------------|-----------|-----------|
| `created` | PR open, 라벨 없음 | main 직접 푸시 아님, 시크릿 없음, CI 통과 | PR `opened`/`synchronize` 이벤트 |
| `verified` | status check `antigravity/verify` = success, 라벨 `verified` 부착 | 검증 SHA == PR HEAD SHA | Antigravity의 status 게시 |
| `approved` | 라벨 `approved`, 또는 comment `/approve <SHA>` | `verified` 라벨 존재 + 검증 SHA == HEAD | 사용자 액션 |
| `deployed` | merged + 배포 워크플로우 완료 | 머지 후 헬스체크 통과 | 배포 워크플로우 종료 |
| `observed` | 배포 후 N분 경과 + 메트릭 안정 | SLI 임계값 충족 | 스케줄러 |
| `rejected` | 라벨 `rejected` 또는 PR closed | — | 어느 액터든 거절 |
| `rolled-back` | 롤백 워크플로우 실행됨 | — | 헬스체크 실패 또는 사용자 트리거 |

> 이 표는 **출발점**입니다. 첫 케이스가 발생하면 표의 한 행이 강제 결정되고, 그 결정이 다른 행에 파급됩니다.

## 4. 게이트 차단 시나리오 ↔ 구현 위치 (가정)

`PIPELINE_STATES.md` §4의 G1~G5를 GitHub 차원에서 어떻게 구현할지의 초안입니다.

| 시나리오 | 구현 위치 (가정) |
|---------|------------------|
| G1. main 직접 푸시 차단 | branch protection (이미 적용) + 오케스트레이터 워크플로우(보조) |
| G2. 검증 없이 승인 시도 | 오케스트레이터 워크플로우 — `approved` 라벨 부착 시 `verified` 라벨 존재 + SHA 일치 검증, 미달 시 라벨 자동 제거 + 코멘트 |
| G3. 검증 후 새 커밋 추가 | 오케스트레이터 워크플로우 — PR `synchronize` 이벤트에서 `verified` 라벨 자동 제거 |
| G4. 운영 직접 배포 | 배포 워크플로우 자체에서 `v*.*.*` 태그가 main 머지 SHA를 가리키는지 검증 |
| G5. 배포 후 SLI 위반 | 관찰 워크플로우 — 메트릭 임계 위반 시 자동 롤백 트리거 |

## 5. 구현 우선순위 가정

이 문서는 코드를 만들지 않습니다. 그러나 첫 케이스가 발생할 때 **어느 가드부터 코드화하는 게 합리적인가**의 기준선을 제시합니다:

1. **G3 (검증 후 새 커밋 차단)** — 가장 단순, GitHub 이벤트 1개 + 라벨 조작만으로 구현
2. **G2 (검증 없이 승인 시도)** — G3의 부산물로 같이 구현 가능
3. **G1 (main 직접 푸시 차단)** — branch protection으로 이미 부분 충족, 오케스트레이터의 보조 알림은 후순위
4. **G5 (배포 후 SLI)** — 메트릭 인프라 가정 필요, 후순위
5. **G4 (운영 직접 배포)** — 배포 워크플로우 자체의 변경 필요, 후순위

## 6. 미해결 가정 (케이스 발생 시 결정)

이 문서가 가정만 하고 결정하지 않은 항목들. 첫 케이스가 강제할 때 결정합니다.

- Antigravity 결과 게시 위치: PR comment vs status check vs 별도 API → **case ?**
- 사용자 승인 액션의 정식 형식: 라벨 vs slash command vs UI → **case ?**
- 다중 승인자 정책 도입 여부 → 1인 운영 환경에서는 보류
- 핫픽스 단축 경로 (검증 일부 생략 가능 여부) → **case ?**
- 캡처 채널의 첫 트리거 (case #002) → **후보 A(수동 발행) 도입 완료 (case #003)**. 후보 B(반자동 디스패치)는 gwangcheon-shop의 첫 트리거 사례 발생 시 실체화 예정.
- §2.2 Antigravity 인터페이스의 첫 실체화 진입 → **case #009 (a) 격리 결정** (2026-05-02). §2.2 가정 유지(폐기·톤 다운 안 함). `antigravity/verify` status check 게시는 여전히 0건이며, 첫 실체화 진입은 별도의 검증자 통합 케이스가 발행될 때. 이는 case #010 §6.2 트리거 임계점(case #004 두 번째 인스턴스 누적 또는 머지 후 회귀 2회 누적)이 충족되는 시점에 검증자 교체(Antigravity → gemini-cli) 결정과 함께 진행될 후보

## 7. 변경 절차

이 문서의 가정을 변경할 때:

1. 변경을 강제한 케이스를 `cases/`에 먼저 기록
2. 같은 PR에서 이 문서 + 그 케이스 파일을 함께 수정
3. PR 본문에 케이스 ID 명시

가정이 코드보다 먼저 결정될 일은 거의 없지만, 만약 그런 일이 생기면 그 자체를 케이스로 기록한다 (왜 코드 없이 가정만 바뀌었는가).
