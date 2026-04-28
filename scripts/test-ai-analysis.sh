#!/bin/bash

# AI DevOps Orchestrator - AI 분석 테스트 스크립트
# 실제 검증된 에러 패턴들을 테스트합니다

set -euo pipefail

API_URL="http://localhost:8000"

echo "🤖 AI DevOps Orchestrator - 분석 테스트"
echo "======================================"

# 헬스체크
echo "1. 헬스체크 테스트..."
curl -s "$API_URL/health" | jq '.'

echo
echo "2. Prisma pure-rand 에러 테스트..."
curl -s -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "error_log": "Error: Cannot find module '\''pure-rand'\''",
    "project_config": {
      "repo_name": "test-project",
      "framework": "nextjs"
    },
    "framework": "nextjs"
  }' | jq '.'

echo
echo "3. graceful-fs 에러 테스트..."
curl -s -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "error_log": "Error: Cannot find module '\''graceful-fs'\''",
    "project_config": {
      "repo_name": "test-project",
      "framework": "nextjs"
    },
    "framework": "nextjs"
  }' | jq '.'

echo
echo "4. 알려지지 않은 에러 테스트..."
curl -s -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "error_log": "Some unknown error occurred",
    "project_config": {
      "repo_name": "test-project",
      "framework": "django"
    },
    "framework": "django"
  }' | jq '.'

echo
echo "✅ AI 분석 테스트 완료!"