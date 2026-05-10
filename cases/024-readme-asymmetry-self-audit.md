---
id: 021
title: README와 코드 실체 비대칭 사건 (Self-Audit)
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: closed
related_pr: 
---

# Case 021 — README와 코드 실체 비대칭 사건 (Self-Audit)

**TL;DR.** 지휘자 모델의 정직성(Honesty)을 확보하기 위해 README의 상태 선언을 실제 코드 구현 수준에 맞게 정정하고, 상태 정의를 명문화함.

## 1. 무슨 일이 있었나 (사실)

- 2026-05-05, 자가 점검 결과 README의 상태 ✅가 실제 코드 구현(`🏗️ 실체화 진행 중`) 및 검증 수준과 괴리가 있음을 확인.
- 특히 Layer 1, 3, 4가 하드코딩이나 API 엔드포인트만 존재하는 단계였으나 ✅로 표시됨.

## 5. 결정
- [x] (a) decided-implement: README 상태 기호 정의 명문화 (CLAUDE.md). (완료: 2026-05-08)
- [x] (b) decided-implement: Layer 1, 3, 4 상태를 🏗️(실체화 진행 중)로 정정. (완료: 2026-05-08)
- [x] (c) decided-implement: 향후 상태 변경 시 검증 근거(어떤 입력 -> 어떤 출력) 기록 의무화. (완료: 2026-05-08)
- [x] (d) decided-implement: Layer 4 검증 게이트 리팩토링 및 G2/G3 가드 실체화 시작. (완료: 2026-05-08)

## 7. 학습 (ChromaDB 인덱싱 대상)
'연결(Connect) ≠ 구현(Implement) ≠ 검증(Validate)'은 서로 다른 단계다. 파이프를 놓는 것과 물이 흐르는 것은 별개이며, 물이 깨끗한지 확인하는 것은 또 다른 단계다. 지휘자 모델은 타인의 코드를 지휘하기 전, 자기 자신의 주장이 사실과 일치하는지 점검하는 정직성 파이프라인을 가장 먼저 갖춰야 한다. 이 자가 점검 자체가 프로젝트의 환류 루프가 작동한 첫 실전 사례다.

## 7. 학습 (ChromaDB 인덱싱 대상)

[이케이스를 통해 배운 점을 한 문단으로 작성하세요]
