#!/usr/bin/env python3
import os
import re
import chromadb
from pathlib import Path

# ChromaDB 설정
CHROMA_HOST = os.getenv("CHROMADB_HOST") or "localhost"
CHROMA_PORT = int(os.getenv("CHROMADB_PORT") or 8000)
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME") or "devops_knowledge"

def index_cases():
    print(f"🤖 ChromaDB 인덱싱 시작: {COLLECTION_NAME}")
    
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    case_dir = Path("cases")
    if not case_dir.exists():
        print("Error: cases directory not found.")
        return

    for case_file in case_dir.glob("*.md"):
        if case_file.name == "README.md" or case_file.name == "TEMPLATE.md":
            continue
            
        print(f"Processing {case_file.name}...")
        with open(case_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 간단한 메타데이터 및 본문 분리
        # 실 구현 시에는 프론트매터 파싱 필요
        case_id = case_file.name.split("-")[0]
        
        # 문서 추가 (id가 같으면 덮어씀)
        collection.upsert(
            documents=[content],
            metadatas=[{"id": case_id, "source": case_file.name}],
            ids=[case_id]
        )
        
    print("✅ ChromaDB 인덱싱 완료")

if __name__ == "__main__":
    index_cases()
