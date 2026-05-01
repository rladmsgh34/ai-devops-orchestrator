---
id: 003
title: 최초 양방향 정렬 + 실제 CI 사건 캡처 (PR #370 E2E) + 후보 A 도입
date: 2026-05-01
project: ai-devops-orchestrator (캡처) / gwangcheon-shop (사건 발원지)
actor_involved: [user, claude-code, antigravity, orchestrator]
state: resolved
related_pr: case/003-first-real-event-and-capture-A
related_components: [layer-2-triage, cases-pipeline]
references:
  - gwangcheon-shop PR https://github.com/rladmsgh34/gwangcheon-shop/pull/370
  - gwangcheon-shop PR https://github.com/rladmsgh34/gwangcheon-shop/pull/369
  - run https://github.com/rladmsgh34/gwangcheon-shop/actions/runs/25213351506
---

# Case 003 — 최초 양방향 정렬 + 실제 CI 사건 캡처 + 후보 A 도입

## 1. 무슨 일이 있었나 (사실)

### 1-1. 양방향 정렬 (orchestrator ↔ gwangcheon-shop)

- 2026-05-01 오전 (UTC), orchestrator 측에서 case #000으로 "Antigravity = 검증자" 모델을 박제
- 같은 날 11:46 UTC, gwangcheon-shop 측에서 PR #369 `chore/role-flip` "B안 — Antigravity = verification only" 가 main에 머지됨 (run `25213161455`)
- **두 저장소가 같은 결정 방향으로 같은 시점에 정렬됨**. 사용자 한 명이 양쪽을 운영 중이라 사실상 같은 결정의 두 표면

### 1-2. 첫 실제 CI 사건 캡처 (수동)

- 2026-05-01 12:14 UTC경, 사용자가 orchestrator 측에서 "지금 gwangcheon-shop은 ci 작업중인데 이걸 캐치해서 체크할 순 없지"라고 물음
- 자동 채널은 case #002로 박제된 대로 부재 → `gh run list` + `ps -ef`로 수동 캡처
- 캡처된 작업: PR #370 `hotfix/#366-gemini-flash-latest` (Gemini chatbot 모델을 flash-latest 별칭으로 전환)
  - 이 VM의 self-hosted runner (PID 3465864 listener → 2513929 worker)에서 직접 실행 중이었음
  - 5개 워크플로우 중 4개 완료(CI / Security Review / Copilot 2건), 1개(E2E) 진행 중
- E2E 결과: **✅ PASS** (run `25213351506`, 25m26s 소요, Playwright 6 tests in 48.6s)
- 동반 발견: Node.js 20 deprecation 경고 (actions/checkout@v4 등) — 2026-06-02부터 강제 전환

## 2. 어느 액터/레이어에서 발생했나

- **Layer 2 (트리아지)** — case #002의 캡처 채널이 비어있는 상태에서, 사용자의 질문이 사실상 수동 트리거로 작용
- **양방향 정렬은 메타** — 액터 경계 문제가 아니라, orchestrator와 1차 적용 대상의 결정이 **같은 사용자**의 머릿속에서 동기화된 사례

## 3. 오케스트레이터가 막거나 도울 수 있었는가

- **이번에는 막을 일이 없었음**: PR #370은 모든 검증을 통과하고 정상 처리됨
- **다음에 도울 수 있는 것**:
  - PR #370 같은 이벤트가 자동으로 `cases/` 후보로 들어오면 사용자가 매번 손으로 묻지 않아도 됨 → 후보 A의 즉시 도입 근거
  - Node.js 20 deprecation 같은 annotation도 자동 캡처되면 만료일(2026-06-02) 전 처리 트리거가 됨

## 4. 반복 가능성

- gwangcheon-shop의 모든 PR이 동일한 5개 워크플로우 패턴을 가짐 → 같은 형태의 캡처가 매 PR마다 발생
- 사용자가 매번 "지금 뭐 돌고 있어?"를 묻는 건 명백히 비효율적
- 영향: 큼 (메인 워크플로우)

## 5. 결정

이 PR에서 처리:

- [x] 양방향 정렬을 **사실로** 박제 (재인용 가능한 이력)
- [x] PR #370 E2E 결과(PASS)를 첫 캡처 사례로 박제
- [x] **case #002 후보 A 도입**: GitHub issue 템플릿 추가 (`.github/ISSUE_TEMPLATE/case-report.md`)
  - 누구든(사용자 또는 후속에 추가될 자동화) issue로 사건을 발행 → orchestrator 측에서 `cases/NNN-*.md`로 변환하는 표준 입구
  - 코드 0줄, 양식만 — 케이스 주도 원칙 준수
- [x] `cases/README.md`에 issue → case 변환 절차 추가
- [x] `cases/002-capture-channel.md`의 상태를 `open` → `partial` 로 (후보 A 도입, B/C 미정)

별도 케이스로 보류:

- [ ] 후보 B (gwangcheon-shop의 cross-repo `repository_dispatch` 워크플로우): 다음 실제 트리거(예: 검증 누락 PR이 머지되려 할 때) 발생 시
- [ ] gwangcheon-shop의 Node.js 20 deprecation 처리: 본 저장소 범위 밖, gwangcheon-shop의 issue로 별도 등록 권장
- [ ] 기존 `bug_report.md` / `feature_request.md`의 폐기 모델 톤("AI Analysis Request" 등) — 별도 정리 케이스

## 6. 후속 작업

- 후보 A의 첫 실사용: 이 케이스 머지 직후, **PR #370 사건을 새 issue 템플릿으로 등록**해 보아 워크플로우 자체를 검증
- 두 번째 실제 사건이 발생하면 후보 B 코드화 케이스 발행 (gwangcheon-shop 워크플로우 추가)

## 7. 학습 (ChromaDB 인덱싱 대상)

오케스트레이터가 1차 적용 대상(gwangcheon-shop)과 정렬되어 있는지의 가장 강한 증거는 **두 저장소의 결정이 같은 시점에 같은 방향으로 머지되는 것**이다. case #000(orchestrator의 "Antigravity = 검증")과 gwangcheon-shop PR #369(`chore/role-flip` "B안")이 같은 날 정렬된 것은 우연이 아니라 같은 사용자의 같은 결정의 두 표면이다. 미래의 결정에서도 한쪽만 박제되고 다른쪽이 비어있는 상태를 발견하면, 그것은 즉시 정렬 대상이다.

또한, 케이스 캡처 채널의 부재(case #002)는 **사용자가 매번 손으로 묻는 형태로 우회된다**. "지금 ci 돌고 있는데 캐치할 수 있나?"라는 질문 자체가 캡처 채널 부재의 비용이다. 후보 A는 그 비용을 0으로 만들지 못하지만, 비용이 발생할 때 들어가는 비공식 경로를 대체하는 표준 입구를 제공한다.
