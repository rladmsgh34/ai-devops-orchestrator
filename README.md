# AI DevOps Orchestrator

> **포지션**: Claude Code(생성) → Antigravity(검증) → 사용자(승인) 세 액터를 잇는 **지휘자(conductor)**.
> 코드를 직접 만들지 않고, 액터 사이의 컨텍스트·상태·게이트·학습을 매개합니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-case--driven%20bootstrap-orange)](#현재-상태)

## 현재 상태

이 저장소는 **케이스 주도 부트스트랩** 단계입니다. 척추(문서·스펙·게이트 정의)는 잡혔고, 컴포넌트 코드는 `cases/`에 실제 발생 근거가 쌓일 때마다 한 조각씩 추가됩니다.

| 영역 | 상태 |
|------|------|
| 운영 규칙 (`CLAUDE.md`) | ✅ 확정 |
| 지휘자 5-레이어 아키텍처 (`docs/ARCHITECTURE.md`) | ✅ 확정 |
| 승인 상태머신 (`docs/PIPELINE_STATES.md`) | ✅ 스펙 확정 / ❌ 미구현 |
| 케이스 로그 (`cases/`) | ✅ 워크플로우 시동 (case #000 resolved) |
| FastAPI `/analyze` 키워드 매칭 데모 | ⚠️ 기존 코드 잔존 (지휘자 모델로 재작성 예정) |
| Layer 1 컨텍스트 패커 | ❌ 미구현 (첫 케이스 대기) |
| Layer 2 트리아지 라우터 | ❌ 미구현 |
| Layer 3 컨텍스트 패킹 | ❌ 미구현 |
| Layer 4 검증 게이트 | ❌ 미구현 |
| Layer 5 승인+배포 게이트 | ❌ 미구현 |
| ChromaDB 환류 루프 | ❌ 미구현 |
| 테스트 (`tests/`) | ❌ 비어있음 |
| 최소 CI (ruff + compose + yaml) | ✅ PR-only 트리거 |

> 본 저장소는 **이전 버전(README 기준)에서 "AI 6개 에이전트가 자동 분석·수정 PR을 만든다"는 모델**을 폐기했습니다. 그 모델은 Claude Code(생성)·Antigravity(검증) 역할과 정면으로 충돌합니다. 자세한 폐기 결정은 [`cases/000-bootstrap.md`](./cases/000-bootstrap.md), 컴포넌트 매트릭스는 [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) 참조.

## 작업 원칙

1. **케이스 주도**: 새 컴포넌트는 `cases/NNN-*.md`에 실제 발생 근거가 있을 때만 코드화합니다. 가설 기반 기능 추가 금지.
2. **액터 경계**: 새 작업을 받으면 "이건 어느 액터의 일인가, 오케스트레이터가 매개해야 하는가"를 먼저 묻습니다.
3. **최소 척추 우선**: 문서·스펙·인터페이스 → 케이스 발생 → 최소 구현.

## 무엇을 만드는가 / 만들지 않는가

| ✅ 만든다 | ❌ 만들지 않는다 |
|---|---|
| 컨텍스트 패커 (과거 사례 자동 주입) | AI가 자동으로 수정 PR 생성 (Claude Code와 충돌) |
| 승인 상태머신 (`created → … → observed`) | 자체 코드 품질 룰 엔진 (Antigravity와 중복) |
| 트리아지 라우터 (알림 분류) | 자체 보안 스캐너 (Antigravity와 중복) |
| 런타임 → ChromaDB → 다음 작업 환류 루프 | 사용자 승인 없는 운영 배포 |
| 배포 오케스트레이션 + 자동 롤백 | 투기적 기능 (아직 케이스 없는) |

## 문서 맵

- [`CLAUDE.md`](./CLAUDE.md) — 프로젝트 운영 규칙 (DO/DON'T, 액터 경계)
- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — 지휘자 5-레이어 모델, 컴포넌트 제거/유지/신규 매트릭스
- [`docs/PIPELINE_STATES.md`](./docs/PIPELINE_STATES.md) — 변경 → 운영 상태머신, 게이트 차단 시나리오 G1~G5
- [`cases/`](./cases) — 실제 케이스 로그 (개선의 유일한 근거)
- [`docs/QUICK_START.md`](./docs/QUICK_START.md) / [`docs/API_REFERENCE.md`](./docs/API_REFERENCE.md) — (현 데모 코드 기준, 지휘자 모델로 재작성 예정)

## 1차 적용 대상

**gwangcheon-shop** — 본 저장소의 지휘자 모델은 이 프로젝트에서 검증된 후 다른 프로젝트로 확장합니다.

## 로컬 실행 (현 데모 코드)

현 시점의 `services/langchain-api/main.py`는 키워드 매칭 기반 데모이며, 지휘자 모델 컴포넌트는 아직 포함되지 않습니다.

```bash
cp .env.example .env  # 필요한 키만 채움 (없으면 데모 엔드포인트는 동작)
docker-compose up -d
```

- LangChain API: http://localhost:8000
- n8n: http://localhost:5678
- ChromaDB: http://localhost:8001

## 라이선스

[MIT](LICENSE)
