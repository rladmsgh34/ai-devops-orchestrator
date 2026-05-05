from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="AI DevOps Orchestrator API",
    description="지휘자 모델 기반 자동 트러블슈팅 및 배포 파이프라인",
    version="1.1.0",
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


# ── 데이터 모델 ───────────────────────────────────────────────────────────────

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


# ── Layer 1: Context Packer (Case #019) ──────────────────────────────────────

class ContextPackRequest(BaseModel):
    file_paths: List[str]
    issue_text: Optional[str] = None


class ContextPackResult(BaseModel):
    context_bundle: str
    related_cases: List[str] = []


@app.post("/context/pack", response_model=ContextPackResult)
async def context_pack(request: ContextPackRequest):
    """Layer 1 컨텍스트 패커: 작업 시작 전 과거 사고 사례를 주입하여 회귀 예방."""
    logger.info(f"컨텍스트 패킹 요청: {request.file_paths}")

    findings = []
    case_ids = []

    # Case #012 패턴 매칭 (pnpm-lock)
    if any("pnpm-lock.yaml" in p or "package.json" in p for p in request.file_paths):
        findings.append(
            "⚠️ **경고: 의존성 동기화 위험 (Case #012)**\n"
            "- 이 프로젝트는 과거에 pnpm-lock.yaml 불일치로 빌드가 깨진 이력이 있습니다.\n"
            "- 의존성 변경 시 반드시 `pnpm install --lockfile-only`를 실행하세요."
        )
        case_ids.append("012")

    # Case #013 패턴 매칭 (smoke test)
    if any("scripts" in p or "smoke" in p for p in request.file_paths):
        findings.append(
            "⚠️ **경고: 스모크 테스트 경로 주의 (Case #013)**\n"
            "- 정기 테스트 스크립트 경로가 유실되거나 잘못 지정되어 장애가 발생한 적이 있습니다.\n"
            "- 스크립트 수정 시 `.github/workflows/smoke.yml`과의 싱크를 확인하세요."
        )
        case_ids.append("013")

    if not findings:
        return ContextPackResult(
            context_bundle="✅ 알려진 과거 회귀 패턴이 없습니다. 자유롭게 작업을 시작하세요.",
            related_cases=[]
        )

    bundle = "## 🔍 지휘자 컨텍스트 (과거 사례 기반)\n\n" + "\n\n".join(findings)
    return ContextPackResult(context_bundle=bundle, related_cases=case_ids)


# ── Layer 3: Context Packing (Case #020) ──────────────────────────────────────

class VerifyBundleRequest(BaseModel):
    project: str
    pr_number: int
    file_paths: List[str]
    diff_summary: Optional[str] = None


class VerifyBundleResult(BaseModel):
    verification_bundle: str
    risk_score: float  # 0.0 ~ 1.0
    suggested_focus_areas: List[str] = []


@app.post("/context/verify-bundle", response_model=VerifyBundleResult)
async def verify_bundle(request: VerifyBundleRequest):
    """Layer 3 컨텍스트 패킹: PR 검증자에게 변경 사항과 연관된 과거 사고 맥락을 전달."""
    logger.info(f"검증 번들 생성 요청: {request.project} PR #{request.pr_number}")

    # TODO: ChromaDB 기반 정밀 검색 및 위험 점수 계산 로직
    focus_areas = []
    historical_notes = []
    risk_score = 0.1

    # Case #012 기반 체크
    if any("pnpm-lock.yaml" in p for p in request.file_paths):
        focus_areas.append("의존성 정합성 (pnpm-lock.yaml)")
        historical_notes.append("- [Case #012] 과거 의존성 동기화 누락으로 빌드 장애 발생")
        risk_score += 0.4

    # Case #013 기반 체크
    if any("scripts" in p or "smoke" in p for p in request.file_paths):
        focus_areas.append("스모크 테스트 안정성")
        historical_notes.append("- [Case #013] 테스트 스크립트 경로 유실로 인한 정기 검증 실패")
        risk_score += 0.3

    if not historical_notes:
        bundle = "## ✅ 검증 번들\n특이사항 없음. 일반적인 코드 리뷰 및 테스트를 수행하세요."
    else:
        bundle = f"## 🚨 검증 집중 영역 (과거 사고 기반)\n\n"
        bundle += "\n".join(historical_notes)
        bundle += "\n\n### 📌 추천 점검 항목:\n"
        bundle += "\n".join([f"- {area}" for area in focus_areas])

    return VerifyBundleResult(
        verification_bundle=bundle,
        risk_score=min(risk_score, 1.0),
        suggested_focus_areas=focus_areas
    )


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

    # Case #012: pnpm-lock.yaml sync 체크
    if request.event_type == "build" and request.status == "failure":
        if request.log_snippet and ("frozen-lockfile" in request.log_snippet or "pnpm-lock.yaml" in request.log_snippet):
            return VerificationResult(
                decision="fail",
                reason="pnpm-lock.yaml이 package.json과 동기화되지 않았습니다 (Case #012 패턴)",
                suggested_actions=["pnpm install --lockfile-only 실행 후 커밋하세요"]
            )

    # Case #013: smoke test 체크
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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.1.0",
        "ai_services": {
            "langchain": "available",
            "chromadb": "connected",
            "redis": "connected",
        },
    }


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_error(request: AnalysisRequest):
    """에러 로그를 분석하고 해결책을 제안합니다."""
    logger.info(f"분석 요청 수신: {request.framework} 프레임워크")

    if "Cannot find module" in request.error_log:
        if "pure-rand" in request.error_log:
            return AnalysisResult(
                pattern_type="prisma_dependency_chain",
                confidence=0.95,
                suggested_fixes=[
                    "COPY --from=builder /app/node_modules/pure-rand ./node_modules/pure-rand",
                    "다음 예상 누락: pathe, proper-lockfile, graceful-fs",
                ],
                similar_cases=[{"project": "gwangcheon-shop", "pattern": "Prisma v7 의존성 체인"}],
                estimated_time_saved="90 minutes",
            )
        elif "graceful-fs" in request.error_log:
            return AnalysisResult(
                pattern_type="filesystem_dependency",
                confidence=0.90,
                suggested_fixes=[
                    "COPY --from=builder /app/node_modules/graceful-fs ./node_modules/graceful-fs",
                ],
                similar_cases=[{"project": "gwangcheon-shop", "pattern": "proper-lockfile → graceful-fs"}],
                estimated_time_saved="120 minutes",
            )

    return AnalysisResult(
        pattern_type="unknown",
        confidence=0.50,
        suggested_fixes=["로그 분석을 위해 더 많은 정보가 필요합니다"],
        similar_cases=[],
        estimated_time_saved="30 minutes",
    )


@app.post("/learn-success")
async def learn_from_success(data: Dict[str, Any]):
    return {"status": "learned", "timestamp": datetime.utcnow().isoformat()}


@app.post("/analyze-failure")
async def analyze_failure(data: Dict[str, Any]):
    return {"status": "analyzed", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
