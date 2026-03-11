# 팀 온보딩: RAG 팟 분리 운영 가이드

## 아키텍처(쿠버네티스 기준)
- `rag-api`:
  - 역할: 사용자 질의 수신, Hybrid Retrieval(BM25+FAISS), 프롬프트 구성
  - 입력: Query
  - 출력: 최종 답변(또는 LLM 호출용 프롬프트)
- `rag-llm`:
  - 역할: EXAONE 모델 로딩/추론
  - 입력: Prompt
  - 출력: Generated text
- 저장소:
  - `data/processed/*`, `vector_db/*.index`는 재생성 가능 파일
  - 운영에서는 이미지 포함 또는 PVC/S3에서 공급

## 현재 코드 기준 모듈 맵
- 진입점: `main.py`
- Retrieval: `rag_pipeline/hybrid_retriever.py`, `rag_pipeline/retriever.py`
- Prompt 구성: `rag_pipeline/prompt.py`
- LLM 호출: `rag_pipeline/rag_chain.py`
- 인덱스 생성: `scripts/build_index.py`

## 팟 분리 시 코드 수정 포인트(최소)
1. `rag_pipeline/rag_chain.py`
   - 현재: 로컬에서 EXAONE 모델 직접 로딩
   - 분리 후: `rag-llm` 서비스 HTTP 호출 클라이언트로 교체
2. `main.py`
   - 현재: 검색 후 `rag_answer(prompt)` 직접 호출
   - 분리 후: 동일 인터페이스로 LLM 서비스 결과 수신
3. `config.py`
   - `LLM_SERVICE_URL` 환경변수 추가

## 권장 환경변수
- `FAISS_INDEX_PATH`
- `CHUNKS_PATH` (예: `data/processed/chunks_metadata.json`)
- `LLM_SERVICE_URL` (예: `http://rag-llm:8001/generate`)
- `TOP_K`, `RRF_K`

## 로컬(쿠버네티스 없이) 개발 방식
- 프론트 팀은 우선 `main.py` 단일 프로세스로 기능 검증
- 백엔드 API 래핑 후 프론트 연동
- 이후 LLM 호출만 서비스 분리

## 새 팀원 체크리스트
1. `pip install -r requirements.txt`
2. 샘플 데이터 준비 (`data/raw` 또는 대체 텍스트)
3. `python3 scripts/chunk_papers.py`
4. `python3 scripts/build_index.py`
5. `python3 main.py --query "Who is Harry Potter?" --k 3`
6. 출력/소스 참조 정상 확인

## 트러블슈팅
- `FAISS index not found`: 인덱스 빌드 먼저 실행
- `No module named ...`: `pip install -r requirements.txt` 재실행
- 모델 로딩이 느림: 데모에서는 warm-up 요청 1회 수행
