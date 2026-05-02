# AI DevOps Orchestrator — 프로젝트 규칙

이 저장소는 단독 자동화 도구가 아니라, **세 액터를 잇는 지휘자(conductor)** 입니다.

## 액터와 역할

```
Claude Code (생성자)  →  Antigravity (검증자)  →  사용자 (승인자)
                              ↑
                    AI DevOps Orchestrator (지휘자)
```

- **Claude Code**: 코드 생성·리팩터·구현
- **Antigravity**: 코드 검증·품질·보안·회귀 검사
- **사용자**: 최종 승인·배포 결정
- **Orchestrator(이 저장소)**: 위 셋 사이의 컨텍스트·상태·게이트·학습 루프 관리

## 무엇을 만드는가 (DO)

1. **컨텍스트 패커** — Claude Code 작업 시작 시 ChromaDB의 과거 사고 사례 주입
2. **승인 상태머신** — `created → verified → approved → deployed` 단계 강제, 누락 차단
3. **트리아지 라우터** — 알림/에러를 올바른 액터에게 라우팅
4. **런타임 → 학습 피드백 루프** — 운영 에러 → ChromaDB → 다음 작업 프롬프트
5. **배포 오케스트레이션 + 롤백** — 카나리·헬스체크·자동 롤백 (운영 레이어)
6. **케이스 로그** — 실제 사고/요청을 `cases/`에 기록, 이게 다음 개선의 근거가 됨

## 무엇을 만들지 않는가 (DON'T)

| 금지 | 이유 |
|---|---|
| AI가 자동으로 수정 PR 생성 | Claude Code의 생성자 역할과 충돌 |
| 자체 코드 품질 룰 엔진 | Antigravity의 검증자 역할과 중복 |
| 자체 보안 스캐너 | Antigravity의 검증자 역할과 중복 |
| 사용자 승인 없는 운영 배포 | 승인자 역할 우회 |
| 투기적 기능(아직 케이스 없는) | "케이스 주도 개선" 원칙 위반 |

## 작업 원칙

### 1. 케이스 주도 개선 (Case-Driven Improvement)
새 기능은 **실제 발생한 케이스**가 `cases/`에 기록된 뒤에만 만든다. 가설 기반 기능 추가 금지.

동일 패턴의 **인스턴스 2회 누적 시 결정 케이스 발행 의무**가 발동된다 (자동화 지연 역설 차단). 절차·양식·옵션은 `cases/README.md`의 "트리거 임계점과 결정 케이스" 섹션을 단일 출처로 한다.

### 2. 최소 척추 우선
문서·스펙·인터페이스를 먼저 만들고, 코드는 케이스가 요구할 때만 짠다.

### 3. 액터 경계 존중
의심스러우면 "이건 Claude Code 일인가? Antigravity 일인가? 사용자 결정인가? 아니면 오케스트레이터가 매개해야 하나?"를 먼저 묻는다.

## 디렉토리 구조

```
ai-devops-orchestrator/
├── CLAUDE.md                    ← 이 파일 (규칙)
├── docs/
│   ├── ARCHITECTURE.md          ← 지휘자 모델 설계
│   ├── PIPELINE_STATES.md       ← 상태머신 스펙
│   ├── API_REFERENCE.md         ← (기존)
│   └── QUICK_START.md           ← (기존)
├── cases/                       ← 실제 발생 사례 로그
│   ├── README.md                ← 케이스 작성·처리 절차
│   ├── TEMPLATE.md              ← 케이스 양식
│   └── NNN-<slug>.md            ← 개별 케이스
├── services/
│   ├── langchain-api/           ← (재정의 중)
│   └── n8n-workflows/           ← (재정의 중)
└── ...
```

## 커밋·브랜치 규칙

전역 `~/.claude/CLAUDE.md` 규칙을 따른다. 추가로:

- 케이스 1건 처리 = 커밋 1개 이상, 메시지에 케이스 ID 포함 (`feat: context packer (case #003)`)
- 문서·스펙 변경은 코드 없이 단독 커밋 가능
- main 직접 커밋 금지 (전역 규칙)

## 적용 대상

현재 1차 적용 대상은 **gwangcheon-shop**. 검증된 패턴은 이후 다른 프로젝트로 확장한다.
