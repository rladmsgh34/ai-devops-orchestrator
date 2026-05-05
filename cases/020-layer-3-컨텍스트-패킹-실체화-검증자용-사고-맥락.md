---
id: 020
title: Layer 3 컨텍스트 패킹 실체화 — 검증자용 사고 맥락 번들링
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: open
related_pr: 
related_components: []
---

# Case 020 — Layer 3 컨텍스트 패킹 실체화 — 검증자용 사고 맥락 번들링

**TL;DR.** [이슈 요약 및 핵심 통찰을 작성하세요]

## 1. 무슨 일이 있었나 (사실)

title: [CASE] Layer 3 컨텍스트 패킹 실체화 — 검증자용 사고 맥락 번들링
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- Claude Code가 PR을 생성한 후, 검증자(Antigravity 또는 Gemini)가 해당 PR의 변경 사항이 과거에 발생했던 장애와 연관이 있는지 판단하기 위한 정보가 부족함.
- Layer 1(Pre-Generation)이 개발자에게 정보를 준다면, Layer 3(Generation -> Verification)은 검증자에게 정보를 주어 '과거에 틀렸던 곳을 또 틀리지 않았는지' 집중 점검하게 해야 함.
- 현재 `gwangcheon-shop`의 PR 워크플로우에서 이러한 '사고 맥락 번들'이 누락되어 검증의 정밀도가 떨어짐.

## 2. 어느 액터/레이어에서 발생했나
- Layer 3 (컨텍스트 패킹) 미구현.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- Layer 3에서 "이 PR이 수정한 파일은 과거에 pnpm-lock 불일치(Case #012)가 빈번했던 곳입니다"라는 맥락을 검증자에게 전달했다면 더 정밀한 검증이 가능했음.

## 4. 반복 가능성
- 모든 PR 검증 요청 시마다 발생.

## 5. 결정
- [x] (a) decided-implement: Layer 3 실체화 시작.
- [x] (a-1) PR diff 및 변경 파일 목록을 입력받아 ChromaDB에서 관련 사고 사례를 추출하는 API 구현.
- [x] (a-2) 추출된 정보를 검증자가 읽기 좋은 'Verification Context Bundle' 형식으로 패킹.

## 6. 어디서 보았나 (선택)
- 지휘자 5-레이어 아키텍처 설계

## 7. 학습 (ChromaDB 인덱싱 대상)

[이케이스를 통해 배운 점을 한 문단으로 작성하세요]
