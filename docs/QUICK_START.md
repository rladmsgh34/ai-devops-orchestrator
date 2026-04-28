# 🚀 Quick Start Guide

## 3분 설치

### 1. 사전 요구사항
- Docker & Docker Compose
- Git  
- API 키 (OpenAI, Anthropic, 또는 Google AI)
- GitHub Personal Access Token

### 2. 설치
```bash
git clone https://github.com/rladmsgh34/ai-devops-orchestrator.git
cd ai-devops-orchestrator
./setup.sh
```

### 3. 접속
- **n8n**: http://localhost:5678 (admin/changeme)
- **LangChain API**: http://localhost:8000
- **ChromaDB**: http://localhost:8001

## 첫 번째 프로젝트 연결

### 1. GitHub Token 설정
```bash
# .env 파일에 추가
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=your-organization
MONITORED_PROJECTS=my-nextjs-app,my-django-api
```

### 2. Webhook 등록
1. n8n (http://localhost:5678) 접속
2. GitHub Integration workflow 활성화  
3. Repository Settings → Webhooks → Add webhook
4. URL: `http://your-domain.com:5678/webhook/github-webhook`
5. Content type: `application/json`
6. Events: `Push`, `Pull requests`

### 3. 첫 배포 테스트
1. Repository에 Push 또는 PR 생성
2. n8n에서 워크플로우 실행 확인
3. LangChain API에서 AI 분석 결과 확인
4. ChromaDB에서 학습 데이터 축적 확인

## 실제 검증된 사례

### Prisma v7 의존성 체인 해결
```
에러: Cannot find module 'pure-rand'
AI 분석: Prisma v7 의존성 체인 감지
해결책: COPY --from=builder /app/node_modules/pure-rand ./node_modules/pure-rand
결과: 2시간 → 5분으로 단축 ✅
```

### Docker Alpine 호환성 문제
```
에러: npx prisma generate 실행 실패
AI 분석: Alpine 환경 바이너리 resolve 문제
해결책: node node_modules/prisma/build/index.js 직접 경로
결과: 즉시 해결 ✅
```

완료! 🎉 이제 AI가 자동으로 배포 문제를 학습하고 해결합니다.