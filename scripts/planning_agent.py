#!/usr/bin/env python3
import sys
import os
import requests
import subprocess

# 설정
API_URL = os.getenv("CONDUCTOR_API_URL", "http://localhost:8000")

def run_planning_analysis():
    """
    기존 Gemini CLI 분석 placeholder 기능과 API 호출 기능을 통합합니다.
    """
    if len(sys.argv) > 1:
        # 인자가 있으면 API 호출 모드로 동작
        main_api_mode()
    else:
        # 인자가 없으면 분석 제안 모드로 동작 (Simulation)
        print("🤖 기획 에이전트 가동: 저장소 상태 분석 중...")
        
        # 분석 결과 제안 (Draft)
        proposal = """
### [PROPOSAL 1] gwangcheon-shop 배포 전 'pnpm lock' 무결성 검증 자동화
**본문**: Case #012의 재발 방지를 위해, PR 단계에서 Layer 4 게이트를 호출하여 lock 파일 동기화 여부를 강제해야 합니다.

### [PROPOSAL 2] Layer 1 컨텍스트 패커 초기 구현
**본문**: Claude Code가 작업 시작 시 과거 사고 사례를 ChromaDB에서 읽어올 수 있도록 컨텍스트 주입 로직을 시작해야 합니다.

### [PROPOSAL 3] API 명세 내 'Planned' 엔드포인트 실체화 로드맵
**본문**: docs/API_REFERENCE.md에 적힌 계획된 API들의 우선순위를 정하고 첫 번째 구현 대상을 확정해야 합니다.
        """
        print("-" * 40)
        print("Gemini CLI 분석 결과 제안 (Draft):")
        print("-" * 40)
        print(proposal)
        print("-" * 40)
        print("작업을 시작하려면 다음과 같이 실행하세요:")
        print("  planning_agent.py \"제목\" \"본문\"")

def main_api_mode():
    if len(sys.argv) < 3:
        print("Usage: planning_agent.py <title> <body> [discord_reply_url]")
        sys.exit(1)

    title = sys.argv[1]
    body = sys.argv[2]
    discord_url = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"🚀 지휘자 API를 통해 자율 개발 요청 중: {title}")

    payload = {
        "command": "develop",
        "issue_title": title,
        "issue_body": body,
        "discord_reply_url": discord_url
    }

    try:
        response = requests.post(f"{API_URL}/agent/trigger", json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "triggered":
                print(f"✅ 성공: {result.get('message')}")
                print(f"🔗 GitHub Actions 탭에서 진행 상황을 확인하세요.")
            else:
                print(f"❌ 실패: {result.get('message')}")
        else:
            print(f"❌ API 오류: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")

if __name__ == "__main__":
    run_planning_analysis()
