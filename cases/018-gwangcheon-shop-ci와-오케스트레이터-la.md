---
id: 018
title: gwangcheon-shop CI와 오케스트레이터 Layer 4 연동
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: open
related_pr: 
related_components: []
---

# Case 018 — gwangcheon-shop CI와 오케스트레이터 Layer 4 연동

**TL;DR.** [이슈 요약 및 핵심 통찰을 작성하세요]

## 1. 무슨 일이 있었나 (사실)

title: [CASE] gwangcheon-shop CI와 오케스트레이터 Layer 4 연동
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- 오케스트레이터에 Layer 4 (검증 게이트) API가 실체화되었으나, 실제 위성 프로젝트(`gwangcheon-shop`)에서 이를 호출하고 있지 않음.
- 지휘자 모델이 실질적인 효력을 발휘하려면, 위성 프로젝트의 CI 실패/성공 신호가 오케스트레이터로 전달되어야 함.
- 이를 통해 Case #012와 같은 빌드 실패 시 오케스트레이터가 즉각적인 가이드를 제공하는 루프를 완성함.

## 2. 어느 액터/레이어에서 발생했나
- Layer 4 (검증 게이트) 연결부 미비.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- 연동이 완료되면, 향후 `gwangcheon-shop`의 모든 빌드/테스트 결과는 오케스트레이터의 승인을 거쳐야 운영으로 넘어갈 수 있음.

## 4. 반복 가능성
- 지속적 (모든 PR 및 빌드 시)

## 5. 결정
- [x] (a) decided-implement: gwangcheon-shop 워크플로우 수정.
- [x] (a-1) 빌드 실패 시 오케스트레이터 `/verify/gate` 호출 로직 추가.
- [x] (a-2) 분석 결과(결정 및 제안)를 GitHub Action 요약 또는 코멘트로 출력.

## 6. 어디서 보았나 (선택)
- Layer 4 실체화 후속 단계

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
