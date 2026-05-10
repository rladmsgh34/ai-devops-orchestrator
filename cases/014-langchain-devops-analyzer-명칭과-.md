---
id: 014
title: langchain-devops-analyzer 명칭과 실체의 괴리 (Honesty)
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: resolved
related_pr: 
related_components: [naming, honesty]
---

# Case 014 — devops-error-analyzer 명칭과 실체의 괴리 해결 (Honesty)

**TL;DR.** 실제 LangChain을 사용하지 않음에도 이름에 포함되어 있던 `langchain-devops-analyzer`를 `devops-error-analyzer`로 개명하고, 지휘자(Conductor) 모델의 전문 위성 모듈로서의 정체성을 README 및 API 명세에 반영함.

## 1. 무슨 일이 있었나 (사실)

title: [CASE] langchain-devops-analyzer 명칭과 실체의 괴리 (Honesty)
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- rladmsgh34/langchain-devops-analyzer 저장소의 이름에 "LangChain"이 포함되어 있음.
- 그러나 실제 코드에는 LangChain 라이브러리 연동이나 LLM 활용 로직이 없으며, 로컬 임베딩과 ChromaDB만 사용 중임.
- 이는 Case #007/009의 "Unbacked Self-Claim" 패턴과 유사함. 단, README에 "현재는 포함되어 있지 않음"이라고 명시되어 있어 정직성 시그널은 존재함.

## 2. 어느 액터/레이어에서 발생했나
- 메타 (명명 정책)

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- 지휘자 모델로 통합 시, 해당 모듈을 "LangChain 기반"으로 소개하기 전 실제 구현을 강제하거나 명칭을 "devops-error-analyzer" 등으로 정정할 필요가 있음.

## 4. 반복 가능성
- 중간 (미래 로드맵을 이름에 미리 반영하는 습관)

## 5. 어디서 보았나 (선택)
- 위성 프로젝트 분석 중 발견

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
