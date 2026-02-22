# rag/build_index.py
from __future__ import annotations
import json
from pathlib import Path

def chunk_markdown(text: str) -> list[dict]:
    """
    Chunk by headings (## ...) so each metric definition becomes a chunk.
    """
    lines = text.splitlines()
    chunks = []
    current_title = None
    current = []

    for line in lines:
        if line.startswith("## "):
            if current_title and current:
                chunks.append({"title": current_title, "text": "\n".join(current).strip()})
            current_title = line.replace("## ", "").strip()
            current = [line]
        else:
            if current_title is not None:
                current.append(line)

    if current_title and current:
        chunks.append({"title": current_title, "text": "\n".join(current).strip()})

    return chunks

def main():
    docs_dir = Path("docs")
    out_dir = Path("rag_storage")
    out_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    for p in sorted(docs_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        # For schema.md, chunking by headings is fine too; for now use same
        chunks = chunk_markdown(text)
        for c in chunks:
            c["source"] = p.name
        all_chunks.extend(chunks)

    (out_dir / "chunks.json").write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"Wrote {len(all_chunks)} chunks to rag_storage/chunks.json")

if __name__ == "__main__":
    main()