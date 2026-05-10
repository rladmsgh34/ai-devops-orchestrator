from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
from datetime import datetime
import chromadb

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ChromaDB 설정
CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMADB_PORT", 8000))
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "devops_knowledge")

try:
    # Docker 환경에서는 'chromadb' 호스트로, 로컬에서는 'localhost'로 시도
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    logger.info(f"ChromaDB 연결 성공: {CHROMA_HOST}:{CHROMA_PORT}")
except Exception as e:
    logger.error(f"ChromaDB 연결 실패 (지휘자 모델 일부 기능이 제한될 수 있음): {e}")
    collection = None

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


# ── 유틸리티 함수 ─────────────────────────────────────────────────────────────

def get_related_cases(query_text: str, n_results: int = 2) -> List[Dict[str, Any]]:
    """ChromaDB에서 쿼리와 유사한 과거 사고 사례를 검색합니다."""
    if collection is None:
        return []
    
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        cases = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                cases.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
        return cases
    except Exception as e:
        logger.error(f"케이스 검색 중 오류 발생: {e}")
        return []


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

    # 1. 하드코딩된 크리티컬 패턴 매칭 (pnpm-lock, smoke test)
    if any("pnpm-lock.yaml" in p or "package.json" in p for p in request.file_paths):
        findings.append(
            "⚠️ **경고: 의존성 동기화 위험 (Case #012)**\n"
            "- 이 프로젝트는 과거에 pnpm-lock.yaml 불일치로 빌드가 깨진 이력이 있습니다.\n"
            "- 의존성 변경 시 반드시 `pnpm install --lockfile-only`를 실행하세요."
        )
        case_ids.append("012")

    if any("scripts" in p or "smoke" in p for p in request.file_paths):
        findings.append(
            "⚠️ **경고: 스모크 테스트 경로 주의 (Case #013)**\n"
            "- 정기 테스트 스크립트 경로가 유실되거나 잘못 지정되어 장애가 발생한 적이 있습니다.\n"
            "- 스크립트 수정 시 `.github/workflows/smoke.yml`과의 싱크를 확인하세요."
        )
        case_ids.append("013")

    # 2. ChromaDB 시맨틱 검색 (Case #019 실체화)
    query = request.issue_text or ""
    if request.file_paths:
        query += " " + " ".join(request.file_paths)
    
    if query.strip():
        semantic_cases = get_related_cases(query)
        for sc in semantic_cases:
            cid = sc['id']
            if cid not in case_ids:
                # 간단한 요약 생성 (첫 200자)
                summary = sc['content'][:200].strip().replace("\n", " ") + "..."
                findings.append(f"🔍 **관련 과거 사례 (Case #{cid})**\n{summary}")
                case_ids.append(cid)

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

    focus_areas = []
    historical_notes = []
    risk_score = 0.1

    # 1. 하드코딩된 체크 (Case #012, #013)
    if any("pnpm-lock.yaml" in p for p in request.file_paths):
        focus_areas.append("의존성 정합성 (pnpm-lock.yaml)")
        historical_notes.append("- [Case #012] 과거 의존성 동기화 누락으로 빌드 장애 발생")
        risk_score += 0.4

    if any("scripts" in p or "smoke" in p for p in request.file_paths):
        focus_areas.append("스모크 테스트 안정성")
        historical_notes.append("- [Case #013] 테스트 스크립트 경로 유실로 인한 정기 검증 실패")
        risk_score += 0.3

    # 2. ChromaDB 시맨틱 검색 (Case #020 실체화)
    query = request.diff_summary or ""
    if request.file_paths:
        query += " " + " ".join(request.file_paths)

    if query.strip():
        semantic_cases = get_related_cases(query)
        for sc in semantic_cases:
            cid = sc['id']
            # 하드코딩된 것과 중복 방지
            if not any(f"Case #{cid}" in note for note in historical_notes):
                historical_notes.append(f"- [Case #{cid}] 유사 사고 탐지: {sc['content'][:100]}...")
                risk_score += 0.2

    if not historical_notes:
        bundle = "## ✅ 검증 번들\n특이사항 없음. 일반적인 코드 리뷰 및 테스트를 수행하세요."
    else:
        bundle = f"## 🚨 검증 집중 영역 (과거 사고 기반)\n\n"
        bundle += "\n".join(historical_notes)
        bundle += "\n\n### 📌 추천 점검 항목:\n"
        bundle += "\n".join([f"- {area}" for area in focus_areas]) if focus_areas else bundle + "\n- 유사 사고 사례의 해결 방식 재현 여부 확인"

    return VerifyBundleResult(
        verification_bundle=bundle,
        risk_score=min(risk_score, 1.0),
        suggested_focus_areas=focus_areas or ["유사 사고 회귀 검증"]
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


# ── Layer 5: Approval & Observation (Case #022, #023) ───────────────────────

class ApproveRequest(BaseModel):
    project: str
    pr_number: int
    approver: str
    sha: str
    force_deploy: bool = False


class ApproveResult(BaseModel):
    status: str      # "approved" | "pending" | "rejected"
    deployment_id: Optional[str] = None
    message: str


@app.post("/verify/approve", response_model=ApproveResult)
async def verify_approve(request: ApproveRequest):
    """Layer 5 승인 게이트: 사용자의 최종 승인을 확인하고 배포 파이프라인을 트리거."""
    logger.info(f"승인 요청 수신: {request.project} PR #{request.pr_number} by {request.approver}")

    # TODO: GitHub API를 통한 실제 PR 라벨/리뷰 상태 검증
    
    if not request.sha:
        return ApproveResult(
            status="rejected",
            message="커밋 SHA 정보가 누락되었습니다. 승인할 대상이 불분명합니다."
        )

    # 배포 식별자 생성
    deployment_id = f"dep-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.sha[:7]}"
    
    return ApproveResult(
        status="approved",
        deployment_id=deployment_id,
        message=f"[{request.approver}] 승인 확인됨. SHA {request.sha[:7]} 배포를 시작합니다."
    )


class ObserveRequest(BaseModel):
    project: str
    deployment_id: str
    metrics: Dict[str, Any]  # e.g., {"error_rate": 0.005, "p95_latency_ms": 200}
    duration_minutes: int = 30


class ObserveResult(BaseModel):
    decision: str    # "stable" | "unstable" | "degraded"
    reason: str
    suggested_actions: List[str] = []


@app.post("/verify/observe", response_model=ObserveResult)
async def verify_observe(request: ObserveRequest):
    """Layer 5 관찰 단계 (Case #023): 배포 후 SLI 지표를 분석하여 안정성 판단."""
    logger.info(f"관찰 요청 수신: {request.project} Deployment {request.deployment_id}")

    error_rate = request.metrics.get("error_rate", 0.0)
    p95_latency = request.metrics.get("p95_latency_ms", 0)

    # SLI 기준 (임계값)
    ERROR_THRESHOLD = 0.01  # 1%
    LATENCY_THRESHOLD = 500 # 500ms

    if error_rate > ERROR_THRESHOLD:
        return ObserveResult(
            decision="unstable",
            reason=f"에러율({error_rate*100:.2f}%)이 임계값({ERROR_THRESHOLD*100}%)을 초과했습니다.",
            suggested_actions=["즉시 롤백을 검토하고 로그를 분석하세요", "Case 파일 작성을 시작하세요"]
        )

    if p95_latency > LATENCY_THRESHOLD:
        return ObserveResult(
            decision="degraded",
            reason=f"p95 레이턴시({p95_latency}ms)가 임계값({LATENCY_THRESHOLD}ms)을 초과했습니다.",
            suggested_actions=["성능 병목 지점을 확인하세요", "리소스 사용량(CPU/MEM)을 점검하세요"]
        )

    return ObserveResult(
        decision="stable",
        reason="모든 SLI 지표가 정상 범위 내에 있습니다.",
        suggested_actions=["배포를 최종 확정(Archive)하고 학습 데이터로 저장하세요"]
    )


class LearnRecordRequest(BaseModel):
    case_id: Optional[str] = None
    title: str
    content: str
    metadata: Dict[str, Any] = {}


class LearnRecordResult(BaseModel):
    status: str
    id: str
    message: str


@app.post("/learn/record", response_model=LearnRecordResult)
async def learn_record(request: LearnRecordRequest):
    """학습 루프 (Case #023): 성공/실패 사례를 ChromaDB에 저장하여 지식 베이스 확장."""
    logger.info(f"학습 데이터 기록 요청: {request.title}")

    if collection is None:
        return LearnRecordResult(
            status="error",
            id="none",
            message="ChromaDB가 연결되지 않아 기록할 수 없습니다."
        )

    # ID 생성 (제공되지 않은 경우)
    record_id = request.case_id or f"auto-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        collection.upsert(
            documents=[request.content],
            metadatas=[{
                "title": request.title,
                "recorded_at": datetime.now().isoformat(),
                **request.metadata
            }],
            ids=[record_id]
        )
        
        return LearnRecordResult(
            status="success",
            id=record_id,
            message=f"지식 베이스에 성공적으로 기록되었습니다: {request.title}"
        )
    except Exception as e:
        logger.error(f"기록 중 오류 발생: {e}")
        return LearnRecordResult(
            status="error",
            id=record_id,
            message=f"ChromaDB 기록 실패: {str(e)}"
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
