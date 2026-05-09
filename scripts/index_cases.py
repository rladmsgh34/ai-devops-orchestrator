#!/usr/bin/env python3
import os
import yaml
import chromadb
from pathlib import Path

# ChromaDB 설정
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "devops_knowledge")

def parse_case_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # YAML Frontmatter 파싱
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata, body
            except yaml.YAMLError as e:
                print(f"Error parsing frontmatter in {file_path}: {e}")
    
    return {}, content.strip()

def index_cases():
    print(f"🤖 ChromaDB 로컬 인덱싱 시작: {COLLECTION_NAME}")
    
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"❌ ChromaDB 연결 실패: {e}")
        return
    
    case_dir = Path("cases")
    if not case_dir.exists():
        print("Error: cases directory not found.")
        return

    indexed_count = 0
    for case_file in case_dir.glob("*.md"):
        if case_file.name in ["README.md", "TEMPLATE.md"]:
            continue
            
        print(f"Processing {case_file.name}...")
        metadata, body = parse_case_file(case_file)
        
        # 기본 메타데이터 보완
        case_id = metadata.get("id") or case_file.name.split("-")[0]
        metadata["id"] = str(case_id)
        metadata["source"] = case_file.name
        
        # 리스트 형태의 메타데이터 및 날짜 등을 문자열로 변환 (ChromaDB 제약)
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                metadata[key] = str(value)
            elif not isinstance(value, (str, int, float, bool)) and value is not None:
                metadata[key] = str(value)
        
        # 문서 추가 (id가 같으면 덮어씀)
        collection.upsert(
            documents=[body],
            metadatas=[metadata],
            ids=[str(case_id)]
        )
        indexed_count += 1
        
    print(f"✅ ChromaDB 인덱싱 완료 (총 {indexed_count}건)")

if __name__ == "__main__":
    index_cases()
