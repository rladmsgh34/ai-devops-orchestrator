#!/usr/bin/env python3
import os
import re
import sys
from datetime import datetime

def get_next_case_info():
    case_dir = 'cases'
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
        return 0, '000'
    
    case_files = [f for f in os.listdir(case_dir) if re.match(r'^\d{3}-.*\.md$', f)]
    if not case_files:
        return 0, '000'
    
    last_case = sorted(case_files)[-1]
    last_id = int(last_case.split('-')[0])
    next_id = last_id + 1
    return next_id, f"{next_id:03d}"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9가-힣]+', '-', text)
    return text.strip('-')

def ingest_case():
    print("Reading issue content from stdin...")
    content = sys.stdin.read()
    if not content.strip():
        print("Error: No content provided.")
        sys.exit(1)

    # Extract title from the issue (looking for [CASE] in title or the first section)
    title_search = re.search(r'title: \[CASE\] (.*)', content)
    if not title_search:
        # Try to find the first header or just use a default
        first_line = content.strip().split('\n')[0]
        title = first_line.replace('# ', '').replace('[CASE] ', '').strip()
    else:
        title = title_search.group(1).strip()

    if not title or title == "New Case":
        title = "Untitled Case"

    next_id_int, next_id_str = get_next_case_info()
    slug = slugify(title)
    if not slug:
        slug = "case"
    
    file_name = f"{next_id_str}-{slug[:30]}.md"
    file_path = os.path.join('cases', file_name)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Prepare the skeleton
    skeleton = f"""---
id: {next_id_str}
title: {title}
date: {date_str}
project: gwangcheon-shop
actor_involved: [user]
state: open
related_pr: 
related_components: []
---

# Case {next_id_str} — {title}

**TL;DR.** [이슈 요약 및 핵심 통찰을 작성하세요]

## 1. 무슨 일이 있었나 (사실)

{content.strip()}

## 7. 학습 (ChromaDB 인덱싱 대상)

[이 케이스를 통해 배운 점을 한 문단으로 작성하세요]
"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(skeleton)
    
    print(f"✅ Created: {file_path}")

    # Update cases/README.md index
    readme_path = 'cases/README.md'
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the last line of the table
        last_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(f"| {next_id_int - 1:03d} |"):
                last_index = i
                break
        
        new_entry = f"| {next_id_str} | {title} | ⏳ | [TBD] |\n"
        
        if last_index != -1:
            lines.insert(last_index + 1, new_entry)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ Updated: {readme_path} index")
        else:
            print(f"⚠️ Could not find index table in {readme_path}. Please update manually.")

if __name__ == "__main__":
    ingest_case()
