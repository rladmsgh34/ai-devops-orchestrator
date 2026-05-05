---
id: 015
title: Layer 4 검증 게이트 실체화 — 빌드 및 테스트 보호 (결정 케이스)
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: open
related_pr: 
related_components: []
---

# Case 015 — Layer 4 검증 게이트 실체화 — 빌드 및 테스트 보호 (결정 케이스)

**TL;DR.** [이슈 요약 및 핵심 통찰을 작성하세요]

## 1. 무슨 일이 있었나 (사실)

title: [CASE] Layer 4 검증 게이트 실체화 — 빌드 및 테스트 보호 (결정 케이스)
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- Case #012 (gwangcheon-shop 빌드 실패)와 Case #013 (ai-dev-loop-analyzer 테스트 실패)가 발생함.
- 두 사건 모두 "결함이 있는 코드가 메인 브랜치에 도달"하여 운영/배포 장애를 유발한 공통 패턴을 보임.
- 이는 case #005 트리거 룰(2회 누적)을 충족하며, 지휘자 모델의 Layer 4 (검증 게이트) 실체화가 시급함을 입증함.

## 2. 어느 액터/레이어에서 발생했나
- Layer 4 (검증 게이트) 부재.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- Layer 4에서 PR 머지 전 빌드 무결성 및 스모크 테스트 통과 여부를 강제했다면 두 사고 모두 차단 가능했음.

## 4. 반복 가능성
- 매우 높음 (자동화된 게이트 없이는 지속 발생)

## 5. 결정 (결정 케이스 필수)
- [x] (a) decided-implement: Layer 4 실체화 시작.
- [x] (a-1) langchain-api 및 chromadb 격리 해제 (docker-compose 프로파일 수정).
- [x] (a-2) gwangcheon-shop CI에 오케스트레이터 검증 호출 추가.
- [x] (a-3) 빌드 및 잠재적 회귀 위험 검증 로직 구현.

## 6. 어디서 보았나 (선택)
- Case #012, #013 통합 분석 결과

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
