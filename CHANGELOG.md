# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Semantic Versioning은 지휘자 모델 첫 릴리즈 이후에 다시 도입합니다.

## [Unreleased] — 지휘자(Conductor) 모델 재정의

### Changed

- **포지션 재정의**: "AI 6개 에이전트가 자동 분석·수정 PR을 만든다"는 v1.0.0 모델을 폐기. Claude Code(생성) → Antigravity(검증) → 사용자(승인) 세 액터를 잇는 **지휘자(conductor)** 모델로 전환.
- **컴포넌트 매트릭스 결정** ([`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)):
  - 제거: Security Scanner, Code Quality Enforcer, Auto-Fix PR (Antigravity와 충돌)
  - 유지: Error Analyzer(분석만), Performance Detector, Infra Monitor, Deploy Orchestrator
  - 신규: 컨텍스트 패커, 승인 상태머신, 트리아지 라우터, 케이스 로그
- **케이스 주도 개선 원칙 도입** ([`cases/`](./cases)): 새 컴포넌트는 실제 발생 케이스를 근거로만 코드화. 가설 기반 기능 추가 금지.

### Added

- `CLAUDE.md` — 프로젝트 운영 규칙 (DO/DON'T, 액터 경계)
- `docs/ARCHITECTURE.md` — 지휘자 5-레이어 모델, 컴포넌트 매트릭스
- `docs/PIPELINE_STATES.md` — `created → verified → approved → deployed → observed` 상태머신 (스펙)
- `cases/{README,TEMPLATE}.md` + `cases/000-bootstrap.md`, `cases/001-purge-legacy-claims.md`
- 최소 CI: ruff lint + docker-compose syntax + YAML lint (PR 트리거 한정)
- master branch protection: required status checks + force push 차단

### Removed

- `nginx` 서비스 (docker-compose.yml) — `nginx/` 디렉토리가 비어 있어 실제로는 실행 불가능했던 ghost 서비스
- `nginx/` 빈 디렉토리

### Deprecated (후속 케이스에서 정리)

- `services/langchain-api/main.py`의 키워드 매칭 데모 (`/analyze`, `/learn-success`, `/analyze-failure`) — 지휘자 모델 첫 컴포넌트 구현 시 함께 재작성
- `services/n8n-workflows/github-integration.json` — Auto-Fix PR 흐름 검토 후 결정
- `monitoring/`, `prometheus/grafana/elastic/kibana/logstash` profile 서비스 — 지휘자 5-레이어 매핑 결정 시 정리

---

## [1.0.0] — 2026-04-28 (Superseded)

> ⚠️ 이 릴리즈의 청구·성과 지표는 검증된 근거가 없어 폐기되었습니다.
> case #000(2026-05-01) 참조. 이력 추적용으로만 보존하며, 향후 어떤 결정의 근거로도 인용하지 마세요.

폐기된 청구의 예 (전체 목록은 git log `e17528a..2303830` 참조):

- "세계 최초 자기 학습하는 DevOps AI"
- "7차례 실제 배포로 검증된 AI 학습 시스템"
- "디버깅 시간 1-2시간 → 5분 (2400% 효율 향상)"
- "AI 정확도 33% → 95%+"
- "전 세계 기여: 2천만 시간 절약 예상", "$20억 기대효과"
- "v2.0.0 미래 — AI 기반 자동 수정 PR 생성"

이 릴리즈가 실제로 포함했던 것은: FastAPI 헬스체크 + 키워드 매칭 `/analyze` 엔드포인트, docker-compose 정의(다수 서비스가 ghost), n8n 워크플로우 1개, 빈 `tests/`. 위 모든 청구의 근거는 코드에 존재하지 않습니다.
