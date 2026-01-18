"""
Harry Potter RAG System - Main Execution Module
Professional Edition for Seminar
"""
import json
import os
import faiss
import argparse
import time
from config import FAISS_INDEX_PATH
from rag_pipeline.retriever import retrieve
from rag_pipeline.prompt import build_prompt
from rag_pipeline.rag_chain import rag_answer

def print_boxed_response(text):
    """답변 내용을 깔끔한 테두리 박스에 담아 출력합니다."""
    lines = text.split('\n')
    # 터미널 너비에 맞춰 유동적으로 조절 (최대 80자)
    max_len = max(len(line) for line in lines) if lines else 0
    width = min(max_len, 80)
    
    border = "+" + "-" * (width + 4) + "+"
    print("\n" + border)
    print("| " + "FINAL AI RESPONSE".center(width + 2) + " |")
    print(border)
    for line in lines:
        # 긴 문장은 자르거나 그대로 출력 (데모용이므로 간단히 처리)
        print(f"|  {line.ljust(width)}  |")
    print(border + "\n")

def load_chunks_and_index():
    """청크 데이터와 FAISS 인덱스를 로드합니다."""
    chunks_path = "data/processed/chunks_metadata.json"
    if not os.path.exists(chunks_path):
        chunks_path = "data/processed/chunks.json"
    
    if not os.path.exists(chunks_path):
        print(f"[ERROR] Data file not found: {chunks_path}")
        return None, None
    
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"[ERROR] FAISS index not found: {FAISS_INDEX_PATH}")
        return None, None
    
    index = faiss.read_index(FAISS_INDEX_PATH)
    return chunks, index

def main():
    parser = argparse.ArgumentParser(description="Harry Potter RAG System")
    parser.add_argument("--query", type=str, default="Tell me about Harry Potter", help="User Query")
    parser.add_argument("--filter", type=str, default=None, help="Metadata Filter (JSON)")
    parser.add_argument("--k", type=int, default=3, help="Number of chunks to retrieve")
    args = parser.parse_args()

    print("[INFO] Initializing RAG System Components...")
    chunks, index = load_chunks_and_index()
    
    if chunks is None or index is None:
        return
    
    print(f"[INFO] Database: {len(chunks)} chunks loaded")
    print(f"[INFO] Index: FAISS loaded successfully\n")

    metadata_filter = None
    if args.filter:
        try:
            metadata_filter = json.loads(args.filter)
            print(f"[INFO] Metadata Filter Applied: {metadata_filter}")
        except json.JSONDecodeError:
            print(f"[WARN] Invalid filter format: {args.filter}")

    # 1. 검색 단계 (Retrieval)
    print(f"[QUERY] {args.query}")
    print("[PROCESS] Searching for relevant document chunks...")
    
    start_search = time.perf_counter()
    retrieved_chunks = retrieve(args.query, index, chunks, metadata_filter=metadata_filter, k=args.k)
    end_search = time.perf_counter()
    
    # 2. 검색 결과 리포트
    print("-" * 60)
    print(f"[DEBUG] Retrieval completed in {end_search - start_search:.4f}s")
    print("-" * 60)
    
    for i, chunk in enumerate(retrieved_chunks, 1):
        source = chunk.get('source_file', 'Unknown')
        print(f"[{i}] Source: {source}")
        print(f"    Preview: {chunk['text'][:150]}...")

    # 3. 답변 생성 단계 (Generation)
    print("\n" + "=" * 60)
    print("  GENERATING RESPONSE VIA LOCAL LLM (EXAONE 3.5)")
    print("=" * 60)
    
    contexts = [chunk['text'] for chunk in retrieved_chunks]
    prompt = build_prompt(contexts, args.query)
    
    # rag_answer 함수 내부에서 디버깅 로그가 찍힘
    answer = rag_answer(prompt)
    
    # 4. 박스 테두리 답변 출력
    print_boxed_response(answer)
    
    # 5. 출처 리스트 출력
    print("=" * 60)
    print("  REFERENCE LIST")
    print("=" * 60)
    sources = []
    for chunk in retrieved_chunks:
        info = chunk.get('source_file', 'unknown')
        if info not in sources:
            sources.append(info)
    
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()