# Quick Start — 지휘자(Conductor) 모델

이 가이드는 AI DevOps Orchestrator의 **지휘자 모델**과 **케이스 주도 개발(Case-Driven Development)** 워크플로우에 빠르게 적응하는 방법을 안내합니다.

## 1. 핵심 철학 이해

우리는 코드를 직접 짜지 않습니다. 대신 다음 액터들을 지휘합니다:
- **Claude Code**: 개발자 (코드 생성)
- **Antigravity (또는 Gemini)**: 검증자 (코드 검사)
- **사용자**: 승인자 (최종 결정)
- **Orchestrator (본 프로젝트)**: 지휘자 (컨텍스트 및 게이트 관리)

## 2. 첫 사건(Case) 발행하기

모든 변경은 실제 사건에서 시작됩니다.

1.  **사건 발생**: `gwangcheon-shop` 또는 관련 시스템에서 빌드 실패, 검증 누락, 혹은 반복되는 실수를 발견합니다.
2.  **Issue 등록**: 본 저장소의 GitHub Issues에서 `Case Report (사건 발행)` 템플릿을 사용하여 내용을 작성합니다.
3.  **Case 변환**: 등록된 Issue를 `cases/` 폴더의 마크다운 파일로 변환합니다.
    ```bash
    # Issue 내용을 복사하여 파일로 저장 (예: issue.txt)
    cat issue.txt | python3 scripts/ingest_case.py
    ```
4.  **박제**: 생성된 `cases/NNN-*.md` 파일을 커밋합니다. (이 시점에서는 코드 수정 없이 '관찰' 상태로 둡니다.)

## 3. 임계점 도달 및 실체화

동일한 패턴의 케이스가 **2회 누적**되면 '결정 케이스'를 발행하고 코드를 구현할 수 있습니다.

1.  **결정 케이스 발행**: `state: pending-decision` 필드를 추가하여 어떤 레이어(L1~L5)를 구현할지 제안합니다.
2.  **사용자 승인**: 사용자가 결정을 확정하면(`decided-implement`), 해당 레이어의 코드를 `services/` 하위에 작성합니다.

## 4. 로컬 환경 확인 (Legacy Demo)

기존의 분석 엔진 데모를 확인하려면 명시적 프로파일을 사용하여 실행합니다.

```bash
cp .env.example .env
docker-compose --profile legacy-demo up -d
```

- **LangChain API**: http://localhost:8000
- **n8n**: http://localhost:5678
- **ChromaDB**: http://localhost:8001

## 5. 유닛 테스트 실행

새로운 스크립트나 컴포넌트를 추가했다면 테스트를 실행하여 무결성을 확인합니다.

```bash
PYTHONPATH=. python3 tests/test_ingest_case.py
```

## 6. 다음 단계

- `docs/ARCHITECTURE.md`를 읽고 5개 레이어 모델을 이해하세요.
- `cases/` 폴더를 둘러보며 기존에 어떤 문제들이 박제되었는지 확인하세요.
- `CLAUDE.md`에서 작업 규칙을 숙지하세요.
