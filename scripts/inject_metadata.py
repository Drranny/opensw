"""
scripts/inject_metadata.py
Inject metadata headers into chunk text fields.

Usage:
    python scripts/inject_metadata.py \
      --input data/processed/chunks.json \
      --output data/processed/chunks_with_header.json
"""

import argparse
import json
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepend metadata headers to chunk text fields")
    parser.add_argument("--input", required=True, help="Input chunk JSON file path")
    parser.add_argument("--output", required=True, help="Output chunk JSON file path")
    return parser.parse_args()


def build_header(chunk: dict) -> str:
    parts: list[str] = []

    source_file = chunk.get("source_file")
    if source_file:
        parts.append(f"File: {source_file}")

    metadata = chunk.get("metadata") or {}

    # Code domain fields
    parent = metadata.get("parent")
    if parent:
        parts.append(f"parent: {parent}")

    node_type = metadata.get("node_type")
    if node_type:
        parts.append(f"node_type: {node_type}")

    # Text domain fields
    source = chunk.get("source")
    if source:
        parts.append(f"source: {source}")

    volume = chunk.get("volume")
    if volume is not None:
        parts.append(f"volume: {volume}")

    topic = chunk.get("topic")
    if topic:
        parts.append(f"topic: {topic}")

    series = chunk.get("series")
    if series:
        parts.append(f"series: {series}")

    if not parts:
        return ""

    return "[" + " | ".join(parts) + "]"


def main() -> None:
    args = parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        chunks: list[dict] = json.load(f)

    for chunk in chunks:
        header = build_header(chunk)
        if header:
            chunk["text"] = header + "\n" + chunk["text"]

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"[DONE] {len(chunks)} chunks written to {args.output}")


if __name__ == "__main__":
    main()
