from ingest.embed import model

def retrieve(query, index, chunks, metadata_filter=None, k=3):
    """
    쿼리에 대한 유사한 청크를 검색합니다.
    
    Args:
        query: 검색 쿼리
        index: FAISS 인덱스
        chunks: 모든 청크 리스트
        metadata_filter: 메타데이터 필터 딕셔너리 (예: {"source": "review"})
        k: 반환할 청크 개수
    
    Returns:
        필터링된 청크 리스트
    """
    q_vec = model.encode([query])
    
    # 메타데이터 필터가 없으면 전체 검색
    if metadata_filter is None:
        ids = index.search(q_vec, k)[1][0]
        return [chunks[i] for i in ids]
    
    # 메타데이터 필터가 있으면 더 많이 검색한 후 필터링
    search_k = min(k * 10, len(chunks))  # 필터링을 위해 더 많이 검색
    ids = index.search(q_vec, search_k)[1][0]
    
    # 메타데이터 필터 적용
    filtered_chunks = []
    for i in ids:
        chunk = chunks[i]
        # 필터 조건 확인 (모든 키-값 쌍이 일치해야 함)
        match = all(
            chunk.get(key) == value 
            for key, value in metadata_filter.items()
        )
        if match:
            filtered_chunks.append(chunk)
            if len(filtered_chunks) >= k:
                break
    
    return filtered_chunks
