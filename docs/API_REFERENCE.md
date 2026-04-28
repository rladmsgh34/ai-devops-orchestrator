# 📚 API Reference

## LangChain API Endpoints

Base URL: `http://localhost:8000`

### `GET /health`
서비스 상태를 확인합니다.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-28T13:30:00Z",
  "version": "1.0.0",
  "ai_services": {
    "langchain": "available",
    "chromadb": "connected",
    "redis": "connected"
  }
}
```

### `POST /analyze`
에러 로그를 분석하고 해결책을 제안합니다.

**Request:**
```json
{
  "error_log": "Error: Cannot find module 'graceful-fs'",
  "project_config": {
    "repo_name": "my-project",
    "framework": "nextjs",
    "branch": "main"
  },
  "framework": "nextjs"
}
```

**Response:**
```json
{
  "pattern_type": "filesystem_dependency",
  "confidence": 0.90,
  "suggested_fixes": [
    "COPY --from=builder /app/node_modules/graceful-fs ./node_modules/graceful-fs",
    "COPY --from=builder /app/node_modules/retry ./node_modules/retry",
    "COPY --from=builder /app/node_modules/signal-exit ./node_modules/signal-exit"
  ],
  "similar_cases": [{
    "project": "gwangcheon-shop",
    "pattern": "proper-lockfile → graceful-fs 체인",
    "resolution_time": "3 minutes"
  }],
  "estimated_time_saved": "120 minutes"
}
```

### `POST /learn-success`
성공한 배포에서 학습합니다.

**Request:**
```json
{
  "commit": "abc123",
  "deployment": "success",
  "project": "my-app",
  "duration": "5 minutes"
}
```

**Response:**
```json
{
  "status": "learned",
  "timestamp": "2026-04-28T13:30:00Z"
}
```

### `POST /analyze-failure`
실패한 배포를 분석합니다.

**Request:**
```json
{
  "commit": "abc123",
  "logs": "Error: Cannot find module 'some-module'",
  "project": "my-app",
  "framework": "nextjs"
}
```

**Response:**
```json
{
  "status": "analyzed",
  "timestamp": "2026-04-28T13:30:00Z"
}
```

## 실제 검증된 패턴

### Prisma v7 의존성 체인
- **패턴**: `pure-rand` → `pathe` → `proper-lockfile` → `graceful-fs`
- **신뢰도**: 95%
- **해결 시간**: 5분
- **절약 시간**: 90-120분

### Docker Alpine 호환성
- **패턴**: `npx` 실행 실패
- **해결책**: 직접 경로 사용
- **신뢰도**: 99%
- **해결 시간**: 1분

### GitHub Actions 비용
- **패턴**: hosted runner 결제 실패
- **해결책**: self-hosted runner 전환
- **신뢰도**: 100%
- **절약**: 월 $500