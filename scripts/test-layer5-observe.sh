#!/bin/bash

# AI DevOps Orchestrator - Layer 5 Observation & Learning 테스트 스크립트
# Layer 5의 Observe 및 Learn 기능을 테스트합니다.

set -euo pipefail

API_URL="http://localhost:8000"

echo "🤖 Layer 5 관찰 및 학습 루프 테스트"
echo "======================================"

# 1. Layer 5: Observe (Stable Case)
echo "1. Layer 5 (Observe) 테스트 - 안정적 배포..."
curl -s -X POST "$API_URL/verify/observe" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "deployment_id": "dep-20260510-abc1234",
    "metrics": {
      "error_rate": 0.002,
      "p95_latency_ms": 150
    }
  }' | jq '.'

echo
# 2. Layer 5: Observe (Unstable Case)
echo "2. Layer 5 (Observe) 테스트 - 불안정한 배포 (고에러율)..."
curl -s -X POST "$API_URL/verify/observe" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "deployment_id": "dep-20260510-abc1234",
    "metrics": {
      "error_rate": 0.05,
      "p95_latency_ms": 200
    }
  }' | jq '.'

echo
# 3. Layer 5: Observe (Degraded Case)
echo "3. Layer 5 (Observe) 테스트 - 성능 저하 배포 (고레이턴시)..."
curl -s -X POST "$API_URL/verify/observe" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "deployment_id": "dep-20260510-abc1234",
    "metrics": {
      "error_rate": 0.001,
      "p95_latency_ms": 800
    }
  }' | jq '.'

echo
# 4. Learning Loop: Record Success
echo "4. Learning Loop (Record) 테스트 - 성공 사례 기록..."
curl -s -X POST "$API_URL/learn/record" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "성공적인 로컬 이미지 업로드 마이그레이션",
    "content": "GCS 의존성을 제거하고 로컬 스토리지로 전환함. 배포 후 에러율 0.1% 미만 유지.",
    "metadata": {
      "project": "gwangcheon-shop",
      "type": "success",
      "tags": ["migration", "local-storage"]
    }
  }' | jq '.'

echo
echo "✅ Layer 5 관찰 및 학습 루프 테스트 스크립트 작성 완료!"
