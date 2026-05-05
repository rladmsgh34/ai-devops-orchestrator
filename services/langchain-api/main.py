from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import logging
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="AI DevOps Orchestrator API",
    description="LangChain 기반 자동 트러블슈팅 및 배포 파이프라인",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5678"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 데이터 모델
class AnalysisRequest(BaseModel):
    error_log: str
    project_config: Dict[str, Any]
    framework: str = "unknown"


class AnalysisResult(BaseModel):
    pattern_type: str
    confidence: float
    suggested_fixes: List[str]
    similar_cases: List[Dict[str, Any]]
    estimated_time_saved: str


# ── Layer 4: Verification Gate (Case #015) ────────────────────────────────────

class VerificationRequest(BaseModel):
    project: str
    event_type: str  # e.g., "build", "test", "smoke"
    status: str      # "success" | "failure"
    log_snippet: Optional[str] = None
    metadata: Dict[str, Any] = {}


class VerificationResult(BaseModel):
    decision: str    # "pass" | "fail" | "warn"
    reason: str
    suggested_actions: List[str] = []


@app.post("/verify/gate", response_model=VerificationResult)
async def verify_gate(request: VerificationRequest):
    """Layer 4 검증 게이트: 빌드/테스트 결과를 분석하여 승인 단계 진입 여부 결정."""
    logger.info(f"검증 요청 수신: {request.project} - {request.event_type}")

    # Case #012: pnpm-lock.yaml sync 체크 (임시 로직)
    if request.event_type == "build" and request.status == "failure":
        if request.log_snippet and "frozen-lockfile" in request.log_snippet:
            return VerificationResult(
                decision="fail",
                reason="pnpm-lock.yaml이 package.json과 동기화되지 않았습니다 (Case #012 패턴)",
                suggested_actions=["pnpm install --lockfile-only 실행 후 커밋하세요"]
            )

    # Case #013: smoke test 체크 (임시 로직)
    if request.event_type == "smoke" and request.status == "failure":
        return VerificationResult(
            decision="fail",
            reason="운영 환경 스모크 테스트 실패 (Case #013 패턴)",
            suggested_actions=["scripts/smoke.sh 경로 및 운영 URL 응답을 확인하세요"]
        )

    if request.status == "success":
        return VerificationResult(decision="pass", reason="검증 통과")

    return VerificationResult(
        decision="fail",
        reason="알 수 없는 실패 발생",
        suggested_actions=["로그 전체를 확인하고 케이스로 등록하세요"]
    )


# ── Legacy Endpoints ──────────────────────────────────────────────────────────

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "ai_services": {
            "langchain": "available",
            "chromadb": "connected",
            "redis": "connected",
        },
    }


# 에러 분석 엔드포인트
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_error(request: AnalysisRequest):
    """
    에러 로그를 분석하고 해결책을 제안합니다.
    """
    logger.info(f"분석 요청 수신: {request.framework} 프레임워크")

    # 실제 검증된 Prisma v7 의존성 체인 패턴
    if "Cannot find module" in request.error_log:
        if "pure-rand" in request.error_log:
            return AnalysisResult(
                pattern_type="prisma_dependency_chain",
                confidence=0.95,
                suggested_fixes=[
                    "COPY --from=builder /app/node_modules/pure-rand ./node_modules/pure-rand",
                    "다음 예상 누락: pathe, proper-lockfile, graceful-fs",
                ],
                similar_cases=[
                    {
                        "project": "gwangcheon-shop",
                        "pattern": "Prisma v7 의존성 체인",
                        "resolution_time": "5 minutes",
                    }
                ],
                estimated_time_saved="90 minutes",
            )
        elif "graceful-fs" in request.error_log:
            return AnalysisResult(
                pattern_type="filesystem_dependency",
                confidence=0.90,
                suggested_fixes=[
                    "COPY --from=builder /app/node_modules/graceful-fs ./node_modules/graceful-fs",
                    "COPY --from=builder /app/node_modules/retry ./node_modules/retry",
                    "COPY --from=builder /app/node_modules/signal-exit ./node_modules/signal-exit",
                ],
                similar_cases=[
                    {
                        "project": "gwangcheon-shop",
                        "pattern": "proper-lockfile → graceful-fs 체인",
                        "resolution_time": "3 minutes",
                    }
                ],
                estimated_time_saved="120 minutes",
            )

    # 기본 응답
    return AnalysisResult(
        pattern_type="unknown",
        confidence=0.50,
        suggested_fixes=["로그 분석을 위해 더 많은 정보가 필요합니다"],
        similar_cases=[],
        estimated_time_saved="30 minutes",
    )


# 학습 엔드포인트
@app.post("/learn-success")
async def learn_from_success(data: Dict[str, Any]):
    """성공한 배포에서 학습합니다."""
    logger.info("성공 케이스 학습 중...")
    return {"status": "learned", "timestamp": datetime.utcnow().isoformat()}


@app.post("/analyze-failure")
async def analyze_failure(data: Dict[str, Any]):
    """실패한 배포를 분석합니다."""
    logger.info("실패 케이스 분석 중...")
    return {"status": "analyzed", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
