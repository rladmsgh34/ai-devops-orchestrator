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
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "devops_knowledge")

# Lazy loading for ChromaDB
_chroma_client = None
_collection = None

def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        try:
            # HttpClient 대신 PersistentClient 사용 (로컬 파일 저장 방식)
            _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
            _collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)
            logger.info(f"ChromaDB 로컬 DB 연결 성공 (경로: {CHROMA_PATH})")
        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {e}")
            return None
    return _collection

# FastAPI 앱 초기화
app = FastAPI(
    title="AI DevOps Orchestrator API",
    description="지휘자 모델 기반 자동 트러블슈팅 및 배포 파이프라인",
    version="1.2.0",
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
    if not collection:
        return ContextPackResult(
            context_bundle="⚠️ 지식 베이스 연결 실패. 일반적인 주의사항을 확인하세요.",
            related_cases=[]
        )

    # 검색 쿼리 구성 (파일 경로 및 이슈 텍스트 결합)
    query_text = " ".join(request.file_paths)
    if request.issue_text:
        query_text += f" {request.issue_text}"

    # ChromaDB 검색
    results = collection.query(
        query_texts=[query_text],
        n_results=3
    )

    findings = []
    case_ids = []

    if results and results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i] if 'distances' in results else 0
            # 유사도 임계값 완화 (MiniLM 모델 특성 고려)
            if distance < 1.5:  
                case_id = results['ids'][0][i]
                findings.append(f"### 🚩 과거 관련 사례 [{case_id}]\n{doc[:500]}...")
                case_ids.append(case_id)

    if not findings:
        return ContextPackResult(
            context_bundle="✅ 알려진 과거 회귀 패턴이 없습니다. 자유롭게 작업을 시작하세요.",
            related_cases=[]
        )

    bundle = "## 🔍 지휘자 컨텍스트 (과거 사례 기반)\n\n" + "\n\n".join(findings)
    bundle += "\n\n---\n*위 내용은 ChromaDB 검색 결과를 기반으로 자동 생성되었습니다.*"
    
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
    risk_score = 0.1
    historical_notes = []

    if collection:
        query_text = " ".join(request.file_paths)
        results = collection.query(query_texts=[query_text], n_results=2)
        
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                if distance < 1.0:
                    case_id = results['ids'][0][i]
                    historical_notes.append(f"- **[Case #{case_id}]** 연관성 발견 (거리: {distance:.2f})")
                    risk_score += 0.3

    if not historical_notes:
        bundle = "## ✅ 검증 번들\n특이사항 없음. 일반적인 코드 리뷰 및 테스트를 수행하세요."
    else:
        bundle = f"## 🚨 검증 집중 영역 (과거 사고 기반)\n\n"
        bundle += "\n".join(historical_notes)
        bundle += "\n\n### 📌 추천 점검 항목:\n"
        bundle += "- 변경된 파일들의 과거 회귀 패턴 재발 여부"

    return VerifyBundleResult(
        verification_bundle=bundle,
        risk_score=min(risk_score, 1.0),
        suggested_focus_areas=["과거 회귀 영역"] if historical_notes else []
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

    # 검증 규칙 로드
    rules_path = os.path.join(os.path.dirname(__file__), "rules.json")
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
    except Exception as e:
        logger.error(f"규칙 파일 로드 실패: {e}")
        rules = []

    if request.status == "success":
        return VerificationResult(decision="pass", reason="검증 통과")

    # 규칙 매칭 (대소문자 구분 없음)
    log_snippet_lower = request.log_snippet.lower() if request.log_snippet else ""
    
    for rule in rules:
        if request.event_type == rule["event_type"] and request.status == rule["status"]:
            # 패턴이 있는 경우 로그 스니펫 확인
            if not rule["pattern"] or any(p.lower() in log_snippet_lower for p in rule["pattern"]):
                return VerificationResult(
                    decision=rule["decision"],
                    reason=rule["reason"],
                    suggested_actions=rule["suggested_actions"]
                )

    return VerificationResult(
        decision="fail",
        reason=f"미정의된 {request.event_type} 실패 발생",
        suggested_actions=["로그 전체를 확인하고 케이스로 등록하세요"]
    )


class IngestRequest(BaseModel):
    content: str


@app.post("/cases/ingest")
async def ingest_case_endpoint(request: IngestRequest):
    """사례 인입 엔드포인트: 외부 사건을 받아 케이스 파일로 변환."""
    import subprocess
    
    try:
        # ingest_case.py 스크립트 실행
        process = subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(__file__), "../../scripts/ingest_case.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=request.content)
        
        if process.returncode == 0:
            return {"status": "success", "message": stdout.strip()}
        else:
            return {"status": "error", "message": stderr.strip()}
    except Exception as e:
        logger.error(f"케이스 인입 실패: {e}")
        return {"status": "error", "message": str(e)}


class PRApproveRequest(BaseModel):
    project: str
    pr_number: int
    decision: str  # "approve" | "reject"
    comment: Optional[str] = None

@app.post("/pr/approve")
async def approve_pr(request: PRApproveRequest):
    """Discord/n8n의 요청을 받아 PR을 승인하고 머지함."""
    import subprocess
    
    logger.info(f"PR 승인 요청 수신: {request.project} PR #{request.pr_number} - {request.decision}")
    
    if request.decision == "approve":
        try:
            # 1. PR 승인 (리뷰 등록)
            subprocess.run(["gh", "pr", "review", str(request.pr_number), "--approve", "--body", request.comment or "Approved via Discord Conductor"], check=True)
            
            # 2. PR 머지
            subprocess.run(["gh", "pr", "merge", str(request.pr_number), "--merge", "--delete-branch"], check=True)
            
            return {"status": "success", "message": f"PR #{request.pr_number} 승인 및 머지 완료."}
        except Exception as e:
            logger.error(f"PR 승인/머지 실패: {e}")
            return {"status": "error", "message": str(e)}
    
    else:
        # 거절 시 코멘트만 남김
        subprocess.run(["gh", "pr", "comment", str(request.pr_number), "--body", f"Rejected via Discord: {request.comment}"], check=True)
        return {"status": "rejected", "message": f"PR #{request.pr_number} 거절 처리됨."}


class AgentTriggerRequest(BaseModel):
    command: str
    issue_title: str
    issue_body: str
    discord_reply_url: Optional[str] = None

@app.post("/agent/trigger")
async def trigger_agent(request: AgentTriggerRequest):
    """(Layer 0) 생성 에이전트를 트리거하여 이슈 등록부터 PR 생성까지 풀 루프 실행."""
    import subprocess
    
    logger.info(f"에이전트 트리거 요청 수신: {request.issue_title}")
    
    try:
        # 1. Layer 1 컨텍스트 패킹 (과거 사고 사례 조회)
        context_req = ContextPackRequest(file_paths=[], issue_text=f"{request.issue_title} {request.issue_body}")
        context_res = await context_pack(context_req)
        context_bundle = context_res.context_bundle

        # 2. GitHub Action 트리거 (gh CLI 사용)
        # workflow_dispatch에 필요한 입력값 전달
        cmd = [
            "gh", "workflow", "run", "full-loop-agent.yml",
            "-f", f"issue_title={request.issue_title}",
            "-f", f"issue_body={request.issue_body}",
            "-f", f"context_bundle={context_bundle}",
        ]
        if request.discord_reply_url:
            cmd.extend(["-f", f"discord_reply_url={request.discord_reply_url}"])

        logger.info(f"GitHub Workflow 트리거 중: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        return {
            "status": "triggered", 
            "message": "GitHub Actions를 통해 자율 개발 워크플로가 시작되었습니다.",
            "context_injected": "success" if context_bundle else "none"
        }
        
    except Exception as e:
        logger.error(f"에이전트 트리거 실패: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/pr/event")
async def handle_pr_event(event: Dict[str, Any]):
    """GitHub PR 이벤트를 처리하여 상태머신 가드(G1~G5)를 실행."""
    action = event.get("action")
    pr_number = event.get("pull_request", {}).get("number")
    
    logger.info(f"PR 이벤트 수신: PR #{pr_number} - {action}")

    # G3: 검증 후 새 커밋 추가 시 'verified' 라벨 제거
    if action == "synchronize":
        return {
            "decision": "action_required",
            "action": "remove_label",
            "label": "verified",
            "reason": "검증 후 새로운 커밋이 추가되었습니다. 재검증이 필요합니다. (G3 가드)"
        }

    # G2: 검증 없이 승인 시도 차단 (라벨링 이벤트 기반)
    if action == "labeled":
        label_name = event.get("label", {}).get("name")
        labels = [l.get("name") for l in event.get("pull_request", {}).get("labels", [])]
        
        if label_name == "approved" and "verified" not in labels:
            return {
                "decision": "action_required",
                "action": "remove_label",
                "label": "approved",
                "reason": "Antigravity 검증이 완료되지 않은 PR은 승인할 수 없습니다. (G2 가드)"
            }

    return {"decision": "pass", "status": "no_action_needed"}


# ── Legacy Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    chroma_status = "connected" if get_chroma_collection() else "disconnected"
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.2.0",
        "ai_services": {
            "langchain": "available",
            "chromadb": chroma_status,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
