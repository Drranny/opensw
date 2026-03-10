# Structure-Aware Chunking 연구 2주 실행 계획

기준 문서: `route.pdf`  
기간: 2주 (14일)  
목표: 설계 수준에서 멈춘 연구를 실행 가능한 실험/결과 수준으로 완료

## 성공 기준 (2주 종료 시점)
- 텍스트/코드 도메인 모두에서 baseline 대비 구조 인식 청킹 실험 완료
- 핵심 지표 산출 완료: 
  - 1단계(검색): `HitRate@K`, `MRR`
  - 2단계(구조): `Boundary Truncation Ratio`, `Syntax Error Rate`, `Orphan Code Ratio`, `Executable Chunk Ratio`
  - 3단계(생성): RAGAS 기반 `Answer Relevance`, `Faithfulness`
- 재현 가능한 실험 스크립트 + 결과표/그래프 + 분석 노트 확보

## Week 1 (구현 + 실험 준비)

### Day 1: 실험 스펙 고정
- [ ] 실험 질문 3개 확정
  - [ ] Q1: 작은 chunk size에서 성능 저하를 구조 인식 청킹이 완화하는가?
  - [ ] Q2: 코드 도메인에서 구조 보존 지표가 유의미하게 개선되는가?
  - [ ] Q3: 동일 인덱스로 다중 태스크 재사용성이 올라가는가?
- [ ] baseline/제안 기법 정의 문서화
  - [ ] Baseline A: fixed-size
  - [ ] Baseline B: line-based (코드), token/문장 기반(텍스트)
  - [ ] Proposed: structure-aware
- [ ] 평가 지표 계산 규칙 고정
- 산출물: `RAG_PIPELINE.md` 내 실험 규칙 섹션 업데이트

### Day 2: 데이터셋 정제/분할
- [ ] 텍스트 데이터셋(Harry Potter) 학습/평가 분리 규칙 정의
- [ ] 코드 데이터셋(Legacy Python) 파일 단위 메타데이터 표준화
- [x] 평가용 질의셋 초안 작성 (텍스트 30+, 코드 30+ 권장)
- 산출물: `data/eval/queries_text.jsonl`, `data/eval/queries_code.jsonl`

### Day 3: Baseline chunker 구현
- [x] fixed-size chunker 파라미터화 (`size`, `overlap`)
- [x] line-based/token-based chunker 구현
- [x] chunk 메타데이터 공통 스키마 통일
- 산출물: baseline chunk 생성 스크립트 + 샘플 출력

### Day 4: Structure-aware chunker (텍스트)
- [x] 문단/챕터 경계 기반 청킹 구현
- [x] source/book/chapter metadata 보존
- [ ] 작은 chunk size 조건에서도 문맥 유지 정책 추가
- 산출물: 텍스트 구조 인식 chunk 결과

### Day 5: Structure-aware chunker (코드, AST)
- [x] Python `ast` 기반 class/function/control block 청킹
- [x] 부모 컨텍스트 메타데이터 주입
  - [x] 예: `Parent: Class X > def y`
- [x] orphan 코드 탐지 로직(초기 버전) 구현
- 산출물: 코드 구조 인식 chunk 결과

### Day 6: 인덱싱/검색 파이프라인 통합
- [x] Embedding 인덱스(FAISS) 빌드 자동화
- [x] BM25 인덱스 구성
- [x] RRF fusion 점수 계산 통합
- [x] chunking 방식별 동일 인터페이스로 검색 가능하게 정리
- 산출물: `scripts/run_index_and_retrieve.*` (형식은 프로젝트 표준 따름)

### Day 7: 스모크 테스트 + 수정
- [x] 샘플 질의로 end-to-end 동작 검증
- [x] 성능/오류 로그 수집
- [x] 깨지는 케이스(파싱 실패, 빈 청크, 메타데이터 누락) 수정
- 산출물: `results/smoke_report.md`

## Week 2 (본실험 + 분석 + 정리)

### Day 8: 본실험 1차 (텍스트 도메인)
- [ ] chunk size 조건 2~3개로 baseline/proposed 일괄 실행
- [ ] 1~3단계 평가지표 산출 (`HitRate@K`, `MRR`, `경계 절단율(Boundary Truncation Ratio)`, `RAGAS 지표`)
- [ ] 실패 질의 사례 수집
- 산출물: `results/text_metrics.csv`, 실패 사례 노트

### Day 9: 본실험 2차 (코드 도메인)
- [ ] 코드 질의셋으로 retrieval + 구조 지표 계산
- [ ] 1~3단계 평가지표 산출 (`Syntax Error Rate`, `Orphan Code Ratio`, `RAGAS 지표` 등)
- [ ] baseline/proposed 차이 로그 저장
- 산출물: `results/code_metrics.csv`

### Day 10: 재사용성 실험
- [ ] 동일 인덱스로 2개 이상 태스크 수행
  - [ ] 예: QA + 요약/문서화
- [ ] 태스크 전환 시 성능 유지/저하 기록
- 산출물: `results/reuse_metrics.md`

### Day 11: 어블레이션
- [ ] 메타데이터 제거/유지 비교
- [ ] RRF on/off 비교
- [ ] overlap/size 민감도 비교
- 산출물: `results/ablation.csv`

### Day 12: 결과 시각화
- [ ] 핵심 표 3개 작성 (텍스트/코드/재사용성)
- [ ] 핵심 그래프 2~4개 작성 (chunk size vs 성능 중심)
- [ ] figure 캡션 초안 작성
- 산출물: `results/figures/*`, `results/tables/*`

### Day 13: 해석 및 한계 정리
- [ ] 왜 개선되는지 구조적 근거 정리
- [ ] 실패 케이스 분류 (질의 유형/도메인/길이)
- [ ] 위협요인(데이터 편향, 질의셋 규모, 일반화 한계) 명시
- 산출물: `docs/analysis_notes.md`

### Day 14: 최종 패키징
- [ ] 재현 실행 순서 문서화 (`README` 또는 `RAG_PIPELINE.md` 갱신)
- [ ] 결과 요약 1페이지 작성
- [ ] 발표/논문용 핵심 기여 3~5줄 정제
- 산출물: 최종 요약본 + 재현 가이드

## 운영 규칙 (권장)
- 하루 시작: 당일 목표 3개만 고정
- 하루 종료: 지표/로그/실패 사례를 반드시 파일로 남김
- 실험 실행 시: 모든 run에 `timestamp`, `chunking_mode`, `chunk_size`, `overlap` 기록

## 즉시 실행 우선순위 (오늘)
1. [완료] `RAG_PIPELINE.md`에 실험 규칙 고정
2. [완료] 평가 질의셋 파일 뼈대 생성 (`data/eval/*.jsonl`)
3. [완료] baseline/proposed chunker 인터페이스 통일

## 완료 로그 (2026-02-15)
- [완료] `scripts/chunk_dataset.py` 추가: `fixed|line|token|structure_text|structure_code` 통합 인터페이스 구축
- [완료] `scripts/chunk_papers.py`를 통합 스크립트와 호환 유지하도록 정리
- [완료] 모드별 청크 생성:
  - `data/processed/chunks_fixed.json`
  - `data/processed/chunks_structure_text.json`
- [완료] 모드별 인덱스/메타데이터 생성:
  - `vector_db/faiss_fixed.index`
  - `vector_db/faiss_structure_text.index`
  - `data/processed/chunks_fixed_metadata.json`
  - `data/processed/chunks_structure_text_metadata.json`
- [완료] 평가 스크립트 추가: `scripts/eval_retrieval.py` (`HitRate@K`, `MRR`)
- [완료] 1차 텍스트 비교 결과 저장:
  - `results/text_fixed_metrics.json`
  - `results/text_structure_text_metrics.json`
- [완료] 의존성 정리:
  - `rank-bm25` 설치 및 `requirements.txt` 반영
  - `langchain-community` 설치 및 `requirements.txt` 반영
- [완료] EXAONE 로드 안정화:
  - `rag_pipeline/rag_chain.py`에 모델 `revision`/`code_revision` 고정
- [완료] 실쿼리 E2E 검증:
  - `python3 main.py --query "Who is Dudley?" --k 3` 검색/생성 진입 확인

## 완료 로그 (2026-03-08)
- [완료] `scripts/chunk_dataset.py` 업데이트: 
  - Python AST 기반 구조 인식 청킹(`structure_code`) 구현
  - 부모 컨텍스트(`parent`) 추적 및 고아 코드(`is_orphan`) 탐지 로직 추가
- [완료] `rag_pipeline/retriever.py` 개선: 
  - FAISS(Dense)와 BM25(Sparse) 검색 결과를 결합하는 RRF(Reciprocal Rank Fusion) 알고리즘 설계 및 통합
- [완료] 하이브리드 검색 파이프라인 연동:
  - `scripts/search_with_metadata.py`에 BM25 인덱스 로드 및 RRF 검색 적용
  - `scripts/eval_retrieval.py` 평가 스크립트에 하이브리드 `retrieve` 인터페이스 적용 완료
- [완료] 구조적 메타데이터 직렬화(Serialization) 파이프라인 구축: 
  - `scripts/inject_metadata.py` 추가 (검색 엔진이 구조를 인식할 수 있도록 청크 텍스트 맨 앞에 메타데이터 헤더 결합)
  - Data Injection -> Re-indexing -> Evaluation으로 이어지는 3단계 파이프라인 확립
- [완료] 구조 인식 검색 E2E 스모크 테스트:
  - 텍스트/코드 도메인 하이브리드 검색 실행 및 로직 검증 완료