RAG 파이프라인 실행 및 관리 가이드
본 문서는 해리포터 데이터 기반 RAG 시스템의 전체 파이프라인 구축 및 실행 절차를 기술합니다.

1. 파이프라인 개요
데이터 준비: data/raw 경로에 소스 텍스트 파일 배치

전처리: scripts/chunk_papers.py를 통한 텍스트 분할 및 메타데이터 추출

색인: scripts/build_index.py를 통한 FAISS 벡터 인덱스 구축

추론: main.py를 통한 검색 및 로컬 LLM(EXAONE 3.5) 답변 생성

2. 단계별 실행 상세
2.1 데이터 전처리 및 청킹
원본 텍스트를 분석 가능한 단위로 분할하고 소스 파일명, 도서 권수 등의 메타데이터를 태깅합니다.

Bash

python3 scripts/chunk_papers.py
생성 파일: data/processed/chunks_metadata.json

2.2 벡터 인덱스 구축
분할된 텍스트를 임베딩하여 벡터 공간에 투영하고 FAISS 인덱스를 생성합니다.

Bash

python3 scripts/build_index.py
생성 파일: vector_db/faiss.index

2.3 시스템 실행 및 질의
로컬 CPU 자원을 활용하여 질의응답을 수행합니다.

기본 실행:

Bash

python3 main.py --query "질문 내용"
메타데이터 필터링 적용 (JSON 포맷):

Bash

# 특정 도서(1권) 데이터만 참조
python3 main.py --query "질문" --filter '{"source": "book", "volume": 1}'

# 특정 주제(주문) 데이터만 참조
python3 main.py --query "질문" --filter '{"source": "lore", "topic": "spells"}'
3. 시스템 사양 및 지표
하이퍼파라미터 및 모델 정보
Generation Model: LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct

Vector Engine: FAISS (ANN Search)

Top-K: 기본 3개 청크 참조

주요 성능 모니터링 지표 (DEBUG Log)
시스템 실행 시 터미널을 통해 실시간으로 다음 지표를 리포트합니다.

Retrieval Latency: 벡터 DB 검색 소요 시간

Inference Latency: LLM 응답 생성 시간

Throughput: 초당 토큰 생성 수 (tokens/s)

Token Count: 입력 프롬프트 및 출력 답변의 토큰 규모

4. 유지보수 및 업데이트 (Full Re-build)
신규 데이터를 추가하거나 파라미터를 수정한 경우 아래 순서로 재구축을 수행합니다.

Bash

# 1. 기존 캐시 및 인덱스 초기화 후 전처리
python3 scripts/chunk_papers.py

# 2. 벡터 인덱스 재빌드
python3 scripts/build_index.py

# 3. 시스템 작동 확인
python3 main.py
5. 프로젝트 디렉토리 구조
Plaintext

rag/
├── data/
│   ├── raw/                    # 소스 데이터 (TXT)
│   └── processed/              # 전처리된 JSON 데이터
├── scripts/
│   ├── chunk_papers.py         # 텍스트 전처리 스크립트
│   └── build_index.py          # 벡터 DB 구축 스크립트
├── vector_db/                  # FAISS Index 저장 경로
├── rag_pipeline/               # 핵심 모듈 (Retriever, Prompt, Chain)
├── config.py                   # 시스템 설정
└── main.py                     # 통합 실행 엔트리포인트