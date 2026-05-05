# API Reference — 지휘자(Conductor) 모델

> ⚠️ 본 API 명세 중 상당수는 **설계 단계**이며, `cases/`의 요구에 따라 순차적으로 구현됩니다.
> 현재 살아있는 실체는 `legacy-demo` 프로파일로 기동되는 에러 분석 API입니다.

## 1. 지휘자 레이어 API (Planned)

### Layer 1 & 3: Context Packer
Claude Code의 생성 시점 및 Antigravity의 검증 시점에 컨텍스트를 주입합니다.

- **POST `/context/pack`**
  - **목적**: 파일 경로와 이슈 텍스트를 기반으로 ChromaDB에서 과거 관련 사례를 추출하여 프롬프트 번들을 생성합니다.
  - **Input**: `{ "file_paths": [...], "issue_text": "..." }`
  - **Output**: `{ "context_bundle": "...", "related_cases": [...] }`

### Layer 2: Triage Router
외부 알림을 분류하여 적절한 액터에게 전달합니다.

- **POST `/triage/route`**
  - **목적**: 런타임 에러나 CI 실패 이벤트를 분석하여 Claude Code(재작업), Antigravity(재검증), 또는 사용자에게 라우팅합니다.
  - **Input**: `{ "event_source": "github_actions", "payload": { ... } }`

### Layer 4 & 5: Approval Gate
승인 상태머신을 관리하고 배포 게이트를 통제합니다.

- **GET `/pipeline/status/{change_id}`**
  - **목적**: 특정 변경 건의 현재 파이프라인 상태(`created`, `verified`, `approved` 등)를 조회합니다.

---

## 2. 레거시 에러 분석 API (Current Demo)

`docker-compose --profile legacy-demo`로 실행 시 접근 가능합니다.

### Error Pattern Analysis

- **POST `/analyze`**
  - **목적**: 에러 로그를 분석하여 알려진 패턴과 해결책을 제시합니다.
  - **Payload**:
    ```json
    {
      "error_log": "Error: Cannot find module 'pure-rand'",
      "project_config": {
        "framework": "nextjs"
      }
    }
    ```
  - **Response**:
    ```json
    {
      "pattern_id": "ERR001",
      "confidence": 0.95,
      "recommendation": "Install pure-rand as a devDependency."
    }
    ```

### Health Check

- **GET `/health`**
  - **목적**: 서비스 상태 확인.
  - **Response**: `{ "status": "healthy" }`

---

## 3. 인증 및 보안 (Planned)

- **Header**: `X-Orchestrator-Token` (환경 변수 `ORCHESTRATOR_API_KEY`와 대조)
- **CORS**: `CLAUDE.md` 및 `.env`에 정의된 허용 도메인만 접근 가능.
