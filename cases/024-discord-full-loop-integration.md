---
id: 024
title: Discord 연동 및 풀 루프 자동화 (Notification Loop)
date: 2026-05-09
project: ai-devops-orchestrator
actor_involved: [user, orchestrator, github-actions, discord-bot]
state: closed
related_pr: 
related_components: [discord-bot, langchain-api, github-workflow]
---

# Case 024 — Discord 연동 및 풀 루프 자동화 (Notification Loop)

**TL;DR.** 사용자가 Discord에서 명령을 내리고 결과를 받을 수 있도록 전체 파이프라인(Discord -> API -> GitHub -> Discord)을 연결함.

## 1. 무슨 일이 있었나 (사실)
- 사용자가 Discord를 통한 제어 및 결과 보고 요구.
- 기존의 로컬 서브프로세스 방식으로는 Discord와의 실시간 상호작용 및 긴 작업 시간 처리에 한계가 있었음.

## 2. 해결 방법 (구현 완료)
- **명령(Command)**: `scripts/discord_bot.py`를 통해 Discord 슬래시 명령어(`/develop`) 지원.
- **실행(Action)**: GitHub Actions(`.github/workflows/full-loop-agent.yml`)로 무거운 작업(Claude Code) 이관.
- **결과(Notification)**: GitHub Action 완료 시 Discord Webhook을 호출하여 작업 결과를 채널에 다시 알림.

## 3. 학습
- 긴 시간이 소요되는 AI 에이전트 작업은 **비동기 워크플로(GitHub Actions)**와 **상태 알림 브릿지(Discord Bot/Webhook)**의 조합이 가장 안정적이다.
- 지휘자(Orchestrator)는 이 과정에서 **과거 맥락(ChromaDB)**을 끄집어내어 에이전트에게 전달하는 '두뇌' 역할을 충실히 수행한다.
