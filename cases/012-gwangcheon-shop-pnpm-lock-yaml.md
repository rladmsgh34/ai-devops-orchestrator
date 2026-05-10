---
id: 012
title: gwangcheon-shop pnpm-lock.yaml 불일치로 인한 빌드 실패
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: resolved
related_pr: 
related_components: [build-pipeline]
---

# Case 012 — gwangcheon-shop pnpm-lock.yaml 불일치로 인한 빌드 실패

**TL;DR.** `pnpm-lock.yaml`이 `package.json`과 동기화되지 않아 Docker 빌드 시 `frozen-lockfile` 검증에서 실패함. `pnpm install --lockfile-only`를 통해 lock 파일을 갱신하고 머지하여 배포 파이프라인을 복구함.

## 1. 무슨 일이 있었나 (사실)

title: [CASE] gwangcheon-shop pnpm-lock.yaml 불일치로 인한 빌드 실패
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- 2026-05-04 UTC, gwangcheon-shop PR 머지 후 배포 워크플로우("Deploy") 실패.
- 실패 원인: Docker Build 중 `pnpm install --frozen-lockfile`이 exit code 1로 종료됨.
- 이는 `pnpm-lock.yaml`이 `package.json`의 변경 사항을 반영하지 못해 동기화가 깨졌을 가능성이 큼.

## 2. 어느 액터/레이어에서 발생했나
- Claude Code 또는 사용자가 의존성을 추가/변경하면서 lock 파일 갱신을 누락함 (생성 단계 결함).

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- Layer 4 (검증 게이트)에서 PR 머지 전 `pnpm install --frozen-lockfile`이 통과하는지 확인했다면 차단 가능했음.
- Layer 3 (컨텍스트 패킹)에서 의존성 변경 감지 시 "lock 파일을 잊지 마세요" 경고 주입 가능.

## 4. 반복 가능성
- 높음 (의존성 관리 시 빈번히 발생)

## 5. 어디서 보았나 (선택)
- GitHub Actions 워크플로우 실패 관찰 (Run ID 25321242112)

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
