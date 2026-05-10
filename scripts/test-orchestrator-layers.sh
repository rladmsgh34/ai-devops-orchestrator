#!/bin/bash

# AI DevOps Orchestrator - 레이어별 기능 테스트 스크립트
# Layer 1, 3, 4 기능을 테스트합니다

set -euo pipefail

API_URL="http://localhost:8000"

echo "🤖 지휘자 모델 레이어 테스트"
echo "======================================"

# Layer 1: Context Packer
echo "1. Layer 1 (Context Packer) 테스트..."
curl -s -X POST "$API_URL/context/pack" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["services/api/pnpm-lock.yaml"],
    "issue_text": "의존성 업데이트가 필요함"
  }' | jq '.'

echo
# Layer 3: Context Packing
echo "2. Layer 3 (Context Packing) 테스트..."
curl -s -X POST "$API_URL/context/verify-bundle" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "pr_number": 123,
    "file_paths": ["scripts/smoke-test.sh"],
    "diff_summary": "스모크 테스트 스크립트 수정"
  }' | jq '.'

echo
# Layer 4: Verification Gate
echo "3. Layer 4 (Verification Gate) 테스트 - 실패 사례..."
curl -s -X POST "$API_URL/verify/gate" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "event_type": "build",
    "status": "failure",
    "log_snippet": "ERR_PNPM_OUT-OF-SYNC: Lockfile is up-to-date with pnpm-lock.yaml but not with package.json"
  }' | jq '.'

echo
# Layer 5: Approval Gate
echo "4. Layer 5 (Approval Gate) 테스트..."
curl -s -X POST "$API_URL/verify/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "gwangcheon-shop",
    "pr_number": 123,
    "approver": "user123",
    "sha": "abc1234567890"
  }' | jq '.'

echo
echo "✅ 지휘자 모델 레이어 테스트 완료!"
