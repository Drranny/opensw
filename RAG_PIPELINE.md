

# RAG 파이프라인 실행 및 관리 가이드 (해리포터 전집 버전)

본 문서는 **해리포터 소설 전집(1-7권)** 및 관련 설정 데이터를 기반으로 구축된 로컬 RAG 시스템의 실행 절차를 기술합니다.

## 1. 파이프라인 개요

* **데이터 준비**: `data/raw` 경로에 해리포터 1~7권 원문(`Book1.txt` ~ `Book7.txt`) 및 추가 설정 데이터 배치
* **전처리**: `scripts/chunk_papers.py`를 통해 전 권의 텍스트를 분할하고 권수(Volume)별 메타데이터 추출
* **색인**: `scripts/build_index.py`를 통해 1.8만 개의 청크를 FAISS 벡터 인덱스로 구축
* **추론**: `main.py`를 통해 전 시리즈를 넘나드는 통합 검색 및 EXAONE 3.5 기반 답변 생성

---

## 2. 단계별 실행 상세

### 2.1 데이터 전처리 및 청킹

해리포터 1~7권 전집과 리뷰, 주문 목록 등 모든 데이터를 분석 단위로 분할합니다. 특히 각 청크가 몇 권에서 나왔는지(`volume`)를 태깅하여 정밀한 검색이 가능하도록 합니다.

```bash
python3 scripts/chunk_papers.py

```

* **대상 데이터**: `Book1.txt` ~ `Book7.txt`, `hp_spells_list.txt` 등
* **결과**: 18,351개의 지능형 청크 및 메타데이터 생성

### 2.2 벡터 인덱스 구축

분할된 전집 데이터를 임베딩하여 FAISS 인덱스를 생성합니다.

```bash
python3 scripts/build_index.py

```

* **생성 파일**: `vector_db/faiss.index`

### 2.3 시스템 실행 및 질의

전 시리즈를 대상으로 질문하거나, 특정 권수(Volume)만 필터링하여 질문할 수 있습니다.

**메타데이터 필터링 예시:**

```bash
# 7권(죽음의 성물) 내용만 집중적으로 참조하여 질문
python3 main.py --query "해리와 볼드모트의 마지막 결전은 어땠어?" --filter '{"source": "book", "volume": 7}'

# 전체 시리즈에서 특정 마법 주문 정보만 검색
python3 main.py --query "익스펠리아무스 주문의 기원" --filter '{"source": "lore", "topic": "spells"}'

```

---

## 3. 시스템 사양 및 지표

### 하이퍼파라미터 및 모델 정보

* **데이터 규모**: 해리포터 소설 1~7권 전집 포함 총 18,351개 청크
* **Generation Model**: LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct
* **Vector Engine**: FAISS (ANN Search)

### 주요 성능 모니터링 지표

* **Retrieval Latency**: 전 시리즈 데이터(1.8만 개) 중 관련 근거를 찾는 시간 (0.01초 미만)
* **Inference Latency**: EXAONE 모델이 답변을 생성하는 시간
* **Throughput**: 초당 토큰 생성 속도

---

## 4. 유지보수 및 업데이트

새로운 설정 자료나 외전 데이터를 추가할 경우, `data/raw`에 파일을 넣고 아래 과정을 재실행합니다.

```bash
python3 scripts/chunk_papers.py  # 청킹 재실행
python3 scripts/build_index.py   # 인덱스 재빌드

```
