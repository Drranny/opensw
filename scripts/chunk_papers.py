"""
Backward-compatible entrypoint for text chunking.

This script preserves the original workflow documented in README/RAG_PIPELINE:
    python scripts/chunk_papers.py

Internally it delegates to scripts/chunk_dataset.py with mode=fixed.
"""

import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts", "chunk_dataset.py")


def main() -> int:
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--mode",
        "fixed",
        "--text-input-dir",
        "data/raw",
        "--output",
        "data/processed/chunks.json",
    ]

    print("[INFO] Running unified chunker in fixed mode for backward compatibility")
    return subprocess.call(cmd, cwd=BASE_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
