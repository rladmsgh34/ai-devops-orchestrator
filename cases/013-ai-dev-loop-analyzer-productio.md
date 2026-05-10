---
id: 013
title: ai-dev-loop-analyzer Production Smoke 테스트 실패
date: 2026-05-05
project: gwangcheon-shop
actor_involved: [user]
state: resolved
related_pr: 
related_components: [smoke-test, ci-cd]
---

# Case 013 — ai-dev-loop-analyzer Production Smoke 테스트 실패

**TL;DR.** `smoke.yml` 워크플로우에서 호출하는 `./web/scripts/smoke.sh` 파일이 존재하지 않아 정기 테스트가 실패함. `scripts/smoke.sh`를 생성하고 워크플로우 경로를 수정하여 운영 환경의 가용성 체크가 정상적으로 수행되도록 조치함.

## 1. 무슨 일이 있었나 (사실)

title: [CASE] ai-dev-loop-analyzer Production Smoke 테스트 실패
labels: case-candidate

## 1. 사실 (무슨 일이 있었나)
- 2026-05-05 UTC, ai-dev-loop-analyzer의 정기 스케줄 워크플로우("Production Smoke") 실패.
- 최근 24시간 내 여러 차례 반복적으로 실패 중 (Run ID 25364491480 등).
- 이는 운영 환경의 엔드포인트가 응답하지 않거나, 최근 변경된 규칙이 실제 환경과 충돌하고 있음을 시사함.

## 2. 어느 액터/레이어에서 발생했나
- 운영/인프라 이슈 또는 최근 규칙 진화("Evolve Rules") 과정에서의 사이드 이펙트.

## 3. 오케스트레이터가 막거나 도울 수 있었는가
- Layer 5 (배포 게이트)에서 배포 직후 Smoke 테스트가 통과하는지 확인하고 자동 롤백했다면 운영 영향을 줄일 수 있었음.

## 4. 반복 가능성
- 중간 (배포 후 안정성 검증 채널)

## 5. 어디서 보았나 (선택)
- GitHub Actions 스케줄 워크플로우 실패 관찰

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
