import os
import sys
import json
import re

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def extract_metadata(fname: str, text: str) -> dict:
    """
    파일명과 내용을 기반으로 메타데이터를 추출합니다.
    
    Returns:
        dict: 메타데이터 딕셔너리
    """
    metadata = {
        "source_file": fname,
    }
    
    # Book 파일 처리 (Book1.txt ~ Book7.txt)
    if fname.startswith("Book") and fname.endswith(".txt"):
        book_num = re.search(r"Book(\d+)", fname)
        if book_num:
            metadata.update({
                "source": "book",
                "series": "harry_potter",
                "volume": int(book_num.group(1))
            })
        return metadata
    
    # 주문 목록 (lore)
    if fname == "hp_spells_list.txt":
        metadata.update({
            "source": "lore",
            "topic": "spells"
        })
        return metadata
    
    # harrypotter1_X.txt 파일들 처리
    if fname.startswith("harrypotter1_"):
        # 파일 내용을 기반으로 타입 판단
        text_lower = text.lower()
        
        # 리뷰 판단 (영화 리뷰 관련 키워드)
        if any(keyword in text_lower for keyword in [
            "review", "blu-ray", "film", "movie", "cinema", 
            "director", "actor", "performance", "screenplay"
        ]):
            # critic vs audience 판단
            review_type = "critic"  # 기본값
            if any(keyword in text_lower for keyword in [
                "audience", "viewer", "fan", "rating", "imdb"
            ]):
                review_type = "audience"
            
            metadata.update({
                "source": "review",
                "movie": "harry_potter_1",  # 첫 번째 영화 리뷰로 추정
                "type": review_type
            })
            return metadata
        
        # 캐릭터 정보 판단
        if any(keyword in text_lower for keyword in [
            "character", "protagonist", "harry potter", "dumbledore", 
            "voldemort", "hermione", "ron weasley", "appearance", 
            "personality", "characterisation"
        ]):
            # 어떤 캐릭터인지 추출 시도
            character = "unknown"
            if "harry potter" in text_lower and "character" in text_lower:
                character = "harry_potter"
            elif "dumbledore" in text_lower:
                character = "dumbledore"
            elif "voldemort" in text_lower or "dark lord" in text_lower:
                character = "voldemort"
            
            metadata.update({
                "source": "lore",
                "topic": "character",
                "character": character
            })
            return metadata
        
        # 시리즈 개요/정보
        if any(keyword in text_lower for keyword in [
            "overview", "series", "novels", "author", "j. k. rowling",
            "published", "genre", "themes", "reception", "impact"
        ]):
            metadata.update({
                "source": "lore",
                "topic": "overview"
            })
            return metadata
        
        # 마법/로어 관련
        if any(keyword in text_lower for keyword in [
            "magic", "spell", "wand", "wizard", "wizarding world"
        ]):
            metadata.update({
                "source": "lore",
                "topic": "magic"
            })
            return metadata
    
    # 기본값: 알 수 없는 경우
    metadata.update({
        "source": "unknown",
        "topic": "unknown"
    })
    return metadata


all_chunks = []

for fname in sorted(os.listdir(RAW_DIR)):
    if not fname.endswith(".txt"):
        continue

    path = os.path.join(RAW_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 메타데이터 추출
    metadata = extract_metadata(fname, text)
    
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks):
        chunk_data = {
            "source_file": fname,
            "chunk_id": i,
            "text": chunk,
            **metadata  # 메타데이터 병합
        }
        all_chunks.append(chunk_data)

    print(f"{fname}: {len(chunks)} chunks (metadata: {metadata})")

# chunk 결과 저장
out_path = os.path.join(OUT_DIR, "chunks.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"\nTotal chunks: {len(all_chunks)}")
print(f"Saved to {out_path}")
