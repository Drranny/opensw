# WIS2026 박람회용 코드 인수인계 가이드

## 1) 이 저장소에 올릴 것
- Python 소스코드: `main.py`, `config.py`, `ingest/`, `rag_pipeline/`, `scripts/`, `vector_db/*.py`
- 실행 의존성: `requirements.txt`
- 최소 문서: `README.md`, `RAG_PIPELINE.md`, 본 문서
- 평가용 소형 질의셋: `data/eval/*.jsonl`

## 2) 이 저장소에 올리지 않을 것
- 대용량/재생성 가능 산출물
	- `vector_db/*.index`
	- `data/processed/*.json`
	- `results/`
- 원문/저작권 이슈 가능 데이터
	- 박람회 저장소(`WIS2026`)는 데모 편의를 위해 `data/raw/`, `data/raw_code/`를 포함 가능
	- 공개 전환 시에는 라이선스/저작권 검토 후 제외 권장
- 로컬 환경/캐시
	- `__pycache__/`, `.venv*`, `.env`, `.vscode/`
- 연구 참고 문서 원본
	- `route.pdf`

## 3) 기존 추적 파일 정리(로컬 파일은 유지)
아래 명령은 Git 추적만 해제합니다.

```bash
git rm -r --cached results || true
git rm -r --cached data/processed || true
git rm --cached vector_db/*.index || true
git rm --cached route.pdf || true
```

## 4) 새 저장소(WIS2026)로 푸시
```bash
git remote set-url origin https://github.com/Drranny/WIS2026.git
git add .
git commit -m "chore: prepare expo handoff (ignore rules + onboarding docs)"
git push -u origin main
```

## 5) 수신 팀용 실행 최소 절차
```bash
pip install -r requirements.txt
python3 scripts/chunk_papers.py
python3 scripts/build_index.py
python3 main.py --query "Who is Dudley?" --k 3
```

## 6) 팟 분리 전제(박람회)
- `rag-api` 팟: retrieval + prompt build
- `rag-llm` 팟: EXAONE 추론 전용
- 데이터/인덱스는 이미지 번들 또는 PVC 마운트 방식으로 운영
