---
id: 001
title: 폐기 모델의 잔존 청구·ghost 서비스 정리
date: 2026-05-01
project: ai-devops-orchestrator (메타)
actor_involved: [orchestrator]
state: resolved
related_pr: case/001-purge-legacy-claims
related_components: [meta]
---

# Case 001 — 폐기 모델 잔존물 정리

## 1. 무슨 일이 있었나 (사실)

- 2026-05-01, case #000으로 오케스트레이터를 지휘자 모델로 재정의하고 README 본문(#4)을 정리했음
- 정리 직후 점검에서, 폐기 모델의 잔존 청구·구성이 다른 파일에 그대로 남아있음을 확인:
  - `CHANGELOG.md`: "세계 최초 자기 학습하는 DevOps AI", "디버깅 시간 1-2시간 → 5분 (2400% 효율 향상)", "AI 정확도 33% → 95%+", "전 세계 기여: 2천만 시간 절약 예상", "$20억 기대효과", "v2.0.0 미래: AI 기반 자동 수정 PR 생성" 등 — README에서 제거된 청구가 그대로
  - `docker-compose.yml`: `nginx` 서비스가 `./nginx/nginx.conf`와 `./nginx/ssl`을 마운트하지만 `nginx/` 디렉토리는 비어있음 → `docker-compose up -d` 시 마운트 실패하는 ghost 서비스
- 사용자가 점검에서 "현재 프로세스 문제점"을 물었고, 위 잔존물이 첫 항목으로 식별됨

## 2. 어느 액터/레이어에서 발생했나

메타 케이스 — 액터 경계 외부의 정직성 문제. 이 저장소가 외부에 노출하는 표면(README/CHANGELOG/compose)이 자기모순 상태였음.

## 3. 오케스트레이터가 막거나 도울 수 있었는가

해당 없음 (메타 케이스). 다만 향후 비슷한 청구가 새로 추가될 때를 대비해, "외부 표면 변경은 cases/ 근거 없으면 PR 차단"을 Layer 4 검증 게이트의 가드로 두는 안 검토 가능 (별도 케이스 발생 시).

## 4. 반복 가능성

- 동일 케이스 재발: 낮음 (잔존물은 한 번에 식별되어 정리됨)
- 영향: 중간 (외부에서 본 저장소를 처음 볼 때 정직성 평가에 직접 영향)

## 5. 결정

이 PR에서 처리:

- [x] `CHANGELOG.md` 재작성: 폐기된 v1.0.0 청구를 사실대로 표기 + 지휘자 모델 재정의(2026-05-01)를 명시
- [x] `docker-compose.yml`에서 `nginx` 서비스 제거 (디렉토리 비어 있어 실행 불가)
- [x] 빈 `nginx/` 디렉토리 제거

별도 케이스로 보류:

- [ ] `services/langchain-api/main.py`의 키워드 매칭 응답에 남은 `estimated_time_saved` 같은 청구성 필드 정리 (지휘자 모델 첫 컴포넌트 코드화 시 함께)
- [ ] `services/n8n-workflows/github-integration.json` 검토 (Auto-Fix PR 흐름이면 폐기 대상)
- [ ] `monitoring/`, `prometheus/grafana/elastic/kibana/logstash` profile 서비스 — 현재 profile-gated라 기본 실행되지 않음. 지휘자 모델에서 어느 레이어에 연결할지 결정될 때 정리

## 6. 후속 작업

- case #002에서 케이스 캡처 메커니즘을 정의 (이 case는 사용자 점검으로 발견됐지만, 일반적 발견 경로가 없는 게 다음 문제)

## 7. 학습 (ChromaDB 인덱싱 대상)

이 저장소가 외부에 노출하는 모든 표면(README, CHANGELOG, docker-compose, /docs)은 동일한 모델을 가리켜야 한다. 한 곳을 정리하면 다른 곳도 같은 PR이나 즉시 이은 PR에서 따라잡아야 자기모순이 누적되지 않는다. "이 저장소를 처음 보는 사람이 받게 될 인상이 일관된가"가 정직성 자기 점검의 기준이다.
