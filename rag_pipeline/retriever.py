from ingest.embed import model


def _rrf_score(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


def retrieve(query, index, chunks, metadata_filter=None, k=3, bm25=None):
    """
    쿼리에 대한 유사한 청크를 검색합니다.

    Args:
        query: 검색 쿼리
        index: FAISS 인덱스
        chunks: 모든 청크 리스트
        metadata_filter: 메타데이터 필터 딕셔너리 (예: {"source": "review"})
        k: 반환할 청크 개수
        bm25: BM25 인덱스 (선택적). 주어지면 FAISS와 RRF로 결합

    Returns:
        필터링된 청크 리스트
    """
    # k의 10배수와 1000개 중 더 큰 값을 선택하되, 전체 청크 개수를 넘지 않도록 안전장치 마련
    search_k = min(max(k * 10, 1000), len(chunks))
    q_vec = model.encode([query])

    # FAISS 검색
    faiss_ids = index.search(q_vec, search_k)[1][0]

    if bm25 is None:
        # BM25 없이 FAISS 단독 검색
        candidate_ids = list(faiss_ids)
        if metadata_filter is None:
            return [chunks[i] for i in candidate_ids[:k]]
        # metadata_filter 적용
        filtered = []
        for i in candidate_ids:
            chunk = chunks[i]
            if all(chunk.get(key) == value for key, value in metadata_filter.items()):
                filtered.append(chunk)
                if len(filtered) >= k:
                    break
        return filtered

    # BM25 검색
    tokens = query.split()
    bm25_scores = bm25.get_scores(tokens)
    bm25_ids = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:search_k]

    # RRF 점수 계산
    rrf: dict[int, float] = {}
    for rank, idx in enumerate(faiss_ids):
        if idx < 0:
            continue
        rrf[idx] = rrf.get(idx, 0.0) + _rrf_score(rank)
    for rank, idx in enumerate(bm25_ids):
        rrf[idx] = rrf.get(idx, 0.0) + _rrf_score(rank)

    # RRF 점수 내림차순 정렬
    ranked_ids = sorted(rrf, key=lambda i: rrf[i], reverse=True)

    if metadata_filter is None:
        return [chunks[i] for i in ranked_ids[:k]]

    # metadata_filter 적용
    filtered = []
    for i in ranked_ids:
        chunk = chunks[i]
        if all(chunk.get(key) == value for key, value in metadata_filter.items()):
            filtered.append(chunk)
            if len(filtered) >= k:
                break
    return filtered
