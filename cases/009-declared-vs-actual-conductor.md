---
id: 009
title: 선언된 컴포넌트 vs 실측 괴리 — 지휘자 자기 자신의 Unbacked Self-Claim (결정 케이스)
date: 2026-05-02
project: ai-devops-orchestrator (자기 인용)
actor_involved: [user, orchestrator, claude-code]
state: pending-decision
deadline: 2026-05-09
related_cases: [007]
related_components:
  - services/langchain-api/
  - services/n8n-workflows/
  - docker-compose.yml (8 컨테이너)
  - docs/INTEGRATIONS.md (Antigravity 가정)
---

# Case 009 — 선언된 컴포넌트 vs 실측 괴리 (결정 케이스)

**TL;DR.** 사용자가 "ai-devops에 연결된 ci/cd 프로젝트가 무엇인가" 물어 실측한 결과, **연결된 프로젝트는 사실상 `gwangcheon-shop` 1개(단방향 관찰)**. orchestrator 본체의 `services/langchain-api/`·`services/n8n-workflows/`·`docker-compose.yml`의 8개 컨테이너·`docs/INTEGRATIONS.md`의 Antigravity 인터페이스는 **선언만 되어 있고 외부 호출/실 사용 흔적이 0**. 이는 case #007("Unbacked Self-Claim — 외부 변형")의 **내부 변형 두 번째 인스턴스**에 해당하며, case #005 트리거 룰(2회 누적)을 만족한다. 결정은 (a) 부분 실체화 + 격리 / (b) 박제만, 실체화 보류 / (c) 폐기 + 정직성 셋 중 사용자 결정 대기.

> case #005 §6.1 변형(동시 다발 인스턴스)을 적용 — 4개 컴포넌트를 별도 케이스로 박제하지 않고 본 결정 케이스 §1 표로 직접 사실화.
> case #005 §6.2(외부 자산 사전 점검 의무)는 **본 케이스에서는 적용 안 됨** — 회수 대상이 외부가 아닌 orchestrator 자기 자신의 트리이므로 사용자 진행 중 작업과 충돌 위험 없음.

## 1. 누적된 인스턴스

### 기존 박제

| ID | 한 줄 요약 | family |
|---|---|---|
| #007 | 4개 위성 repo의 정량 단정 vs 비어있는 자산 (외부) | Unbacked Self-Claim |

### 본 케이스에서 신규 사실화 (case #005 §6.1 동시 다발 변형)

> 4개 항목이 동일 시점·동일 패턴으로 동시 노출되었으므로 별도 박제 없이 본 §1 표로 직접 사실화한다.

| 자산 | 선언 위치 | 실측 | 외부 호출 |
|---|---|---|---|
| `services/langchain-api/` | `services/`, `docker-compose.yml`, README, ARCHITECTURE.md | `Dockerfile`(560B) + `main.py`(키워드 매칭 데모, 4.3KB) + `requirements.txt`(651B). README 명시: "키워드 매칭 기반 데모이며 지휘자 모델 컴포넌트는 아직 포함되지 않음" | 0 — `gwangcheon-shop` CI/CD 어디에서도 호출 흔적 없음 |
| `services/n8n-workflows/` | `services/`, `docker-compose.yml`, ARCHITECTURE.md | `github-integration.json` 1개 파일. 워크플로우 실체 없음 | 0 |
| `docker-compose.yml`의 8 컨테이너 | `docker-compose.yml` | `langchain-api`, `n8n`, `chromadb`, `redis`, `postgres`, `prometheus`, `grafana`, `elasticsearch`, `kibana`, `logstash` 정의 | 사용 흔적 없음. README가 "현 데모 코드 기준" 명시 |
| Antigravity 인터페이스 | `docs/INTEGRATIONS.md` §2.2 | status check `antigravity/verify` 결과 스키마, 입출력 형태 정의 | 게시 0건. 현 단계 인터페이스 가정만 |

> 참고: `docs/INTEGRATIONS.md` 자체는 머리말에서 "스펙 가정(spec assumptions)이며 코드는 아직 없다"고 명시한다. 이 명시 덕분에 INTEGRATIONS.md는 **정직한 가정 단계**이다 — 본 케이스는 그 정직성을 부정하지 않고, 다만 **인터페이스 가정과 docker-compose 컨테이너 정의 사이의 비대칭**(전자는 가정 표시, 후자는 실서비스처럼 서술)을 짚는다.

## 1.1 자기 검증 — case #007의 두 번째 인스턴스인가?

case #006이 case #004에 대해 했던 자기 검증을 본 케이스가 case #007에 대해 수행한다.

### 식별 기준 (case #007 §8 정의: Unbacked Self-Claim)

> "자산이 자기 근거를 가지지 못한 채 존재한다" + "단정적 자기 주장이 활동/실체보다 앞선다"

### 본 케이스 적용

| 차원 | case #007 (1차) | 본 케이스 (2차 후보) | 판정 |
|---|---|---|---|
| 자기 주장 vs 실체 비대칭 | README "47+ 패턴 / 95% 성공률" vs LICENSE+README만 | docker-compose 8 컨테이너·`services/` 트리 vs 데모 1개 + json 1개 | **동형** ✓ |
| 케이스 0건 상태에서 정의 발행 | v1.0.0 태깅 (case 0건) | docker-compose 8개 + services/ 트리 (case 0건) | **동형** ✓ |
| 활동/호출 부재 | 4월 28일 단일 커밋 후 정지 | 외부 호출 0, 내부 사용 흔적 0 | **동형** ✓ |
| 자산 위치 | 외부 위성 repo | 내부 `services/` + `docker-compose.yml` + INTEGRATIONS.md | **차이** — 외부→내부 |
| 액터 책임 | 사용자(생성 결정) + claude-code(생성 실행) | 동일. orchestrator 본체에 적용된 형태 | **동형** ✓ |

### 결론

본 케이스는 case #007과 **동일 family(Unbacked Self-Claim)의 두 번째 인스턴스**다. 차이점은 자산 위치(외부 → 내부) 한 축이며, 패턴의 본질은 보존된다. 따라서:

- case #005 트리거 룰의 **2회 누적 조건 충족** → 결정 케이스 발행 의무 발동 (본 발행이 그 이행)
- case #007 §8의 메타 패턴 명명 "Unbacked Self-Claim"은 본 케이스에 그대로 적용 가능. 단 **변형 축**(외부/내부)을 기록할 가치가 있어 §8에 보완을 둔다

### 자기 검증의 메타 학습

case #006이 case #004에 대해 "후보 박제와 트리거 박제는 다른 단계의 활동"임을 발견했듯, 본 자기 검증은 **"외부 변형으로 박제된 패턴이 내부에서 재현될 때, 그 발견 자체가 두 번째 인스턴스다"** 를 추가한다. 즉 패턴은 **자산 위치 축**으로 일반화될 수 있으며, family 박제 시 "어디서 발생할 수 있는가"를 미리 열거해두는 것이 다음 자기 검증의 비용을 줄인다.

## 2. 공통 패턴 (case #007과 공유)

- **자기소개가 실체보다 앞섬** — README/ARCHITECTURE.md/docker-compose.yml/INTEGRATIONS.md가 8개 컨테이너·5개 레이어·검증자 인터페이스를 서술하지만, 그중 외부에서 실제로 호출/와이어드된 것은 0
- **케이스 0건 상태에서 컴포넌트 정의 발행** — `services/` 트리와 `docker-compose.yml`의 8 컨테이너는 어떤 케이스도 그것을 요구하기 전에 박제됨 (orchestrator의 첫 커밋부터 존재)
- **활동/호출 부재** — `gwangcheon-shop`의 8개 워크플로우 어디에서도 본 컴포넌트들을 호출하지 않음. self-hosted runner와 deploy target으로 같은 VM을 공유할 뿐, 코드/CI 차원의 연결은 0

### case #007과의 변형 축

| 축 | case #007 | 본 케이스 |
|---|---|---|
| 자산 위치 | 외부 위성 repo | 내부 `services/` + `docker-compose.yml` + INTEGRATIONS.md |
| 정직성 시그널 | 없음 (단정적 톤) | 부분적 — README "재정의 중", INTEGRATIONS.md "스펙 가정", `services/langchain-api/main.py` "데모"라 명시 |
| 회수 비용 | 낮음 (`gh repo archive`) | 중간 (docker-compose 정리 + README 톤 갱신 + 향후 케이스 발생 시 실체화 경로 정의) |

> 본 케이스의 정직성 시그널이 부분적으로 존재한다는 점은 case #007과 다른 **완화 요인**이다. 즉 본 케이스의 (c) wontfix 옵션은 case #007보다 약간 더 합리적인 후보 — README/INTEGRATIONS.md의 "가정/데모" 표시가 이미 사실 박제 일부를 수행하고 있기 때문.

## 3. 어느 레이어에서 막을 수 있는가

본 패턴은 **레이어 결함이 아니라 컴포넌트 발행 절차의 결함**이다 (case #007과 동일 분류).

- 직접적 책임은 사용자(생성 결정)와 claude-code(생성 실행)에 분산되며, orchestrator는 **자기 자신의 컴포넌트가 케이스 없이 박제되어 있다는 사실의 박제와 회수 절차**의 책임이 있다
- L1~L5의 어느 레이어에 매핑되지 않음. case #002가 캡처 채널을, case #005가 트리거 임계점을 박제했듯, 본 케이스는 **컴포넌트 정의의 케이스 선행 의무**를 박제한다

## 4. 옵션 (3지선다)

### (a) `decided-implement` — 부분 실체화 + 격리

- **8개 컨테이너 중 첫 케이스가 실제로 요구하는 것 1~2개만** docker-compose 기본 `up` 대상으로 유지. 나머지는 `profiles: future`(또는 `legacy-demo`)로 격리하여 명시적 opt-in 시에만 기동
- 첫 실체화 후보:
  - **case #004(가드 비대칭)의 두 번째 인스턴스 누적 시** → Layer 3 컨텍스트 패커 코드화. 그 시점에 `langchain-api` + `chromadb`만 활성
  - 그 외 컨테이너(redis/postgres/prometheus/grafana/elasticsearch/kibana/logstash)는 격리
- `services/n8n-workflows/`의 `github-integration.json` 1건은 **격리 대상에 포함**(현 시점 호출자 부재) — 첫 활용 케이스 발생 시 분리
- `docs/INTEGRATIONS.md`는 Antigravity 가정 유지. 단, **"본 가정의 첫 실체화는 어느 케이스에서 시작될 것인가"** 한 줄을 §6 미해결 가정에 추가
- README의 "로컬 실행 (현 데모 코드)" 섹션을 **"현 시점 데모 컨테이너는 기본 비활성. case-driven 실체화 경로는 §X 참조"** 로 갱신

### (b) `decided-observe` — 박제만, 실체화 보류

- docker-compose, services/, INTEGRATIONS.md를 **그대로 둠**
- README와 INTEGRATIONS.md에 **"본 자산은 case-driven 원칙에 따라 케이스 발생 시 실체화됩니다"를 더 명시적으로** 추가 (현재는 부분적으로만 표시됨)
- 다음 인스턴스가 또 잡히면 결정 다시
- 사유 후보: 실체화 후보 케이스(case #004 두 번째 인스턴스)가 곧 발생할 가능성이 있다면 격리/폐기는 조기 행동

### (c) `decided-wontfix` — 폐기 + 정직성

- 8개 컨테이너 정의 모두 `docker-compose.yml`에서 제거 (또는 `examples/docker-compose.legacy-demo.yml`로 이전)
- `services/langchain-api/`와 `services/n8n-workflows/`를 `examples/legacy-demo/`로 이전 (또는 삭제 후 case 박제로 사실 보존)
- `docs/INTEGRATIONS.md`는 Antigravity 인터페이스 가정 톤 다운: "현 시점 외부 검증자 인터페이스는 정의되어 있지 않다. 첫 검증자 통합 케이스 발생 시 정의된다"
- README에 **"현 시점 ai-devops-orchestrator는 case-driven 단방향 관찰자 단계"** 를 명시
- 회수 사실 자체를 case #007과 같은 결로 본 §8에 박제 ("Unbacked Self-Claim — 내부 변형의 회수")

## 5. 사용자 결정

- [ ] (a) 부분 실체화 + 격리
- [ ] (b) 추가관찰 (실체화 보류)
- [ ] (c) 폐기 + 정직성

| 항목 | 값 |
|---|---|
| 결정자 | 사용자 |
| 결정일 | (대기) |
| 결정 사유 | (대기) |

## 6. 처리 절차 보완

본 케이스에서 **새 절차 보완 없음**. case #005 §6.1(동시 다발 인스턴스)·§6.2(외부 자산 사전 점검)는 충분하며, 본 케이스의 회수 대상이 내부이므로 §6.2의 외부 자산 사전 점검은 적용 안 됨. 본 §6은 그 사실을 명시하기 위한 자리이며, 새 절차는 결정 PR(후속) 시점에 학습이 발생하면 그때 보완한다.

## 7. 마감일 도래 시

- 2026-05-09까지 §5의 결정이 없으면, 그 사실 자체를 회고 케이스로 발행 (case #005 §6 절차)

## 8. 학습 (ChromaDB 인덱싱 대상)

"Unbacked Self-Claim"은 **자산 위치 축**으로 변형된다 — case #007이 외부 변형(위성 repo의 자기 주장이 자산보다 앞섬)이라면, 본 케이스는 내부 변형(지휘자 본체의 컴포넌트 정의가 케이스보다 앞섬)이다. 둘은 표면 형태가 달라 보이지만 **자산이 자기 근거를 가지지 못한 채 존재한다**는 본질이 동일하다. family를 박제할 때 미래 인스턴스가 발견될 수 있는 자산 위치(외부/내부/혼합)를 미리 열거해두면, 다음 자기 검증의 비용이 줄어든다 — 본 case #009의 발견은 **"family 자체에 변형 축을 미리 박는다"** 는 학습으로 이어진다.

지휘자 모델의 자기 모순 — orchestrator는 케이스 주도 원칙을 운영 룰로 박제했으나, **자기 자신의 컴포넌트 정의는 케이스보다 앞서 박제되어 있었다**. 이 자기 모순의 발견 자체가 본 케이스의 가치이며, "지휘자가 자기 룰을 자기 자신에게도 적용한다"는 case #005의 메타 원칙이 본 케이스에서 두 번째 자기 적용을 보인다 (첫 자기 적용은 case #006의 case #004 자기 검증).

### 외부 변형의 정직성 시그널 차이 (보완)

case #007의 외부 변형은 정직성 시그널이 0이었다("47+ 패턴" 같은 단정적 톤). 본 케이스의 내부 변형은 부분적으로 정직성 시그널이 존재한다(README "데모", INTEGRATIONS.md "스펙 가정", main.py "키워드 매칭 데모"). 이 차이는 회수 옵션의 무게를 바꾼다 — 외부 변형은 archive가 자연스러웠지만, 내부 변형은 (b) 박제만 + 정직성 강화가 (a)/(c)와 동등 후보가 될 수 있다. 향후 family 박제 시 **"정직성 시그널의 강도"** 를 회수 결정의 입력 변수로 둘 가치가 있다.
