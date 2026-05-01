---
name: Case Report (사건 발행)
about: gwangcheon-shop 또는 연관 시스템에서 발생한 사건을 cases/ 후보로 발행합니다
title: '[CASE] '
labels: case-candidate
assignees: ''
---

> 이 issue는 `cases/` 후보 입력입니다. orchestrator의 케이스 주도 원칙에 따라,
> 이 issue가 cases/NNN-*.md 파일로 변환되어야 코드 변경의 근거가 됩니다.
>
> 변환 절차: [`cases/README.md`](../cases/README.md#케이스-작성-절차)

## 1. 사실 (무슨 일이 있었나)

<!--
사건 발생 시각, 어느 저장소·어느 워크플로우·어느 PR에서 발생했는지.
링크는 모두 그대로 붙여주세요. 추후 git log·gh run으로 추적할 수 있도록.

예:
- 2026-05-XX hh:mm UTC, gwangcheon-shop PR #NNN의 워크플로우 "X"가 실패
- 실패 잡: ...
- 에러 요약: ...
-->

## 2. 어느 액터/레이어에서 발생했나

<!--
- Claude Code 생성물의 결함인가? (코드 회귀)
- Antigravity가 놓친 검증인가? (검증 누락)
- 사용자 결정이 필요한 사안인가? (정책)
- 운영/인프라 이슈인가? (orchestrator 직접 처리)
- 또는 메타 (모델·정의 자체의 문제)
-->

## 3. 오케스트레이터가 막거나 도울 수 있었는가

<!--
- "이번에 막을 수 있었나" — 현재 게이트로 차단 가능한 종류였는가
- "다음에 도울 수 있나" — 어떤 레이어가 무엇을 더 하면 같은 일을 막거나 줄일 수 있는가
- 해당 없음(메타/외부 요인)이면 그렇게 적기
-->

## 4. 반복 가능성

<!--
- 같은 형태가 다시 발생할 가능성: 매우 낮음 / 낮음 / 중간 / 높음 / 매일
- 영향 크기: 작음 / 중간 / 큼 / 결정적
-->

## 5. 어디서 보았나 (선택)

<!--
- 사용자 직접 발견 / Antigravity 리포트 / 헬스체크 / 사용자 피드백 / 기타
- 캡처 경로가 자동이면 그 경로(워크플로우, 알람 등)를 명시
-->

## 변환 체크리스트 (orchestrator 측에서 처리)

- [ ] `cases/NNN-<slug>.md` 생성 (번호: `git ls-files cases/ | sort | tail -1` 다음)
- [ ] 이 issue 링크를 케이스 파일의 `references:` 프론트매터에 포함
- [ ] 이 issue를 close (`Closes #<이 issue 번호>`를 PR에 명시)
- [ ] `cases/README.md` 인덱스에 한 줄 추가
