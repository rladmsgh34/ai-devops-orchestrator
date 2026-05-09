# AI DevOps Orchestrator

> **포지션**: Claude Code(생성) → Antigravity(검증) → 사용자(승인) 세 액터를 잇는 **지휘자(conductor)**.
> 코드를 직접 만들지 않고, 액터 사이의 컨텍스트·상태·게이트·학습을 매개합니다.
> *(현재 척추 단계: 인프라 및 자동화 파이프라인 우선 구축 중)*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-case--driven%20materialization-orange)](#현재-상태)

## 현재 상태

이 저장소는 **케이스 주도 실체화** 단계입니다. 컴포넌트는 우선순위 및 의존성에 따라 순차적으로 구현됩니다.

### [1순위] 기반 레이어 (의존성 하단)
| 영역 | 상태 | 비고 |
|------|------|------|
| 운영 규칙 (`CLAUDE.md`) | ✅ 확정 | 액터 경계 및 작업 원칙 |
| 지휘자 5-레이어 아키텍처 | ✅ 확정 | `docs/ARCHITECTURE.md` |
| ChromaDB 환류 루프 | 🟡 기초 통합 | 인덱싱 자동화 완료, API 검색 연동됨 |
| Layer 2 트리아지 라우터 | 🤖 자동화 완료 | 위성 프로젝트 사고 자동 수신 및 박제 |

### [2순위] 기능 레이어 (기반 위에서 동작)
| 영역 | 상태 | 비고 |
|------|------|------|
| Layer 1 컨텍스트 패커 | 🏗️ 실체화 진행 중 | API 검색 연동 완료, 검색 품질 및 가드레일 검증 필요 |
| Layer 3 컨텍스트 패킹 | 🏗️ 실체화 진행 중 | PR 코멘트 연동 완료, 맥락 추출 로직 고도화 필요 |
| 단계 0 기획 에이전트 | ✅ 시동 | Gemini CLI 기반 자율 개선 이슈 제안 |

### [3순위] 완성 레이어 (검증 및 승인)
| 영역 | 상태 | 비고 |
|------|------|------|
| Layer 4 검증 게이트 | 🏗️ 실체화 진행 중 | gwangcheon-shop CI 연동, 장애 패턴 분석 고도화 필요 |
| 승인 상태머신 스펙 | ✅ 확정 | `docs/PIPELINE_STATES.md` |
| Layer 5 승인+배포 게이트 | ❌ 미구현 | 사용자 승인 기반 배포 통제 |
| 테스트 (`tests/`) | 🟡 기초 유닛 테스트 도입 | 주요 스크립트 무결성 검증 |

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

현재 `services/langchain-api/main.py`는 지휘자 모델의 핵심 엔드포인트를 제공합니다.

```bash
cp .env.example .env
docker-compose up -d
```

- **LangChain API**: http://localhost:8000
- **ChromaDB**: http://localhost:8001

## 라이선스

[MIT](LICENSE)
