#!/usr/bin/env python3
import sys
import os
import requests

# 설정
API_URL = os.getenv("CONDUCTOR_API_URL", "http://localhost:8000")

def main():
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
    main()
