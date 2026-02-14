"""
Retrieval evaluation script for HitRate@K and MRR.

Usage:
    python3 scripts/eval_retrieval.py \
      --queries data/eval/queries_text.jsonl \
      --chunks data/processed/chunks_fixed_metadata.json \
      --index vector_db/faiss_fixed.index \
      --k 5 \
      --out results/text_fixed_metrics.json
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple

import faiss

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest.embed import model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate retrieval metrics")
    parser.add_argument("--queries", required=True, help="JSONL query file path")
    parser.add_argument("--chunks", required=True, help="Chunk metadata JSON path")
    parser.add_argument("--index", required=True, help="FAISS index path")
    parser.add_argument("--k", type=int, default=5, help="Top-K")
    parser.add_argument("--out", required=True, help="Output metrics JSON path")
    return parser.parse_args()


def load_queries(path: str) -> List[Dict]:
    queries: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            queries.append(json.loads(line))
    return queries


def load_chunks(chunks_path: str) -> List[Dict]:
    with open(chunks_path, "r", encoding="utf-8") as f:
        return json.load(f)


def retrieve_top_k(query: str, index: faiss.Index, chunks: List[Dict], k: int) -> List[str]:
    query_vec = model.encode([query]).astype("float32")
    ids = index.search(query_vec, k)[1][0]

    sources: List[str] = []
    for idx in ids:
        if idx < 0 or idx >= len(chunks):
            continue
        sources.append(chunks[idx].get("source_file", "Unknown"))
    return sources


def evaluate(queries: List[Dict], index: faiss.Index, chunks: List[Dict], k: int) -> Tuple[Dict, List[Dict]]:
    evaluated = 0
    hit_count = 0
    mrr_sum = 0.0
    skipped = 0
    per_query: List[Dict] = []

    for q in queries:
        gold_sources = q.get("gold_sources") or []
        if not gold_sources:
            skipped += 1
            continue

        evaluated += 1
        query = q["query"]
        qid = q.get("qid", f"q_{evaluated}")
        retrieved_sources = retrieve_top_k(query, index, chunks, k)

        rank = None
        for i, src in enumerate(retrieved_sources, start=1):
            if src in gold_sources:
                rank = i
                break

        hit = rank is not None
        rr = 0.0 if rank is None else 1.0 / rank
        if hit:
            hit_count += 1
        mrr_sum += rr

        per_query.append(
            {
                "qid": qid,
                "query": query,
                "gold_sources": gold_sources,
                "retrieved_sources": retrieved_sources,
                "hit": hit,
                "reciprocal_rank": rr,
            }
        )

    metrics = {
        "k": k,
        "total_queries": len(queries),
        "evaluated_queries": evaluated,
        "skipped_queries": skipped,
        "hit_rate_at_k": 0.0 if evaluated == 0 else hit_count / evaluated,
        "mrr": 0.0 if evaluated == 0 else mrr_sum / evaluated,
    }
    return metrics, per_query


def main() -> None:
    args = parse_args()
    queries = load_queries(args.queries)
    chunks = load_chunks(args.chunks)
    index = faiss.read_index(args.index)
    metrics, per_query = evaluate(queries, index, chunks, args.k)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "details": per_query}, f, ensure_ascii=False, indent=2)

    print(f"[DONE] Saved metrics to {args.out}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
