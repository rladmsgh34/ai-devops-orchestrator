#!/usr/bin/env python3
import subprocess
import sys
import json
import os

def run_planning_analysis():
    print("🤖 기획 에이전트 가동: 저장소 상태 분석 중...")
    
    # 지휘자 모델의 규칙과 현재 케이스 상황을 프롬프트로 전달
    prompt = """
    너는 AI DevOps Orchestrator의 '기획 에이전트'야.
    현재 저장소의 README.md, ARCHITECTURE.md, 그리고 cases/ 폴더의 최근 사례들을 분석해서
    다음 '광천샵(gwangcheon-shop)' 개선을 위해 가장 시급한 작업 3가지를 제안해줘.
    
    분석 기준:
    1. 최근 발생한 장애(Case #012, #013)와 연관된 예방 조치
    2. 지휘자 모델의 5개 레이어 중 아직 미구현된 부분의 우선순위
    3. 문서와 실체 사이의 괴리(Honesty) 수정
    
    형식:
    각 제안은 GitHub Issue 제목과 본문(Markdown) 형태로 작성해줘.
    """
    
    # Gemini CLI 호출 (여기서는 시뮬레이션 또는 실제 CLI 호출 로직)
    # 실제 환경에서는 `gemini "prompt"` 형식을 사용
    print("-" * 40)
    print("Gemini CLI 분석 결과 제안 (Draft):")
    print("-" * 40)
    
    # 시뮬레이션 결과 출력 (실제 구현 시에는 subprocess.run(["gemini", prompt]) 등 사용)
    proposal = """
### [PROPOSAL 1] gwangcheon-shop 배포 전 'pnpm lock' 무결성 검증 자동화
**본문**: Case #012의 재발 방지를 위해, PR 단계에서 Layer 4 게이트를 호출하여 lock 파일 동기화 여부를 강제해야 합니다.

### [PROPOSAL 2] Layer 1 컨텍스트 패커 초기 구현
**본문**: Claude Code가 작업 시작 시 과거 사고 사례를 ChromaDB에서 읽어올 수 있도록 컨텍스트 주입 로직을 시작해야 합니다.

### [PROPOSAL 3] API 명세 내 'Planned' 엔드포인트 실체화 로드맵
**본문**: docs/API_REFERENCE.md에 적힌 계획된 API들의 우선순위를 정하고 첫 번째 구현 대상을 확정해야 합니다.
    """
    print(proposal)
    print("-" * 40)
    print("위 제안 중 정식 이슈로 등록할 번호를 선택하거나 'all'을 입력하세요 (또는 q로 종료).")

if __name__ == "__main__":
    run_planning_analysis()
