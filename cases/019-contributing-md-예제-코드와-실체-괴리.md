---
id: 019
title: CONTRIBUTING.md 예제 코드와 실체 괴리
date: 2026-05-05
project: ai-devops-orchestrator
actor_involved: [user]
state: resolved
related_pr: 
related_components: [docs]
---

# Case 019 — CONTRIBUTING.md 예제 코드와 실체 괴리

**TL;DR.** `CONTRIBUTING.md`에 남아 있던 구버전(AI 에이전트 자동 수정 모델)의 예제 코드를 제거하고, 새 지휘자(Conductor) 모델 및 케이스 주도 원칙에 맞춰 문서를 동기화함. 문서의 정직성을 회복하고 기여자 혼란을 차단함.

## 1. 무슨 일이 있었나 (사실)

- 2026-05-05, 프로젝트 분석 중 `CONTRIBUTING.md`의 코드 예제가 실제 코드(`main.py`) 및 현재 아키텍처와 정면 충돌하는 것을 발견.
- `async def analyze_error_pattern` 등 폐기된 모델의 인터페이스가 기여 가이드로 제시되고 있었음.

## 5. 결정

- [x] 문서 동기화 (CONTRIBUTING.md 수정)

## 6. 후속 작업

- 없음.

## 7. 학습 (ChromaDB 인덱싱 대상)

아키텍처 대전환(`v1.0.0` 지휘자 모델 재정의) 시, 핵심 척추 문서(`CLAUDE.md`, `ARCHITECTURE.md`) 외에도 기여자 가이드(`CONTRIBUTING.md`)와 같은 주변부 문서의 예제 코드가 구버전의 유령(ghost)으로 남을 수 있다. 이는 기여자에게 잘못된 인터페이스를 학습시키는 위험이 있으므로, 주요 결정 시 동기화 범위를 전수 점검해야 한다.
