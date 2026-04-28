#!/bin/bash

# AI DevOps Orchestrator - 원클릭 설치 스크립트
# Version: 1.0.0
# Author: AI DevOps Team

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로고 출력
print_logo() {
    echo -e "${BLUE}"
    cat << "EOF"
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║     🤖 AI DevOps Orchestrator                                        ║
    ║                                                                      ║
    ║     LangChain + n8n 기반 자동 트러블슈팅 및 배포 파이프라인            ║
    ║                                                                      ║
    ║     ⚡ 디버깅 시간 1-2시간 → 5분 (2400% 효율 향상)                    ║
    ║     🌐 멀티 프레임워크 지원 (Next.js, Django, React, Vue, Spring)    ║
    ║     🧠 실시간 학습 및 예측적 문제 해결                                 ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 시스템 요구사항 확인
check_requirements() {
    log_step "시스템 요구사항 확인 중..."

    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다. https://docs.docker.com/get-docker/ 에서 설치해주세요."
        exit 1
    else
        log_success "Docker 설치 확인 ✓"
    fi

    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    else
        log_success "Docker Compose 설치 확인 ✓"
    fi

    # Git 확인
    if ! command -v git &> /dev/null; then
        log_error "Git이 설치되지 않았습니다."
        exit 1
    else
        log_success "Git 설치 확인 ✓"
    fi

    # 최소 메모리 확인 (4GB)
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -lt 4 ]; then
        log_warning "권장 최소 메모리(4GB)보다 적습니다. 현재: ${total_mem}GB"
        read -p "계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "메모리 요구사항 확인 ✓ (${total_mem}GB)"
    fi
}

# 환경변수 설정
setup_environment() {
    log_step "환경변수 설정 중..."

    if [ ! -f .env ]; then
        log_info ".env 파일이 없습니다. .env.example에서 복사 중..."
        cp .env.example .env
        log_success ".env 파일 생성 완료"
    else
        log_info ".env 파일이 이미 존재합니다."
    fi

    # JWT Secret 자동 생성
    if ! grep -q "JWT_SECRET=" .env || grep -q "JWT_SECRET=your-random-jwt-secret" .env; then
        log_info "JWT Secret 자동 생성 중..."
        JWT_SECRET=$(openssl rand -base64 32)
        sed -i "s/JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET}/" .env
        log_success "JWT Secret 생성 완료"
    fi

    # GitHub Webhook Secret 자동 생성
    if ! grep -q "GITHUB_WEBHOOK_SECRET=" .env || grep -q "GITHUB_WEBHOOK_SECRET=your-random-secret-string" .env; then
        log_info "GitHub Webhook Secret 자동 생성 중..."
        WEBHOOK_SECRET=$(openssl rand -hex 16)
        sed -i "s/GITHUB_WEBHOOK_SECRET=.*/GITHUB_WEBHOOK_SECRET=${WEBHOOK_SECRET}/" .env
        log_success "GitHub Webhook Secret 생성 완료"
    fi
}

# API 키 설정 확인
check_api_keys() {
    log_step "API 키 설정 확인 중..."

    local has_openai=false
    local has_anthropic=false
    local has_google=false

    if grep -q "OPENAI_API_KEY=sk-" .env; then
        has_openai=true
        log_success "OpenAI API 키 확인 ✓"
    fi

    if grep -q "ANTHROPIC_API_KEY=sk-ant-" .env; then
        has_anthropic=true
        log_success "Anthropic API 키 확인 ✓"
    fi

    if grep -q "GOOGLE_AI_API_KEY=AIza" .env; then
        has_google=true
        log_success "Google AI API 키 확인 ✓"
    fi

    if [ "$has_openai" = false ] && [ "$has_anthropic" = false ] && [ "$has_google" = false ]; then
        log_warning "AI API 키가 설정되지 않았습니다."
        echo -e "${CYAN}다음 중 하나 이상의 API 키를 .env 파일에 설정해주세요:${NC}"
        echo "  - OPENAI_API_KEY=sk-..."
        echo "  - ANTHROPIC_API_KEY=sk-ant-..."
        echo "  - GOOGLE_AI_API_KEY=AIza..."
        echo
        read -p "나중에 설정하고 계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # GitHub Token 확인
    if ! grep -q "GITHUB_TOKEN=ghp_" .env; then
        log_warning "GitHub Token이 설정되지 않았습니다."
        echo -e "${CYAN}GitHub Personal Access Token을 .env 파일에 설정해주세요:${NC}"
        echo "  - GITHUB_TOKEN=ghp_..."
        echo "  - 권한: repo, workflow, admin:repo_hook"
        echo
    else
        log_success "GitHub Token 확인 ✓"
    fi
}

# Docker 이미지 빌드
build_images() {
    log_step "Docker 이미지 빌드 중..."

    # LangChain API 이미지 빌드
    if [ -d "services/langchain-api" ]; then
        log_info "LangChain API 이미지 빌드 중..."
        docker build -t ai-devops-orchestrator/langchain-api:latest services/langchain-api/
        log_success "LangChain API 이미지 빌드 완료"
    else
        log_warning "services/langchain-api 디렉토리가 없습니다. 이미지를 수동으로 빌드해주세요."
    fi
}

# 서비스 시작
start_services() {
    log_step "서비스 시작 중..."

    # 기본 서비스 시작
    log_info "핵심 서비스 시작 중..."
    docker-compose up -d langchain-api n8n chromadb redis postgres

    # 서비스 상태 확인
    log_info "서비스 시작 대기 중... (30초)"
    sleep 30

    # 헬스체크
    check_services_health
}

# 서비스 상태 확인
check_services_health() {
    log_step "서비스 상태 확인 중..."

    local services=("langchain-api:8000" "n8n:5678" "chromadb:8001" "redis:6379")
    local all_healthy=true

    for service in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service"
        if curl -f -s "http://localhost:${port}" > /dev/null 2>&1 ||
           curl -f -s "http://localhost:${port}/health" > /dev/null 2>&1 ||
           curl -f -s "http://localhost:${port}/api/v1/heartbeat" > /dev/null 2>&1; then
            log_success "${service_name} 서비스 정상 ✓"
        else
            log_error "${service_name} 서비스 응답 없음"
            all_healthy=false
        fi
    done

    if [ "$all_healthy" = true ]; then
        log_success "모든 핵심 서비스가 정상적으로 실행 중입니다!"
    else
        log_warning "일부 서비스에 문제가 있을 수 있습니다. 로그를 확인해주세요."
        echo "  docker-compose logs [service-name]"
    fi
}

# 선택적 서비스 시작
start_optional_services() {
    log_step "선택적 서비스 시작 여부 확인 중..."

    echo -e "${CYAN}추가 서비스를 시작하시겠습니까?${NC}"

    # 모니터링 서비스
    read -p "모니터링 서비스 (Prometheus, Grafana)를 시작하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "모니터링 서비스 시작 중..."
        docker-compose --profile monitoring up -d
        log_success "모니터링 서비스 시작 완료"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3001 (admin/admin)"
    fi

    # 로깅 서비스
    read -p "로깅 서비스 (ELK Stack)를 시작하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "로깅 서비스 시작 중..."
        docker-compose --profile logging up -d
        log_success "로깅 서비스 시작 완료"
        echo "  - Elasticsearch: http://localhost:9200"
        echo "  - Kibana: http://localhost:5601"
    fi
}

# 최종 설정 안내
print_final_info() {
    log_step "설치 완료!"

    echo -e "${GREEN}"
    cat << "EOF"
    🎉 AI DevOps Orchestrator가 성공적으로 설치되었습니다!

    📋 접속 정보:
    ├── 🤖 LangChain API:     http://localhost:8000
    ├── ⚡ n8n 워크플로우:     http://localhost:5678
    ├── 🧠 ChromaDB:         http://localhost:8001
    └── 🔧 Redis:            http://localhost:6379

    🚀 다음 단계:
    1. .env 파일에서 API 키 설정 확인
    2. GitHub Webhook 설정 (n8n에서)
    3. 첫 번째 프로젝트 모니터링 시작

    📚 문서: https://github.com/rladmsgh34/ai-devops-orchestrator/wiki
    💬 지원: https://github.com/rladmsgh34/ai-devops-orchestrator/discussions
EOF
    echo -e "${NC}"

    # 유용한 명령어들
    echo -e "${CYAN}유용한 명령어들:${NC}"
    echo "  docker-compose logs -f                 # 모든 서비스 로그 확인"
    echo "  docker-compose logs -f langchain-api   # 특정 서비스 로그 확인"
    echo "  docker-compose restart [service]       # 서비스 재시작"
    echo "  docker-compose down                     # 모든 서비스 중지"
    echo "  docker-compose down -v                 # 모든 서비스 중지 + 데이터 삭제"
    echo
}

# 메인 설치 프로세스
main() {
    clear
    print_logo

    log_info "AI DevOps Orchestrator 설치를 시작합니다..."
    echo

    # 단계별 설치
    check_requirements
    echo

    setup_environment
    echo

    check_api_keys
    echo

    build_images
    echo

    start_services
    echo

    start_optional_services
    echo

    print_final_info
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi