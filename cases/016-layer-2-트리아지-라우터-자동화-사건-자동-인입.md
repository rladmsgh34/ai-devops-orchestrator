---
id: 016
title: Layer 2 트리아지 라우터 자동화 — 사건 자동 인입
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: open
related_pr: 
related_components: []
---

# Case 016 — Layer 2 트리아지 라우터 자동화 — 사건 자동 인입

**TL;DR.** Case #002 후보 A(수동 발행 + ingest_case.py)는 사람이 직접 로그 복사 필요. 위성 프로젝트 사건이 빈번해져 자동 감지가 필요해짐. (a) Layer 2 자동 인입 채널(후보 B) 결정 — `repository_dispatch` 수신 워크플로우 + `ingest_case.py` 자동 호출 + 광천샵 dispatch 가이드 작성.

## 1. 무슨 일이 있었나 (사실)

title: [CASE] Layer 2 트리아지 라우터 자동화 — 사건 자동 인입
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- Case #002 (캡처 채널 부재) 해결을 위해 도입된 '수동 발행 + ingest_case.py'는 여전히 사람이 직접 로그를 복사해야 하는 단계임.
- 위성 프로젝트(gwangcheon-shop 등)에서 사고가 빈번해짐에 따라, 이를 오케스트레이터가 자동으로 감지하고 박제할 필요가 있음.
- 이는 Layer 2 (트리아지 라우터)의 핵심 기능인 "알림 분류 및 라우팅"의 첫 실체화가 될 것임.

## 2. 어느 액터/레이어에서 발생했나
- Layer 2 (트리아지 라우터) 자동화 미비.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- 자동 인입 채널이 있었다면 Case #012, #013의 기록 지연을 없애고 즉각적인 분석 및 대응이 가능했음.

## 4. 반복 가능성
- 높음 (수동 기록은 누락 위험이 상존함)

## 5. 결정 (결정 케이스 필수)
- [x] (a) decided-implement: Layer 2 자동 인입 채널(후보 B) 구현.
- [x] (a-1) GitHub `repository_dispatch` 수신 워크플로우 추가.
- [x] (a-2) 수신된 페이로드를 `scripts/ingest_case.py`에 전달하여 자동 박제.
- [x] (a-3) 위성 프로젝트(gwangcheon-shop) CI 실패 시 오케스트레이터로 디스패치하는 가이드 작성.

## 6. 어디서 보았나 (선택)
- Case #002 권장사항(후보 B) 이행

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
