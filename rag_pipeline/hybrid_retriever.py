"""
Hybrid Search Retriever: BM25 + FAISS Vector Search with RRF (Reciprocal Rank Fusion)
"""

from typing import List, Dict, Any, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from rank_bm25 import BM25Okapi


class HybridRetriever(BaseRetriever):
    """
    Hybrid Search Retriever that combines BM25 keyword search and FAISS vector search
    using Reciprocal Rank Fusion (RRF) algorithm for re-ranking.
    """
    
    vectorstore: Any  # FAISS VectorStore 객체
    bm25: BM25Okapi  # BM25 검색 객체
    docs: List[Document]  # 원본 Document 리스트
    k: int = 60  # RRF 상수
    top_k: int = 5  # 각 검색기에서 반환할 문서 개수
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        vectorstore: Any,
        docs: List[Document],
        k: int = 60,
        top_k: int = 5
    ):
        """
        Initialize HybridRetriever with FAISS vectorstore and documents.
        
        Args:
            vectorstore: FAISS VectorStore 객체
            docs: BM25 인덱싱을 위한 원본 Document 리스트
            k: RRF 상수 (기본값 60)
            top_k: 각 검색기에서 반환할 문서 개수 (기본값 5)
        """
        # BM25 인덱스 생성
        bm25 = self._build_bm25_index(docs)
        
        super().__init__(
            vectorstore=vectorstore,
            bm25=bm25,
            docs=docs,
            k=k,
            top_k=top_k
        )
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        간단한 토크나이저: 공백 기준으로 분리하고 소문자로 변환
        
        Args:
            text: 토큰화할 텍스트
            
        Returns:
            토큰 리스트
        """
        return text.lower().split()
    
    def _build_bm25_index(self, docs: List[Document]) -> BM25Okapi:
        """
        Document 리스트로부터 BM25 인덱스를 생성
        
        Args:
            docs: Document 리스트
            
        Returns:
            BM25Okapi 객체
        """
        # 각 Document의 page_content를 토큰화
        tokenized_docs = [self._tokenize(doc.page_content) for doc in docs]
        
        # BM25 인덱스 생성
        return BM25Okapi(tokenized_docs)
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        쿼리에 대해 Hybrid Search를 수행하고 RRF로 재순위화
        
        Args:
            query: 검색 쿼리
            run_manager: 콜백 매니저
            metadata_filter: 메타데이터 필터 (예: {"source": ["Book1.txt"]})
            
        Returns:
            재순위화된 Document 리스트
        """
        # 1. Vector Search (FAISS)
        vector_results = self._vector_search(query, metadata_filter)
        
        # 2. Keyword Search (BM25)
        bm25_results = self._bm25_search(query, metadata_filter)
        
        # 3. RRF (Reciprocal Rank Fusion)로 결과 결합
        hybrid_results = self._reciprocal_rank_fusion(
            vector_results,
            bm25_results
        )
        
        return hybrid_results[:self.top_k]
    
    def _vector_search(
        self,
        query: str,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        FAISS Vector Search 수행
        
        Args:
            query: 검색 쿼리
            metadata_filter: 메타데이터 필터
            
        Returns:
            검색된 Document 리스트 (순위 정보 포함)
        """
        # FAISS 검색 (필터 지원)
        if metadata_filter:
            # VectorStore의 similarity_search 메서드에 filter 전달
            results = self.vectorstore.similarity_search(
                query,
                k=self.top_k,
                filter=metadata_filter
            )
        else:
            results = self.vectorstore.similarity_search(
                query,
                k=self.top_k
            )
        
        return results
    
    def _bm25_search(
        self,
        query: str,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        BM25 Keyword Search 수행
        
        Args:
            query: 검색 쿼리
            metadata_filter: 메타데이터 필터
            
        Returns:
            검색된 Document 리스트
        """
        # 쿼리 토큰화
        tokenized_query = self._tokenize(query)
        
        # BM25 검색
        if metadata_filter:
            # 필터링된 문서에 대해서만 검색
            filtered_docs = self._apply_metadata_filter(self.docs, metadata_filter)
            
            if not filtered_docs:
                return []
            
            # 필터링된 문서의 인덱스 생성
            filtered_bm25 = self._build_bm25_index(filtered_docs)
            
            # BM25 스코어 계산
            scores = filtered_bm25.get_scores(tokenized_query)
            
            # 스코어 기준 상위 top_k개 선택
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:self.top_k]
            
            results = [filtered_docs[i] for i in top_indices]
        else:
            # 전체 문서에서 검색
            results = self.bm25.get_top_n(
                tokenized_query,
                self.docs,
                n=self.top_k
            )
        
        return results
    
    def _apply_metadata_filter(
        self,
        docs: List[Document],
        metadata_filter: Dict[str, Any]
    ) -> List[Document]:
        """
        메타데이터 필터를 적용하여 문서 필터링
        
        Args:
            docs: 원본 Document 리스트
            metadata_filter: 메타데이터 필터
            
        Returns:
            필터링된 Document 리스트
        """
        filtered = []
        
        for doc in docs:
            match = True
            
            for key, value in metadata_filter.items():
                # 리스트 값인 경우 (예: {"source": ["Book1.txt", "Book2.txt"]})
                if isinstance(value, list):
                    if doc.metadata.get(key) not in value:
                        match = False
                        break
                # 단일 값인 경우
                else:
                    if doc.metadata.get(key) != value:
                        match = False
                        break
            
            if match:
                filtered.append(doc)
        
        return filtered
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Document],
        bm25_results: List[Document]
    ) -> List[Document]:
        """
        RRF (Reciprocal Rank Fusion) 알고리즘으로 검색 결과 결합
        
        RRF 공식: Score = Σ (1 / (k + rank_i))
        - k: 상수 (보통 60)
        - rank_i: 해당 문서가 각 검색기에서 몇 등 했는지 (1-indexed)
        
        두 검색 결과에 모두 등장한 문서는 점수를 합산하고,
        한쪽에만 등장한 문서는 그쪽 점수만 가집니다.
        
        Args:
            vector_results: Vector Search 결과 (순위순)
            bm25_results: BM25 Search 결과 (순위순)
            
        Returns:
            RRF 점수 기준 정렬된 Document 리스트
        """
        # 문서별 RRF 점수 계산을 위한 딕셔너리
        # Key: 문서 식별자 (page_content의 해시값 사용)
        # Value: (RRF 점수, Document 객체)
        doc_scores: Dict[str, tuple[float, Document]] = {}
        
        # Vector Search 결과의 RRF 점수 계산
        for rank, doc in enumerate(vector_results, start=1):
            # 문서 식별자 생성 (page_content 기준)
            doc_id = self._get_doc_id(doc)
            
            # RRF 점수 계산: 1 / (k + rank)
            rrf_score = 1.0 / (self.k + rank)
            
            # 점수 저장
            if doc_id not in doc_scores:
                doc_scores[doc_id] = (rrf_score, doc)
            else:
                # 이미 존재하면 점수 합산
                existing_score = doc_scores[doc_id][0]
                doc_scores[doc_id] = (existing_score + rrf_score, doc)
        
        # BM25 Search 결과의 RRF 점수 계산
        for rank, doc in enumerate(bm25_results, start=1):
            doc_id = self._get_doc_id(doc)
            
            # RRF 점수 계산
            rrf_score = 1.0 / (self.k + rank)
            
            # 점수 저장 또는 합산
            if doc_id not in doc_scores:
                doc_scores[doc_id] = (rrf_score, doc)
            else:
                existing_score = doc_scores[doc_id][0]
                doc_scores[doc_id] = (existing_score + rrf_score, doc)
        
        # RRF 점수 기준으로 정렬 (내림차순)
        sorted_docs = sorted(
            doc_scores.values(),
            key=lambda x: x[0],
            reverse=True
        )
        
        # Document 객체만 추출하여 반환
        return [doc for score, doc in sorted_docs]
    
    @staticmethod
    def _get_doc_id(doc: Document) -> str:
        """
        Document의 고유 식별자 생성
        
        Args:
            doc: Document 객체
            
        Returns:
            문서 식별자 (page_content의 해시값)
        """
        # page_content를 기준으로 해시값 생성
        return str(hash(doc.page_content))
