from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
import sys
import json
import chromadb
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ChromaDB 설정
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMADB_PORT", 8000))
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "devops_knowledge")

# Lazy loading for ChromaDB
_chroma_client = None
_collection = None

def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        try:
            # PersistentClient (로컬 파일 저장) 또는 HttpClient (서버 접속) 선택
            if os.getenv("CHROMA_MODE") == "http":
                _chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                logger.info(f"ChromaDB HttpClient 연결 성공: {CHROMA_HOST}:{CHROMA_PORT}")
            else:
                _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
                logger.info(f"ChromaDB PersistentClient 연결 성공 (경로: {CHROMA_PATH})")
            
            _collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)
        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {e}")
            return None
    return _collection

# FastAPI 앱 초기화
app = FastAPI(
    title="AI DevOps Orchestrator API",
    description="지휘자 모델 기반 자동 트러블슈팅 및 배포 파이프라인",
    version="1.3.0",
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

    collection = get_chroma_collection()
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
    if collection:
        query = request.issue_text or ""
        if request.file_paths:
            query += " " + " ".join(request.file_paths)
        
        if query.strip():
            results = collection.query(query_texts=[query], n_results=3)
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    cid = results['ids'][0][i]
                    if cid not in case_ids:
                        summary = doc[:200].strip().replace("\n", " ") + "..."
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

    collection = get_chroma_collection()
    focus_areas = []
    historical_notes = []
    risk_score = 0.1

    # 1. 하드코딩된 체크
    if any("pnpm-lock.yaml" in p for p in request.file_paths):
        focus_areas.append("의존성 정합성 (pnpm-lock.yaml)")
        historical_notes.append("- [Case #012] 과거 의존성 동기화 누락으로 빌드 장애 발생")
        risk_score += 0.4

    if any("scripts" in p or "smoke" in p for p in request.file_paths):
        focus_areas.append("스모크 테스트 안정성")
        historical_notes.append("- [Case #013] 테스트 스크립트 경로 유실로 인한 정기 검증 실패")
        risk_score += 0.3

    # 2. ChromaDB 시맨틱 검색 (Case #020 실체화)
    if collection:
        query = request.diff_summary or ""
        if request.file_paths:
            query += " " + " ".join(request.file_paths)

        if query.strip():
            results = collection.query(query_texts=[query], n_results=2)
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    cid = results['ids'][0][i]
                    if not any(f"Case #{cid}" in note for note in historical_notes):
                        historical_notes.append(f"- [Case #{cid}] 유사 사고 탐지: {doc[:100]}...")
                        risk_score += 0.2

    if not historical_notes:
        bundle = "## ✅ 검증 번들\n특이사항 없음. 일반적인 코드 리뷰 및 테스트를 수행하세요."
    else:
        bundle = f"## 🚨 검증 집중 영역 (과거 사고 기반)\n\n"
        bundle += "\n".join(historical_notes)
        bundle += "\n\n### 📌 추천 점검 항목:\n"
        bundle += "\n".join([f"- {area}" for area in focus_areas]) if focus_areas else "- 유사 사고 사례의 해결 방식 재현 여부 확인"

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

    # 검증 규칙 로드 (rules.json 활용)
    rules_path = os.path.join(os.path.dirname(__file__), "rules.json")
    rules = []
    if os.path.exists(rules_path):
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                rules = json.load(f)
        except Exception as e:
            logger.error(f"규칙 파일 로드 실패: {e}")

    if request.status == "success":
        return VerificationResult(decision="pass", reason="검증 통과")

    # 규칙 매칭
    log_snippet_lower = request.log_snippet.lower() if request.log_snippet else ""
    for rule in rules:
        if request.event_type == rule["event_type"] and request.status == rule["status"]:
            if not rule["pattern"] or any(p.lower() in log_snippet_lower for p in rule["pattern"]):
                return VerificationResult(
                    decision=rule["decision"],
                    reason=rule["reason"],
                    suggested_actions=rule["suggested_actions"]
                )

    # 하드코딩된 폴백 (Case #012, #013)
    if request.event_type == "build" and request.status == "failure":
        if "frozen-lockfile" in log_snippet_lower or "pnpm-lock.yaml" in log_snippet_lower:
            return VerificationResult(
                decision="fail",
                reason="pnpm-lock.yaml이 package.json과 동기화되지 않았습니다 (Case #012 패턴)",
                suggested_actions=["pnpm install --lockfile-only 실행 후 커밋하세요"]
            )

    return VerificationResult(
        decision="fail",
        reason=f"미정의된 {request.event_type} 실패 발생",
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

    if not request.sha:
        return ApproveResult(
            status="rejected",
            message="커밋 SHA 정보가 누락되었습니다. 승인할 대상이 불분명합니다."
        )

    deployment_id = f"dep-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.sha[:7]}"
    
    return ApproveResult(
        status="approved",
        deployment_id=deployment_id,
        message=f"[{request.approver}] 승인 확인됨. SHA {request.sha[:7]} 배포를 시작합니다."
    )


class ObserveRequest(BaseModel):
    project: str
    deployment_id: str
    metrics: Dict[str, Any]
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

    ERROR_THRESHOLD = 0.01
    LATENCY_THRESHOLD = 500

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


# ── Automation & Training (Case #023, #027) ─────────────────────────────────

class LearnRecordRequest(BaseModel):
    case_id: Optional[str] = None
    title: str
    content: str
    metadata: Dict[str, Any] = {}


@app.post("/learn/record")
async def learn_record(request: LearnRecordRequest):
    """학습 루프: 성공/실패 사례를 ChromaDB에 저장하여 지식 베이스 확장."""
    collection = get_chroma_collection()
    if not collection:
        return {"status": "error", "message": "ChromaDB 연결 실패"}

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
        return {"status": "success", "id": record_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class AgentTriggerRequest(BaseModel):
    command: str
    issue_title: str
    issue_body: str
    discord_reply_url: Optional[str] = None


@app.post("/agent/trigger")
async def trigger_agent(request: AgentTriggerRequest):
    """(Case #027) 생성 에이전트 트리거: 이슈 등록부터 PR 생성까지 풀 루프 실행."""
    import subprocess
    logger.info(f"에이전트 트리거 요청 수신: {request.issue_title}")
    
    try:
        # 1. Context Packing
        context_req = ContextPackRequest(file_paths=[], issue_text=f"{request.issue_title} {request.issue_body}")
        context_res = await context_pack(context_req)
        context_bundle = context_res.context_bundle

        # 2. Trigger GitHub Action
        cmd = [
            "gh", "workflow", "run", "full-loop-agent.yml",
            "-f", f"issue_title={request.issue_title}",
            "-f", f"issue_body={request.issue_body}",
            "-f", f"context_bundle={context_bundle}",
        ]
        if request.discord_reply_url:
            cmd.extend(["-f", f"discord_reply_url={request.discord_reply_url}"])

        subprocess.run(cmd, check=True)
        return {"status": "triggered", "message": "GitHub Actions 워크플로가 시작되었습니다."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/pr/event")
async def handle_pr_event(event: Dict[str, Any]):
    """GitHub PR 이벤트 처리 및 상태머신 가드 실행."""
    action = event.get("action")
    pr_number = event.get("pull_request", {}).get("number")
    
    if action == "synchronize":
        return {
            "decision": "action_required",
            "action": "remove_label",
            "label": "verified",
            "reason": "새 커밋 추가로 인한 재검증 필요 (G3 가드)"
        }

    if action == "labeled":
        label_name = event.get("label", {}).get("name")
        labels = [l.get("name") for l in event.get("pull_request", {}).get("labels", [])]
        if label_name == "approved" and "verified" not in labels:
            return {
                "decision": "action_required",
                "action": "remove_label",
                "label": "approved",
                "reason": "검증(verified)되지 않은 PR 승인 차단 (G2 가드)"
            }

    return {"decision": "pass"}


# ── Legacy & Health ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.3.0",
        "chromadb": "connected" if get_chroma_collection() else "disconnected"
    }


@app.post("/analyze")
async def analyze_error(request: AnalysisRequest):
    # 기존 키워드 매칭 로직 유지
    if "Cannot find module" in request.error_log:
        return {
            "pattern_type": "dependency_missing",
            "confidence": 0.9,
            "suggested_fixes": ["Dockerfile에 의존성 복사 구문 추가 확인"],
            "estimated_time_saved": "60m"
        }
    return {"pattern_type": "unknown", "confidence": 0.5}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
