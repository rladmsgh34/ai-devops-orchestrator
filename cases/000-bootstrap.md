---
id: 000
title: Bootstrap — 오케스트레이터를 지휘자 모델로 재정의
date: 2026-05-01
project: ai-devops-orchestrator (메타)
actor_involved: [user, orchestrator]
state: resolved
related_pr: chore/redesign-conductor
related_components: [layer-1-context, layer-2-triage, layer-3-packing, layer-4-verify-gate, layer-5-approve-deploy]
---

# Case 000 — Bootstrap

## 1. 무슨 일이 있었나 (사실)

- 2026-05-01, 사용자가 gwangcheon-shop의 운영 방식을 명시:
  - Claude Code가 개발
  - Antigravity가 검증
  - 사용자가 승인
- 기존 오케스트레이터(README 기준)는 "AI 6개 에이전트가 자동 분석·수정 PR 생성" 모델이었음
- 이 모델은 Claude Code(생성자)와 Antigravity(검증자) 역할과 정면으로 충돌함을 확인
- 사용자가 재정의 진행에 동의 ("좋아 진행하자, 실제로 발생할 때마다 적용하면서 개선하자")

## 2. 어느 액터/레이어에서 발생했나

메타 케이스 — 액터 정의 자체가 문제였음. 오케스트레이터가 자기 포지션을 잘못 잡고 있었다.

## 3. 오케스트레이터가 막거나 도울 수 있었는가

해당 없음 (메타 케이스). 단, 이 재정의가 향후 모든 레이어 작업의 토대가 됨.

## 4. 반복 가능성

- 동일 케이스 재발: 매우 낮음 (1회성 정의 작업)
- 영향: 매우 큼 (모든 후속 작업의 전제)

## 5. 결정

- [x] 기존 컴포넌트 재정의 (제거/유지/확장 매트릭스 작성)
- [x] 신규 문서 작성: `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/PIPELINE_STATES.md`
- [x] 케이스 워크플로우 도입: `cases/`
- [x] 코드는 케이스 발생 전까지 만들지 않음

## 6. 후속 작업

- 기존 README의 "Auto-Fix PR / Code Quality / Security Scanner" 섹션을 "재정의 중"으로 표기 → ARCHITECTURE.md로 링크
- 첫 실제 케이스(001) 발생 시점 = 첫 컴포넌트 코드화 시점

## 7. 학습 (ChromaDB 인덱싱 대상)

오케스트레이터는 코드를 직접 만드는 4번째 개발자가 아니라, Claude Code(생성)·Antigravity(검증)·사용자(승인) 세 액터를 잇는 지휘자다. 새 기능을 만들 때 "이건 어느 액터의 일인가, 오케스트레이터가 매개해야 하는가"를 먼저 묻는다. 가설로 기능을 추가하지 않고, `cases/`에 실제 발생 근거가 있을 때만 코드를 짠다.
