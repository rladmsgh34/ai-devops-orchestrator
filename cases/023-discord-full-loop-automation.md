---
id: 023
title: Discord 기반 풀 루프 자동화 요청 (Vibe Coding)
date: 2026-05-08
project: ai-devops-orchestrator
actor_involved: [user, orchestrator]
state: open
related_pr: 
related_components: [discord-integration, planning-agent]
---

# Case 023 — Discord 기반 풀 루프 자동화 요청 (Vibe Coding)

**TL;DR.** 지휘자(Conductor) 모델의 범위를 넘어서, 이슈 생성 → 개발 → PR 생성 → 배포에 이르는 전체 라이프사이클을 자동화하고, 이를 Discord로 제어하고자 하는 요구사항 발생.

## 1. 무슨 일이 있었나 (사실)
- 사용자가 Discord를 통한 단순 조회/보고 기능을 넘어, "이슈 직접 등록 → 개발 → PR 생성 → 배포" 프로세스의 자동화를 요청함.
- 이는 `ARCHITECTURE.md`에서 정의한 "오케스트레이터는 코드를 만들지 않는다(DO NOT: AI가 자동으로 수정 PR 생성)"는 원칙과 정면으로 충돌함.

## 2. 결함 분석 (패러다임 충돌)
- 현재 아키텍처는 **Claude Code가 코드를 짜고**, 지휘자는 **가드레일만 제공**하는 형태임.
- 사용자의 요구는 지휘자가 Claude Code의 역할(개발, PR 생성)까지 **직접 호출하거나 대행**하는 '풀 자동화 에이전트'로 확장되기를 원함.

## 3. 해결 방향 (바이브 코딩)
이 요구를 수용하기 위해서는 기존 원칙(`CLAUDE.md`)을 수정하거나, 지휘자가 Claude Code를 **명령줄(CLI)로 직접 구동시키는 파이프라인**을 구축해야 함.

## 7. 학습 (ChromaDB 인덱싱 대상)
사용자가 진정으로 원하는 것은 '안전한 가드레일'을 넘어서 '손안대는 자동화'다. 지휘자 모델은 멈춰있는 신호등이 아니라, 생성 AI(Claude Code)의 엑셀러레이터를 대신 밟아주는 자율주행 모터가 되어야 한다.
