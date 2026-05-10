# AI DevOps Orchestrator

> **포지션**: Claude Code(생성) → Antigravity(검증) → 사용자(승인) 세 액터를 잇는 **지휘자(conductor)**.
> 코드를 직접 만들지 않고, 액터 사이의 컨텍스트·상태·게이트·학습을 매개합니다.
> *(현재 완성 단계: 5-레이어 지휘자 모델 실체화 완료)*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-materialized-green)](#현재-상태)

## 현재 상태

이 저장소는 **5-레이어 지휘자 아키텍처**의 핵심 기능 구현을 완료했습니다.

### [1순위] 기반 레이어 (의존성 하단)
| 영역 | 상태 | 비고 |
|------|------|------|
| 운영 규칙 (`CLAUDE.md`) | ✅ 확정 | 액터 경계 및 작업 원칙 |
| 지휘자 5-레이어 아키텍처 | ✅ 확정 | `docs/ARCHITECTURE.md` |
| ChromaDB 환류 루프 | ✅ 통합 완료 | 인덱싱 자동화 및 API 검색 연동 완료 |
| Layer 2 트리아지 라우터 | ✅ 자동화 완료 | GitHub Action 기반 이슈/사고 자동 박제 파이프라인 |

### [2순위] 기능 레이어 (기반 위에서 동작)
| 영역 | 상태 | 비고 |
|------|------|------|
| Layer 1 컨텍스트 패커 | ✅ 실체화 완료 | 작업 시작 전 과거 사고 사례 자동 주입 (`/context/pack`) |
| Layer 3 컨텍스트 패킹 | ✅ 실체화 완료 | 검증자용 사고 맥락 번들링 및 위험 점수 산정 (`/context/verify-bundle`) |
| 단계 0 기획 에이전트 | ✅ 시동 | `scripts/planning_agent.py` 기반 자율 개선 이슈 제안 및 트리거 |

### [3순위] 완성 레이어 (검증 및 승인)
| 영역 | 상태 | 비고 |
|------|------|------|
| Layer 4 검증 게이트 | ✅ 실체화 완료 | 빌드/테스트 실패 로그 자동 분석 및 가이드 제공 (`/verify/gate`) |
| Layer 5 승인+배포 게이트 | ✅ 실체화 완료 | 사용자 승인 기반 배포 통제 및 SLI 관찰 루프 (`/verify/observe`) |
| 통합 테스트 | ✅ 완료 | 레이어별 동작 검증 스크립트 구축 및 확인 |

> 본 저장소는 **이전 버전에서 "AI 6개 에이전트가 자동 분석·수정 PR을 만든다"는 모델**을 폐기했습니다. 자세한 폐기 결정은 [`cases/000-bootstrap.md`](./cases/000-bootstrap.md) 참조.


## 작업 원칙

1. **케이스 주도**: 새 컴포넌트는 `cases/NNN-*.md`에 실제 발생 근거가 있을 때만 코드화합니다. 가설 기반 기능 추가 금지.
2. **액터 경계**: 새 작업을 받으면 "이건 어느 액터의 일인가, 오케스트레이터가 매개해야 하는가"를 먼저 묻습니다.
3. **최소 척추 우선**: 문서·스펙·인터페이스 → 케이스 발생 → 최소 구현.

## 무엇을 만드는가 / 만들지 않는가

| ✅ 만든다 | ❌ 만들지 않는다 |
|---|---|
| 컨텍스트 패커 (과거 사례 자동 주입) | 자체 코드 품질 룰 엔진 (Antigravity와 중복) |
| 승인 상태머신 (`created → … → observed`) | 자체 보안 스캐너 (Antigravity와 중복) |
| 트리아지 라우터 (알림 분류) | 사용자 승인 없는 운영 배포 |
| 런타임 → ChromaDB → 다음 작업 환류 루프 | 투기적 기능 (아직 케이스 없는) |
| 배포 오케스트레이션 + 자동 롤백 |  |
| 풀 루프 자동화 (에이전트 구동) | |

## 문서 맵

- [`CLAUDE.md`](./CLAUDE.md) — 프로젝트 운영 규칙 (DO/DON'T, 액터 경계)
- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — 지휘자 모델 설계
- [`docs/PIPELINE_STATES.md`](./docs/PIPELINE_STATES.md) — 변경 → 운영 상태머신, 게이트 차단 시나리오 G1~G5
- [`docs/INTEGRATIONS.md`](./docs/INTEGRATIONS.md) — 외부 시스템 연동 및 상태 매핑 명세
- [`cases/`](./cases) — 실제 케이스 로그 (개선의 유일한 근거)
- [`docs/QUICK_START.md`](./docs/QUICK_START.md) / [`docs/API_REFERENCE.md`](./docs/API_REFERENCE.md) — 최신 가이드라인 및 API 명세

## 1차 적용 대상

**gwangcheon-shop** — 본 저장소의 지휘자 모델은 이 프로젝트에서 검증된 후 다른 프로젝트로 확장합니다.

## 로컬 실행

현재 `services/langchain_api/main.py`는 지휘자 모델의 핵심 엔드포인트를 제공합니다.

```bash
cp .env.example .env
docker-compose up -d
```

- **LangChain API**: http://localhost:8002
- **ChromaDB**: http://localhost:8003 (HTTP 모드 시)

## 라이선스

[MIT](LICENSE)
