# 학부생 팀 온보딩 가이드 (쿠버네티스 없이 웹 연동)

이 문서는 **처음 합류한 팀원**이 이 프로젝트를 빠르게 이해하고,
로컬에서 실행한 뒤 프론트엔드와 연결할 수 있도록 작성했습니다.

---

## 1. 이 프로젝트가 하는 일

사용자가 질문하면,
1) 관련 문서 조각(chunk)을 검색하고
2) 검색된 근거를 바탕으로
3) LLM이 답변을 생성하는 구조입니다.

즉, **검색(Retrieval) + 생성(Generation)**을 결합한 RAG 시스템입니다.

---

## 2. 전체 실행 흐름(매우 중요)

질문 1개가 처리되는 순서:

1. `main.py`가 실행됨
2. `data/processed/chunks_*.json`에서 청크를 로드
3. `vector_db/*.index`에서 FAISS 인덱스 로드
4. `HybridRetriever`가 BM25 + 벡터 검색 결과를 합침(RRF)
5. 상위 문서 조각들을 `prompt.py`에서 프롬프트로 구성
6. `rag_chain.py`가 EXAONE 모델로 답변 생성
7. 최종 답변 + 출처(source) 출력

핵심: **검색 품질**이 답변 품질을 크게 좌우합니다.

---

## 3. 폴더별 역할

- `main.py`
  - CLI 진입점
  - 검색 + 생성 파이프라인을 순서대로 호출

- `config.py`
  - 청크 크기, 오버랩, 인덱스 경로 같은 고정 설정값

- `ingest/`
  - 데이터 로딩/분할 관련 코드
  - 원문 텍스트를 청크로 만드는 전처리 로직

- `scripts/`
  - 실제 실행용 스크립트 모음
  - 예: 청킹, 인덱스 생성, 평가

- `rag_pipeline/retriever.py`
  - 기본 검색기 로직(벡터 검색 중심)

- `rag_pipeline/hybrid_retriever.py`
  - BM25 + FAISS 결과를 결합하는 핵심 로직
  - RRF(Recriprocal Rank Fusion) 기반 정렬

- `rag_pipeline/prompt.py`
  - 검색된 컨텍스트 + 사용자 질문을 프롬프트 문자열로 조합

- `rag_pipeline/rag_chain.py`
  - EXAONE 모델 로드 및 텍스트 생성

- `data/`
  - `raw/`: 원본 텍스트
  - `processed/`: 청크 JSON
  - `eval/`: 평가 질의셋

- `vector_db/`
  - FAISS 인덱스 저장 위치

---

## 4. 로컬 실행 순서(초기 세팅)

```bash
pip install -r requirements.txt
python3 scripts/chunk_papers.py
python3 scripts/build_index.py
python3 main.py --query "Who is Dudley?" --k 3
```

성공 기준:
- 콘솔에 검색된 source preview가 출력됨
- 마지막에 답변 박스가 출력됨

---

## 5. 자주 막히는 포인트

1) `FAISS index not found`
- 인덱스 생성 전이라서 발생
- `python3 scripts/build_index.py` 먼저 실행

2) `No module named ...`
- 패키지 설치 누락
- `pip install -r requirements.txt`

3) 모델 로딩이 너무 느림
- 첫 실행은 다운로드/로딩으로 느릴 수 있음
- 데모 전 warm-up 질문 1개 미리 실행 권장

---

## 6. 프론트엔드 연결 방법(쿠버네티스 없이)

현재는 `main.py` CLI 구조이므로,
웹 연동을 위해서는 **백엔드 API 레이어**를 1개 추가하면 됩니다.

권장 최소 구조:

- 백엔드: FastAPI
- 엔드포인트: `POST /ask`
- 입력: `{ "query": "...", "k": 3 }`
- 출력: `{ "answer": "...", "sources": [...] }`

내부에서는 기존 함수 재사용:
- 검색: `HybridRetriever.invoke(...)`
- 프롬프트: `build_prompt(...)`
- 생성: `rag_answer(...)`

즉, 새로 모델 파이프라인을 만들지 말고 **기존 모듈을 감싸는 방식**으로 구현합니다.

---

## 7. 팀 개발 역할 분담 예시

- A: 데이터/청킹 파이프라인 담당 (`scripts/`, `ingest/`)
- B: 검색 품질 담당 (`hybrid_retriever.py` 튜닝)
- C: 프롬프트/답변 품질 담당 (`prompt.py`, 생성 파라미터)
- D: 웹 백엔드 + 프론트 연결 담당 (FastAPI + UI)

---

## 8. 최소 코드 읽기 순서(입문자 추천)

1. `main.py`
2. `rag_pipeline/hybrid_retriever.py`
3. `rag_pipeline/prompt.py`
4. `rag_pipeline/rag_chain.py`
5. `scripts/build_index.py`

이 순서로 보면 “질문이 들어와서 답변이 나갈 때 어떤 코드가 실행되는지”가 한 번에 이해됩니다.

---

## 9. 과목용 운영 규칙

- 먼저 동작하게 만들고(작동 우선), 그 다음 성능 개선
- 파이프라인 핵심 로직은 유지하고 API 레이어만 얇게 추가
- 실험 결과 파일(`results/`)은 필요 시에만 커밋
- 팀원이 이해할 수 있는 수준으로 함수/모듈 설명 문서 함께 유지

---

## 10. 다음 단계 체크리스트

- [ ] 로컬에서 `main.py` 질의 성공
- [ ] FastAPI `POST /ask` 동작
- [ ] 프론트에서 질문/답변 표시
- [ ] source(출처) 함께 렌더링
- [ ] 에러 메시지 처리(빈 질문, 타임아웃 등)
