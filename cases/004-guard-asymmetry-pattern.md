---
id: 004
title: 가드 비대칭(Guard Asymmetry) — admin/user 라우트 도메인 룰 한쪽 누락 패턴
date: 2026-05-01
project: gwangcheon-shop (사건 발원지) / ai-devops-orchestrator (캡처)
actor_involved: [claude-code, antigravity, orchestrator]
state: observing
related_pr: case/004-guard-asymmetry-pattern
related_components: [layer-3-packing, layer-4-verify-gate]
references:
  - orchestrator issue https://github.com/rladmsgh34/ai-devops-orchestrator/issues/10
  - gwangcheon-shop issue https://github.com/rladmsgh34/gwangcheon-shop/issues/365
  - gwangcheon-shop issue https://github.com/rladmsgh34/gwangcheon-shop/issues/371
---

# Case 004 — 가드 비대칭(Guard Asymmetry) 결함 패턴

> case #003에서 도입한 후보 A 채널(GitHub issue 템플릿)의 두 번째 실사용이자, **첫 번째 진짜 결함 박제**.
> #003은 정상 흐름의 캡처였고, 이건 결함 패턴의 캡처. 캡처 채널이 실제 가치를 만들기 시작한 첫 사례.

## 1. 무슨 일이 있었나 (사실)

- 2026-05-01, gwangcheon-shop 이슈 #365 (운영자 E2E 셀프 테스트)의 **Track A — 사전 코드 검증** 정적 분석 중, 주문 생성/취소 흐름에서 4개 결함이 한 라우트에 동시에 누락된 채 발견됨:
  - **C-1**: 사용자 측 `POST /api/orders` (`src/app/api/orders/route.ts:82-92`) — `isVisible=false` 상품 주문 가능
  - **C-2**: 같은 라우트 — 재고 부족 가드 없음
  - **C-3**: 같은 라우트 (line 124-141) — `Product.stock` 차감 누락
  - **추가**: 사용자 측 `POST /api/orders/[id]/cancel` (`src/app/api/orders/[id]/cancel/route.ts:50-59`) — 재고 복구 누락
- **대조**: 같은 도메인 책임을 다루는 관리자 측 라우트는 모두 갖춤
  - `src/app/api/admin/orders/route.ts:166-181` — 수동 주문: stock decrement + logStockChange
  - `src/app/api/admin/orders/[id]/route.ts:184-227` — PATCH: `canTransition` + `isStockRestoringTransition` + Payment 동기화
- 이 결함들은 gwangcheon-shop 이슈 #371 로 발행됨 (PR 후보)
- gwangcheon-shop의 5개 워크플로우(CI / Security Review / Copilot Review / E2E / Deploy) **모두 이 비대칭을 잡지 못함**

## 2. 어느 액터/레이어에서 발생했나

- **결함 자체**: Claude Code의 **생성 시점** — 같은 도메인 룰(`isVisible`, 재고 차감/복구, 상태 전이)을 admin/user 두 라우트에서 따로 구현하면서 한쪽만 누락
- **검증 측면**: Antigravity가 **도메인 룰의 양방향(admin ↔ user) 일관성**을 점검하는 패턴이 없었음. 단일 라우트의 정합성만 봄
- **오케스트레이터 측면**: **Layer 3(컨텍스트 패킹)** 이 "관련 라우트 번들"을 식별해 동시에 검증 대상으로 묶지 못함. 한 라우트만 변경 컨텍스트로 들어가니, 검증자도 한쪽만 봄

## 3. 오케스트레이터가 막거나 도울 수 있었는가

- [x] Layer 1 (컨텍스트 주입) — 사전 방지 가능? 부분적 (생성자 프롬프트에 "형제 라우트 점검" 힌트로)
- [ ] Layer 2 (트리아지) — 본 결함은 라우팅 문제가 아님
- [x] Layer 3 (컨텍스트 패킹) — **가장 강력한 위치**. 변경 라우트와 같은 도메인을 다루는 형제 라우트들(같은 모델 수정/조회, 같은 lib 함수 호출)을 자동 식별해 검증 컨텍스트에 포함
- [x] Layer 4 (검증 게이트) — 새로 추가된 도메인 룰(예: `isStockRestoringTransition`)이 도입되면, 같은 도메인 모델을 만지는 모든 라우트에서 그 룰의 적용 여부를 점검하도록 Antigravity에 힌트
- [ ] Layer 5 (승인/배포 게이트) — 너무 늦음
- [ ] 어디서도 못 막음 — 해당 없음

> 단, 이 케이스 **단독으로는** 코드화하지 않는다. 같은 패턴이 누적될 때 첫 코드화 트리거가 된다 (case #002 후보 B 누적과 함께).

## 4. 반복 가능성

- **매우 높음**. gwangcheon-shop 코드베이스 전반에 admin vs 사용자 라우트 분리가 거의 모든 모듈에 존재 (products, orders, reviews, wishlist, ...)
- 새 도메인 룰 추가 시마다 한쪽 누락 가능성
- **영향**: 큼 — 보안 가드면 즉시 우회 가능, 데이터 무결성 가드면 운영 데이터 손상

### 같은 패턴이 또 발견될 수 있는 예측 영역

- **products** 공개/관리자 측 (이번엔 `isVisible` 잘 됐지만, 새 가드 추가 시 위험)
- **wishlist** 공개/관리자 측
- **reviews** — 이미 한 결함 발견됨 (중복 방지, gwangcheon-shop #372)

## 5. 결정

이 PR에서 처리:

- [x] 결함 패턴을 **사실로** 박제 (재인용 가능한 이력)
- [x] 인덱스 갱신 (`cases/README.md`)
- [x] orchestrator issue #10 close

별도 케이스/PR로 보류:

- [ ] **Layer 3 컨텍스트 패커 코드화 트리거 대기** — 본 케이스 단독으로는 가설. case #002 후보 B(자동 dispatch) + 두 번째 가드 비대칭 발견이 누적되면 그때 코드화 케이스 발행
- [ ] gwangcheon-shop 측 결함 수정은 **gwangcheon-shop #371**에서 별도 처리 (오케스트레이터 범위 밖)
- [ ] reviews 도메인의 동일 패턴(gwangcheon-shop #372) 추적 — 두 번째 인스턴스가 되면 누적 카운트로 사용

## 6. 후속 작업

- 본 케이스 머지 후, 다음 비대칭 사례가 또 발견되면 **case #005 (또는 그 이상)에서 패턴이 두 번 이상 발생함을 박제** → Layer 3 컨텍스트 패커의 첫 코드화 케이스 발행
- 가드 비대칭 점검 룰은 사용자 메모리에 이미 박제되어 있음(`feedback_guard_symmetry.md`) — gwangcheon-shop 라우트 작업 시 admin/user 양쪽 가드 대칭 점검은 이미 운영 룰

## 7. 학습 (ChromaDB 인덱싱 대상)

gwangcheon-shop 같이 admin/user 두 도메인 라우트를 별도로 두는 코드베이스에서, **새 도메인 룰(가시성·재고·상태 전이 등)이 추가될 때 한쪽 라우트만 갱신되는 비대칭 결함이 매우 자주 발생한다**. 단일 라우트만 보는 검증(빌드/유닛/E2E 시나리오)은 이 비대칭을 거의 잡지 못한다. 라우트 번들(같은 모델/같은 lib을 다루는 형제 라우트 집합)을 검증 컨텍스트로 묶는 것이 가장 효과적인 방어선이며, 이는 오케스트레이터의 Layer 3(컨텍스트 패킹) 책임이다. 단, 이 결론은 두 번째 인스턴스가 박제될 때까지 가설로 둔다 — 케이스 주도 원칙에 따라.
