import argparse
import ast
import json
import os
import re
import sys
from typing import Dict, List

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


TEXT_FILE_EXTENSIONS = {".txt", ".md"}
CODE_FILE_EXTENSIONS = {".py"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified dataset chunker")
    parser.add_argument(
        "--mode",
        choices=["fixed", "line", "token", "structure_text", "structure_code"],
        default="fixed",
        help="Chunking mode",
    )
    parser.add_argument(
        "--text-input-dir",
        default="data/raw",
        help="Directory for text dataset files",
    )
    parser.add_argument(
        "--code-input-dir",
        default="data/raw_code",
        help="Directory for code dataset files (optional)",
    )
    parser.add_argument(
        "--output",
        default="data/processed/chunks.json",
        help="Output path for chunk list JSON",
    )
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP)
    return parser.parse_args()


def read_files(input_dir: str, extensions: set[str]) -> List[str]:
    if not os.path.exists(input_dir):
        return []

    files: List[str] = []
    for root, _, names in os.walk(input_dir):
        for name in names:
            ext = os.path.splitext(name)[1].lower()
            if ext in extensions:
                files.append(os.path.join(root, name))
    return sorted(files)


def extract_text_metadata(fname: str, text: str) -> Dict:
    metadata = {"source_file": fname}

    if fname.startswith("Book") and fname.endswith(".txt"):
        m = re.search(r"Book(\d+)", fname)
        if m:
            metadata.update(
                {
                    "source": "book",
                    "series": "harry_potter",
                    "volume": int(m.group(1)),
                }
            )
        return metadata

    if fname == "hp_spells_list.txt":
        metadata.update({"source": "lore", "topic": "spells"})
        return metadata

    if fname.startswith("harrypotter1_"):
        text_lower = text.lower()
        if any(
            keyword in text_lower
            for keyword in [
                "review",
                "blu-ray",
                "film",
                "movie",
                "cinema",
                "director",
                "actor",
                "performance",
                "screenplay",
            ]
        ):
            review_type = "critic"
            if any(
                keyword in text_lower
                for keyword in ["audience", "viewer", "fan", "rating", "imdb"]
            ):
                review_type = "audience"
            metadata.update(
                {
                    "source": "review",
                    "movie": "harry_potter_1",
                    "type": review_type,
                }
            )
            return metadata

        if any(
            keyword in text_lower
            for keyword in [
                "character",
                "protagonist",
                "harry potter",
                "dumbledore",
                "voldemort",
                "hermione",
                "ron weasley",
            ]
        ):
            metadata.update({"source": "lore", "topic": "character"})
            return metadata

        if any(
            keyword in text_lower
            for keyword in [
                "overview",
                "series",
                "novels",
                "author",
                "j. k. rowling",
                "themes",
            ]
        ):
            metadata.update({"source": "lore", "topic": "overview"})
            return metadata

        if any(
            keyword in text_lower
            for keyword in ["magic", "spell", "wand", "wizard", "wizarding world"]
        ):
            metadata.update({"source": "lore", "topic": "magic"})
            return metadata

    metadata.update({"source": "unknown", "topic": "unknown"})
    return metadata


def split_fixed(text: str, chunk_size: int, overlap: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)


def split_line(text: str, chunk_size: int, overlap: int) -> List[str]:
    lines = text.splitlines()
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for line in lines:
        line_len = len(line) + 1
        if current and current_len + line_len > chunk_size:
            chunks.append("\n".join(current))
            if overlap > 0:
                carry = "\n".join(current)
                carry = carry[-overlap:]
                current = [carry] if carry else []
                current_len = len(carry)
            else:
                current = []
                current_len = 0
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))
    return [c for c in chunks if c.strip()]


def split_token(text: str, chunk_size: int, overlap: int) -> List[str]:
    tokens = text.split()
    if not tokens:
        return []

    chunks: List[str] = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i : i + chunk_size]
        if not chunk_tokens:
            continue
        chunks.append(" ".join(chunk_tokens))
        if i + chunk_size >= len(tokens):
            break
    return chunks


def split_structure_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    # Keep chapter-like blocks first, then paragraph level.
    chapter_blocks = re.split(r"\n\s*(CHAPTER\s+[A-Z0-9]+.*)\n", text, flags=re.IGNORECASE)

    blocks: List[str] = []
    if len(chapter_blocks) <= 1:
        blocks = [text]
    else:
        i = 1
        while i < len(chapter_blocks):
            title = chapter_blocks[i].strip()
            body = chapter_blocks[i + 1] if i + 1 < len(chapter_blocks) else ""
            blocks.append(f"{title}\n{body}".strip())
            i += 2

    chunks: List[str] = []
    for block in blocks:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
        for para in paragraphs:
            if len(para) <= chunk_size:
                chunks.append(para)
            else:
                chunks.extend(split_fixed(para, chunk_size, overlap))

    return [c for c in chunks if c.strip()]


def _iter_ast_chunks(tree: ast.AST, source: str) -> List[Dict]:
    chunks: List[Dict] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.If, ast.For, ast.While, ast.Try, ast.With)):
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            if not start or not end:
                continue
            lines = source.splitlines()
            snippet = "\n".join(lines[start - 1 : end]).strip()
            if not snippet:
                continue

            parent = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent = f"function:{node.name}"
            elif isinstance(node, ast.ClassDef):
                parent = f"class:{node.name}"
            else:
                parent = node.__class__.__name__.lower()

            chunks.append(
                {
                    "text": snippet,
                    "metadata": {
                        "node_type": node.__class__.__name__,
                        "start_line": start,
                        "end_line": end,
                        "parent": parent,
                    },
                }
            )
    return chunks


def split_structure_code(text: str) -> List[Dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return _iter_ast_chunks(tree, text)


def chunk_text_file(path: str, mode: str, chunk_size: int, overlap: int) -> List[Dict]:
    fname = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    base_meta = extract_text_metadata(fname, text)

    if mode == "fixed":
        pieces = split_fixed(text, chunk_size, overlap)
    elif mode == "line":
        pieces = split_line(text, chunk_size, overlap)
    elif mode == "token":
        pieces = split_token(text, chunk_size, overlap)
    elif mode == "structure_text":
        pieces = split_structure_text(text, chunk_size, overlap)
    else:
        return []

    rows: List[Dict] = []
    for i, piece in enumerate(pieces):
        rows.append(
            {
                "chunk_id": i,
                "text": piece,
                "source_file": fname,
                **base_meta,
                "chunk_mode": mode,
                "chunk_size": chunk_size,
                "chunk_overlap": overlap,
                "metadata": {},
            }
        )
    return rows


def chunk_code_file(path: str, mode: str, chunk_size: int, overlap: int) -> List[Dict]:
    fname = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    rows: List[Dict] = []

    if mode == "fixed":
        pieces = split_fixed(text, chunk_size, overlap)
        for i, piece in enumerate(pieces):
            rows.append(
                {
                    "chunk_id": i,
                    "text": piece,
                    "source_file": fname,
                    "source": "code",
                    "chunk_mode": mode,
                    "chunk_size": chunk_size,
                    "chunk_overlap": overlap,
                    "metadata": {},
                }
            )
        return rows

    if mode == "line":
        pieces = split_line(text, chunk_size, overlap)
        for i, piece in enumerate(pieces):
            rows.append(
                {
                    "chunk_id": i,
                    "text": piece,
                    "source_file": fname,
                    "source": "code",
                    "chunk_mode": mode,
                    "chunk_size": chunk_size,
                    "chunk_overlap": overlap,
                    "metadata": {},
                }
            )
        return rows

    if mode == "token":
        pieces = split_token(text, chunk_size, overlap)
        for i, piece in enumerate(pieces):
            rows.append(
                {
                    "chunk_id": i,
                    "text": piece,
                    "source_file": fname,
                    "source": "code",
                    "chunk_mode": mode,
                    "chunk_size": chunk_size,
                    "chunk_overlap": overlap,
                    "metadata": {},
                }
            )
        return rows

    if mode == "structure_code":
        structured = split_structure_code(text)
        for i, obj in enumerate(structured):
            rows.append(
                {
                    "chunk_id": i,
                    "text": obj["text"],
                    "source_file": fname,
                    "source": "code",
                    "chunk_mode": mode,
                    "chunk_size": chunk_size,
                    "chunk_overlap": overlap,
                    "metadata": obj.get("metadata", {}),
                }
            )
        return rows

    return rows


def main() -> None:
    args = parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    text_files = read_files(args.text_input_dir, TEXT_FILE_EXTENSIONS)
    code_files = read_files(args.code_input_dir, CODE_FILE_EXTENSIONS)

    all_chunks: List[Dict] = []

    # Text modes operate on text dataset.
    if args.mode in {"fixed", "line", "token", "structure_text"}:
        for path in text_files:
            rows = chunk_text_file(path, args.mode, args.chunk_size, args.overlap)
            all_chunks.extend(rows)
            print(f"[TEXT] {os.path.basename(path)}: {len(rows)} chunks")

    # Code mode operates on code dataset, but does not fail if dataset is missing.
    if args.mode == "structure_code":
        if not code_files:
            print(f"[WARN] No code files found in {args.code_input_dir}. Writing empty output.")
        for path in code_files:
            rows = chunk_code_file(path, args.mode, args.chunk_size, args.overlap)
            all_chunks.extend(rows)
            print(f"[CODE] {os.path.basename(path)}: {len(rows)} chunks")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"[DONE] mode={args.mode}, chunks={len(all_chunks)}, output={args.output}")


if __name__ == "__main__":
    main()
