#!/usr/bin/env python3
import sys
import os
import json
import requests
import argparse

# 지휘자 API 설정
API_URL = os.getenv("CONDUCTOR_API_URL", "http://localhost:8000")

def analyze_ci_failure(event_type, status, log_file):
    if not os.path.exists(log_file):
        print(f"Error: Log file {log_file} not found.")
        return

    with open(log_file, "r") as f:
        log_snippet = f.read()[-5000:] # 최근 5000자만 추출

    # 1. Layer 4 Gate 호출
    payload = {
        "project": os.getenv("GITHUB_REPOSITORY", "unknown"),
        "event_type": event_type,
        "status": status,
        "log_snippet": log_snippet
    }

    print(f"🤖 지휘자에게 검증 요청 중... ({event_type})")
    try:
        response = requests.post(f"{API_URL}/verify/gate", json=payload, timeout=10)
        result = response.json()
        
        print(f"--- 지휘자 판정 ---")
        print(f"판정: {result['decision'].upper()}")
        print(f"사유: {result['reason']}")
        if result.get("suggested_actions"):
            print("추천 조치:")
            for action in result["suggested_actions"]:
                print(f"  - {action}")
        
        # 2. 만약 지휘자가 모르는 에러라면 자동으로 케이스 인입 시도
        if result['decision'] == 'fail' and "미정의된" in result['reason']:
            print("🚩 새로운 에러 패턴 감지! 케이스 인입을 시도합니다...")
            ingest_payload = {
                "content": f"title: [CI FAILURE] {event_type} failed in {payload['project']}\n\n## 로그 스니펫\n```\n{log_snippet}\n```"
            }
            ingest_resp = requests.post(f"{API_URL}/cases/ingest", json=ingest_payload)
            if ingest_resp.status_code == 200:
                print(f"✅ 새 케이스가 후보로 등록되었습니다: {ingest_resp.json().get('message')}")

    except Exception as e:
        print(f"❌ 지휘자 연결 실패: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="event type (build/test/lint)")
    parser.add_argument("--log", required=True, help="path to log file")
    args = parser.parse_args()
    
    analyze_ci_failure(args.type, "failure", args.log)
