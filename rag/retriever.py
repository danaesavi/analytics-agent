# rag/retriever.py
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from rank_bm25 import BM25Okapi

_TOKEN = re.compile(r"[A-Za-z0-9_øæåØÆÅ]+", re.UNICODE)

def tokenize(s: str) -> List[str]:
    return [t.lower() for t in _TOKEN.findall(s)]

class RagRetriever:
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.corpus_tokens = [tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    @classmethod
    def load(cls, storage_dir: str = "rag_storage") -> "RagRetriever":
        p = Path(storage_dir) / "chunks.json"
        if not p.exists():
            raise FileNotFoundError("rag_storage/chunks.json not found. Run: python -m rag.build_index")
        chunks = json.loads(p.read_text(encoding="utf-8"))
        return cls(chunks)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        q_tokens = tokenize(query)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        out = []
        for idx, score in ranked:
            c = self.chunks[idx]
            out.append(
                {
                    "score": float(score),
                    "title": c.get("title"),
                    "source": c.get("source"),
                    "text": c.get("text"),
                }
            )
        return out