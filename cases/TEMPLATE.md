---
id: NNN
title: <한 줄 제목>
date: YYYY-MM-DD
project: gwangcheon-shop
actor_involved: [claude-code | antigravity | user | runtime | orchestrator]
state: open | resolved | observing | wontfix
related_pr: <PR URL or 없음>
related_components: [layer-1-context | layer-2-triage | layer-3-packing | layer-4-verify-gate | layer-5-approve-deploy | chromadb | n8n]
---

# Case NNN — <제목>

**TL;DR.** <한 문단(2~3문장) 요약. 사건 + 학습의 핵심. ChromaDB 미구현 상태에서 사실상 검색 표면이다 — case #008 결정.>

> §1~§7은 **선택**. TL;DR로 충분하면 §8(학습)만 채우고 나머지는 생략 가능 (case #008).
> 결정 케이스(`state: pending-decision`)는 §4 옵션·§5 사용자 결정이 **필수**.

## 1. 무슨 일이 있었나 (사실)

<시간 순서대로 일어난 일만. 해석·의견은 다음 절에서.>

## 2. 어느 액터/레이어에서 발생했나

<Claude Code 생성 단계? Antigravity 검증 누락? 사용자 승인 우회? 운영 런타임?>

## 3. 오케스트레이터가 막거나 도울 수 있었는가

- [ ] Layer 1 (컨텍스트 주입)에서 사전 방지 가능?
- [ ] Layer 2 (트리아지)에서 올바른 액터로 라우팅 가능?
- [ ] Layer 3 (컨텍스트 패킹)에서 검증자에게 정보 추가 가능?
- [ ] Layer 4 (검증 게이트)에서 차단 가능?
- [ ] Layer 5 (승인/배포 게이트)에서 차단 가능?
- [ ] 어디에서도 못 막음 — 액터의 본질적 책임

## 4. 반복 가능성

- 같은 케이스가 다시 발생할 확률: 낮음 / 중간 / 높음
- 발생 시 영향: 작음 / 중간 / 큼

## 5. 결정

- [ ] 기록만 (반복 가능성 낮음)
- [ ] 컴포넌트 신규 작성 (어느 레이어, 무엇)
- [ ] 기존 컴포넌트 확장 (어느 컴포넌트, 어떻게)
- [ ] 사용자 결정 대기

## 6. 후속 작업

<있다면 PR 링크, 없으면 "없음">

## 7. 학습 (ChromaDB 인덱싱 대상)

<이 케이스를 한 문단 요약. 다음 유사 작업 시 컨텍스트로 자동 첨부될 텍스트.>
