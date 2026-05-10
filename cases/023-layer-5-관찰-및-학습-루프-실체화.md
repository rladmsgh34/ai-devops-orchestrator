---
id: 023
title: Layer 5 관찰 및 학습 루프 실체화 — SLI 기반 검증 및 지식 환류
date: 2026-05-10
project: ai-devops-orchestrator
actor_involved: [orchestrator]
state: proposed
related_pr: 
related_components: [layer-5-observation, chromadb-feedback]
---

# Case 023 — Layer 5 관찰 및 학습 루프 실체화 — SLI 기반 검증 및 지식 환류

**TL;DR.** 배포 후 상태(Observed)를 SLI 지표로 검증하고, 성공 및 실패 사례를 ChromaDB로 자동 환류하여 다음 개발 시 Layer 1에서 참고할 수 있도록 함.

## 1. 무슨 일이 있었나 (사실)

- Layer 5의 승인 게이트(`approved`)는 구현되었으나, 배포 완료(`deployed`) 후의 관찰(`observed`) 및 학습(`archived`) 단계가 구체화되지 않음.
- 배포 성공/실패 여부를 판단하는 구체적인 SLI(에러율, 레이턴시 등) 기준과 이를 측정하여 상태를 전이시키는 로직이 필요함.
- `observed` 단계를 통과한 성공 사례나, `rolled-back`된 실패 사례를 ChromaDB에 자동으로 인덱싱하여 오케스트레이터의 지식 베이스를 확장해야 함.

## 2. 어느 액터/레이어에서 발생했나
- Layer 5 (관찰 및 배포 후 처리) 미구현.
- ChromaDB 학습 환류(Feedback Loop) 미구현.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- 배포 후 관찰 기간 동안 메트릭을 감시하고, 이상 징후 시 자동 롤백을 수행하여 운영 안정성을 높일 수 있음.
- 경험을 데이터화(ChromaDB)하여 동일한 실수를 방지(Layer 1)하도록 도움.

## 5. 결정
- [x] (a) decided-implement: Layer 5 관찰(Observed) 및 학습 엔드포인트 구현.
- [x] (a-1) SLI 지표(Error Rate, p95 Latency)를 수신하고 판단하는 `/verify/observe` 엔드포인트 추가.
- [x] (a-2) 관찰 성공 시 또는 배포 실패 시 해당 맥락을 ChromaDB에 저장하는 `/learn/record` 엔드포인트 구현.
- [x] (a-3) `scripts/ingest_case.py` 및 `scripts/index_cases.py`와 연동 가능한 학습 구조 마련.

## 7. 학습 (ChromaDB 인덱싱 대상)

배포는 단순히 코드가 서버에 올라가는 것으로 끝나지 않는다. 관찰 기간 동안 실질적인 서비스 지표(SLI)를 통해 안정성을 증명하고, 그 과정에서 얻은 데이터(성공/실패 사례)를 지식화하여 다음 개발의 밑거름으로 삼는 '폐쇄형 루프(Closed-Loop)'를 구축하는 것이 오케스트레이터의 최종 목표다.
