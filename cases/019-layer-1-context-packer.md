---
id: 012
title: Layer 1 컨텍스트 패커 실체화 — 과거 사고 사례 주입
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: resolved
related_pr: 
related_components: [layer-1-context]
---

# Case 019 — Layer 1 컨텍스트 패커 실체화 — 과거 사고 사례 주입

**TL;DR.** Claude Code가 작업 시작 시 과거의 회귀 사고 사례를 프롬프트에 자동 첨부할 수 있도록 Layer 1 (컨텍스트 패커) API를 구현함. 파일 경로 기반 매칭을 통해 Case #012(의존성), Case #013(테스트) 등의 위험을 사전에 경고함으로써 동일 실수의 반복을 차단함.


## 1. 무슨 일이 있었나 (사실)

title: [CASE] Layer 1 컨텍스트 패커 실체화 — 과거 사고 사례 주입
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- 지휘자 모델의 'Pre-Generation' 단계인 Layer 1 (컨텍스트 패커)이 아직 미구현 상태임.
- Claude Code가 작업을 시작할 때, 해당 도메인에서 과거에 어떤 실수가 있었는지 알지 못해 동일한 패턴의 회귀 사고(Case #012, #013 등)가 반복될 위험이 있음.
- 실측된 사고 사례(`cases/`)들이 ChromaDB에 인덱싱될 준비가 되었으므로, 이를 검색하여 프롬프트에 자동 첨부하는 로직이 필요함.

## 2. 어느 액터/레이어에서 발생했나
- Layer 1 (컨텍스트 패커) 부재.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- 작업 시작 전 "이 파일은 과거에 lock 파일 불일치로 실패한 적이 있습니다"라는 컨텍스트를 주입했다면 Case #012와 같은 실수를 예방할 수 있었음.

## 4. 반복 가능성
- 매 작업 생성 시마다 발생.

## 5. 결정
- [x] (a) decided-implement: Layer 1 실체화 시작.
- [x] (a-1) ChromaDB에서 파일 경로 및 키워드 기반 유사 사례 검색 로직 구현.
- [x] (a-2) 검색된 결과를 Claude Code용 컨텍스트 번들(Markdown)로 패킹하는 API 추가.

## 6. 어디서 보았나 (선택)
- 지휘자 5-레이어 아키텍처 설계

## 7. 학습 (ChromaDB 인덱싱 대상)

[이케이스를 통해 배운 점을 한 문단으로 작성하세요]
