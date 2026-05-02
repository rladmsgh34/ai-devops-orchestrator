---
id: 007
title: 투기적 위성 저장소 — 근거 없는 단정적 주장(결정 케이스)
date: 2026-05-02
project: ai-devops-orchestrator
actor_involved: [user, orchestrator, claude-code]
state: decided-implement
deadline: 2026-05-09
decided_on: 2026-05-02
decided_by: user
related_cases: [001]
related_components: [cases-pipeline, learning-store]
---

# Case 007 — 투기적 위성 저장소 (결정 케이스)

> 이 케이스는 case #005가 박제한 트리거 임계점 룰의 **두 번째 자기 적용**이다.
> 첫 적용은 case #006(UDI 분리)이었고, 두 번째인 본 케이스는 **인스턴스가 동일 시점·동일 패턴으로 다수 발견된 변형**이다 — 이 변형의 처리 방식 자체가 §6의 학습으로 박제된다.

## 1. 누적된 인스턴스

### 기존 박제

| ID | 한 줄 요약 |
|---|---|
| #001 | 폐기된 nginx 서비스 + docker-compose의 운영 청구가 잔존. "이미 폐기된 모델의 자기소개"가 코드에 박제되어 있던 사례 |

### 본 케이스에서 신규 사실화

> 4건이 동일 시점·동일 패턴으로 동시 발견되어 별도 박제 없이 본 결정 케이스에서 직접 인스턴스 목록으로 다룬다 (본 변형의 처리 절차는 §6 참조).

| 저장소 | 단정적 자기 주장 (README) | 실제 내용 | 마지막 활동 |
|---|---|---|---|
| `devops-docker-templates` | "프로덕션 검증된 Docker 템플릿", "원클릭 배포" | LICENSE + README만 | 2026-04-28 단일 커밋 (v1.0.0) |
| `devops-pattern-library` | "47+ 패턴", "95% 성공률", "7차례 실제 배포 검증" | LICENSE + README만 | 2026-04-28 단일 커밋 (v1.0.0) |
| `framework-devops-adapters` | "5+ 프레임워크 어댑터", "실전 검증" | LICENSE + README만 | 2026-04-28 단일 커밋 (v1.0.0) |
| `n8n-devops-workflows` | "검증된 15개 워크플로우" | 실제 워크플로우 **1개**(`workflows/github/github-push-analyzer.json`). `templates/`·`credentials/`·`docs/`는 빈 디렉토리 | 2026-04-28 단일 커밋 (v1.0.0) |

### 1.1 사후 발견된 사용자 사전 정정 (post-decision)

§5 결정 직후 archive 실행 단계에서, 4개 위성 repo 중 3개(`devops-pattern-library`, `framework-devops-adapters`, `n8n-devops-workflows`)에 사용자가 2026-05-01에 직접 작성한 정정 PR이 OPEN 상태로 존재하고 있었음이 발견됨 (브랜치 `chore/honest-readme-status`, 톤 "Status: Placeholder" / "early prototype"). 본 결정 케이스의 §1 표 작성 시점에는 4월 28일 단일 커밋만 보고 "정지된 repo"로 판단해 `git fetch` + open PR 점검을 누락한 것이 원인.

| Repo | 사용자 PR (2026-05-01) | 본 결정 후 영향 |
|---|---|---|
| `devops-docker-templates` | 없음 | archive 커밋이 master에 정상 적용 |
| `devops-pattern-library` | PR #1 OPEN | 본 결정의 archive 커밋이 사용자 PR base를 어긋나게 만듦 → revert 후 사용자 PR 머지 → 그 위에 archive notice 헤더 prepend |
| `framework-devops-adapters` | PR #1 OPEN | 동일 처리 |
| `n8n-devops-workflows` | PR #1 OPEN | 본 결정의 archive 커밋 push가 원격 ahead로 자동 거부 → 로컬 폐기 후 사용자 PR 머지(충돌은 PR head 채택으로 해결) → archive notice 헤더 prepend |

처리 결과: 사용자의 5월 1일 작업(정정 톤)과 5월 2일 결정(archive)이 양 단계로 누적되어 4개 모두 archive 직전 마지막 README 상태로 보존됨. 이는 사용자가 본 케이스 발행 하루 전 이미 같은 "Unbacked Self-Claim" 패턴을 부분적으로 인식하고 있었음을 의미하며, §5 결정(2026-05-02 (a))은 그 인식의 갱신·강화로 해석된다.

## 2. 공통 패턴

- 케이스 로그(또는 그에 준하는 검증 근거) **0건**인 상태에서 v1.0.0 태깅
- README에 **단정적 정량 주장**(N개·N%·"검증된"·"프로덕션") 선행
- 4건 모두 **2026-04-28 단일 커밋** 이후 정지 — 5일째 후속 활동 없음
- `devops-pattern-library`의 "패턴 라이브러리" 역할은 `langchain-devops-analyzer/patterns/`(실제로 동작 중인 학습 저장소)와 **역할 중복**

## 3. 어느 레이어에서 막을 수 있는가

이 패턴은 **레이어 결함이 아니라 발행 절차의 결함**이다. case #005와 같은 분류:

- **케이스 파이프라인 결함** — "케이스 없이 자산을 발행하는 경로"가 막혀 있지 않음
- 직접적 책임은 사용자(생성 결정)와 claude-code(생성 실행)에 분산되며, orchestrator는 **사실 박제와 회수 절차**의 책임이 있음

## 4. 옵션 (3지선다)

### (a) `decided-implement` — 회수 + 흡수

- **devops-pattern-library** → **archive** (GitHub repo 보존, 새 커밋 차단). 사유: 실제 학습 자산은 `langchain-devops-analyzer/patterns/`에 통합 중이므로 본 repo는 빈 자기소개에 그침
- **devops-docker-templates / framework-devops-adapters** → **archive**. 사유: LICENSE+README만 존재, 케이스 0건
- **n8n-devops-workflows** → **archive**. 사유: 감사 결과 워크플로우 1개·빈 디렉토리 3개로 README의 "15개" 주장과 동일 패턴 위반, 다른 3건과 차등 처리 근거 없음. `github-push-analyzer.json`은 archive 후 재가동 시점에 검증 케이스와 함께 복원 또는 본 orchestrator의 `services/n8n-workflows/`로 이전
- 4건 모두 README의 정량적 단정 표현(N개·N%·"검증된")을 case-driven 원칙에 맞춰 정정 (archive 전 마지막 커밋)
- 회수 사실 자체를 case #001의 후속 박제로 추가 (이미 한 번 발생한 패턴의 두 번째 회수)

### (b) `decided-observe` — 추가 관찰

- 별도 작업 없음. 다음 인스턴스(5번째)가 발견되거나 4개 중 하나가 실제 자산을 갖게 될 때까지 대기
- 관찰 대상: (1) 추가 위성 repo 생성 여부, (2) 기존 4건의 6주 내 활동 재개 여부
- 사유 후보: 4건이 곧 채워질 계획이 있다면 archive는 조기 행동

### (c) `decided-wontfix` — 정정만, archive 안 함

- README의 단정적 표현만 case-driven 원칙에 맞춰 톤 다운(`"가설"`·`"실제 사례 누적 시 채워질 슬롯"` 등)
- archive 비용 > 정정 비용일 때 합리적 선택. 단, "박제만 쌓이는 저장소" 패턴이 잔존함을 본 케이스에 명시

## 5. 사용자 결정

- [x] (a) 코드화(회수+흡수)
- [ ] (b) 추가관찰
- [ ] (c) wontfix(정정만)

| 항목 | 값 |
|---|---|
| 결정자 | 사용자 |
| 결정일 | 2026-05-02 |
| 결정 사유 | 4건 모두 케이스 0건·자산 ≤1건·v1.0.0 박제로 동일 패턴(Unbacked Self-Claim) 위반. 빠른 archive로 패턴 재발의 비용을 박제하는 것이 추가 관찰 비용보다 작음. n8n의 단일 워크플로우는 검증 케이스 발생 시 본 orchestrator로 이전 |

### 후속 PR (분리)

본 PR 머지 직후 다음 작업을 별도 PR로 진행:

1. 4개 위성 repo의 README를 case-driven 원칙에 맞춰 톤 다운 → 마지막 커밋 → `gh repo archive` 실행
2. case #005 §6 양식에 "동시 다발 인스턴스(N≥2) 처리 절차" 보완 (본 케이스 §6 학습 반영)
3. 회수 사실을 case #001의 후속 박제 (선택, 본 §8의 메타 패턴 명명을 case #001 인덱스에서 참조)

## 6. 처리 절차 보완 (본 변형의 학습)

case #005 §6 양식은 "기존 박제된 인스턴스 케이스를 묶는 것"을 전제했지만, 본 케이스처럼 **동일 패턴이 동일 시점에 다수(N≥2) 발견되는 경우** 별도 박제를 강제하면 단일 발견을 N건으로 부풀린다. 따라서 다음 보완을 적용한다:

- 동시 다발 인스턴스(N≥2 동일 패턴, 동일 시점, 동일 액터)는 **별도 박제 없이 결정 케이스의 §1 표로 직접 사실화**한다
- 이 경로를 택한 경우 결정 케이스 본문에 그 사실을 명시한다 (본 §6이 그 명시)
- 이 보완은 본 PR이 머지된 시점에 case #005의 §6 양식에 반영되어야 한다 (후속 PR 또는 본 PR에서 동시 처리)
- **다중 외부 자산 일괄 처리 시 사전 점검 의무** — 결정의 (a) 코드화가 외부 N개 자산(repo·서비스·문서)에 일괄 적용될 때, 적용 직전 각 자산을 `git fetch`하고 open PR / 활성 브랜치 / 진행 중 작업을 점검할 의무가 있다. 본 §1.1은 이 절차의 부재가 사후 정정을 야기한 첫 사례다. 점검 결과 발견 시 처리 경로(병합·revert·통합)를 결정 케이스 본문에 명시한 후 실행한다

## 7. 마감일 도래 시

- 2026-05-09까지 §5의 결정이 없으면, 그 사실 자체를 회고 케이스로 발행 (case #005 절차)

## 8. 학습 (ChromaDB 인덱싱 대상)

투기적 자산은 **단정적 주장**과 **활동 부재**가 동시에 나타나는 신호로 식별된다. 케이스 0건인 상태의 v1.0.0 태깅 + "N개·N%·검증된" 톤의 README + N일 이상 후속 커밋 부재는 단독으로는 부분 신호이지만, 셋이 같이 나타나면 강한 신호다. 회수의 핵심은 자산 자체의 삭제가 아니라 **"자산이 자기 근거를 가지지 못한 채 존재한다"는 사실의 박제**다 — 같은 손이 다음 위성 repo를 만들 때 본 케이스가 컨텍스트로 첨부되어야, 패턴 자체가 재발하지 않는다.

case #001(폐기 모델의 자기소개)과 본 케이스(아직 검증되지 않은 자산의 자기소개)는 **시간축의 양 끝**이다 — 전자는 "과거에 있었던 것이 사라졌는데도 남은 자기소개", 후자는 "아직 없는 것에 대한 미리 쓴 자기소개". 둘 다 **자산이 사실보다 자기 자신에 대한 주장이 앞선 경우**다. 이 메타 패턴을 "Unbacked Self-Claim"으로 명명하고 향후 인스턴스를 본 카테고리로 묶는다.

### 사후 발견의 메타 학습 (§1.1 부산물)

같은 패턴을 사용자가 결정 케이스 발행 하루 전에 이미 부분 정정으로 인식하고 있었다는 사실은 그 자체로 박제 가치가 있다. 결정 케이스의 §5 결정과 사용자의 사전 인식은 같은 패턴의 두 단계(부분 → 강화)이며, 미래 케이스 검색 시 **"사용자가 같은 영역에서 무엇을 이미 시도했는가"** 를 컨텍스트로 자동 첨부하는 것이 학습 루프의 다음 보완 후보다. 또한 결정 직후 외부 자산 일괄 처리는 자동화 지연 역설의 거울상 위험(*자동화 조기 실행 역설*)을 가진다 — 사용자의 진행 중 작업을 덮어쓸 수 있으므로 사전 fetch는 비용이 아니라 안전장치다.
