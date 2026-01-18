Vector DB 기반 RAG 시스템 구축 및 실습
본 프로젝트는 고성능 벡터 검색 엔진인 FAISS와 한국어/영어 능력이 검증된 EXAONE 3.5 모델을 결합하여, 방대한 도서 데이터를 실시간으로 참조하는 RAG(Retrieval-Augmented Generation) 파이프라인 구성을 목적으로 합니다.

기술 스택 (Technical Stack)
Language Model: LGAI-EXAONE-3.5-2.4B-Instruct (Local Inference)

Vector Database: FAISS (Facebook AI Similarity Search)

Data Infrastructure: Wikipedia API, Kaggle Harry Potter Corpus

Computing Resource: 16-Core CPU / 30GiB RAM (Local Cluster)

시스템 파이프라인 (The Pipeline)
Document Loading: 해리포터 시리즈 원문 및 설정 데이터 로드

Preprocessing & Chunking: 문맥 보존을 위한 텍스트 분할 (총 18,351개 청크 생성)

Vector Embedding: 텍스트 데이터의 고차원 수치 벡터 변환

Vector DB Indexing: FAISS를 활용한 벡터 데이터 색인 및 지식 베이스 구축

Similarity Retrieval: 질문 벡터와 지식 베이스 간 유사도 계산 및 상위 K개 근거 추출

Local LLM Generation: 추출된 영문 근거를 기반으로 EXAONE 3.5가 한국어 답변 생성

핵심 작동 원리 (Core Mechanics)
1. FAISS를 활용한 벡터 검색 엔진
단순 키워드 매칭 방식의 한계를 극복하기 위해 ANN(Approximate Nearest Neighbor) 알고리즘 기반의 벡터 검색을 수행합니다. 고차원 공간에서 질문과 가장 가까운 거리에 위치한 데이터 청크를 밀리초(ms) 단위로 탐색하여 응답 지연을 최소화했습니다.

2. Cross-Lingual 정보 처리
임베딩 공간의 언어 중립적 특성을 활용하여 사용자의 한국어 질의를 영문 지식 베이스와 매칭합니다. 이후 모델의 다국어 추론 능력을 통해 영문 텍스트를 한국어로 요약 및 변환하여 최종 결과를 도출하는 교차 언어 파이프라인을 구현했습니다.

3. 로컬 서버 최적화 (CPU Inference)
GPU가 제한된 환경에서 16코어 CPU의 병렬 연산 성능을 극대화하기 위해 bfloat16 데이터 타입을 적용하고 가벼운 2.4B 파라미터 모델을 선택하여 안정적인 추론 속도(Throughput)를 확보했습니다.

성능 지표 (Performance Metrics)
Data Scale: 18,351 Chunks

Search Latency: < 0.01 seconds (via FAISS)

Generation Speed: ~25-45 tokens/sec (CPU-based)