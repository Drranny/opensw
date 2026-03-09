import json
import sys
import os
import faiss

# 프로젝트 최상단 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.embed import model
from rank_bm25 import BM25Okapi
from rag_pipeline.retriever import retrieve

print("1. 코드 청크 로딩 중... 🚀")
with open("data/processed/chunks_structure_code.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("2. 임시 FAISS & BM25 인덱스 빌드 중... 🛠️")
texts = [c["text"] for c in chunks]
# 텍스트를 벡터로 변환하여 FAISS에 즉석 추가
embeddings = model.encode(texts).astype("float32")
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# BM25 인덱스 생성
bm25_index = BM25Okapi([t.split() for t in texts])

print("\n3. 검색 테스트 시작! 🔍\n" + "="*60)

# 테스트 질의 1: 덧셈 함수 찾기
query1 = "How to add two numbers?"
print(f"질문 1: {query1}")
results1 = retrieve(query1, index, chunks, k=1, bm25=bm25_index)
for res in results1:
    meta = res.get("metadata", {})
    print(f"[결과] 부모: {meta.get('parent')} | 고아 여부: {meta.get('is_orphan', False)}")
    print(f"코드:\n{res.get('text')}\n")

# 테스트 질의 2: 글로벌 설정 찾기
query2 = "testing status in global settings"
print(f"질문 2: {query2}")
results2 = retrieve(query2, index, chunks, k=1, bm25=bm25_index)
for res in results2:
    meta = res.get("metadata", {})
    print(f"[결과] 타입: {meta.get('node_type')} | 고아 여부: {meta.get('is_orphan', False)}")
    print(f"코드:\n{res.get('text')}\n")
print("="*60)
