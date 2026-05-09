from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from . import config


_encoder: SentenceTransformer | None = None
_chunks: list[str] = []
_embeddings: np.ndarray | None = None


def _split(text: str, size: int, overlap: int) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paragraphs:
        if len(buf) + len(p) + 2 <= size:
            buf = f"{buf}\n\n{p}".strip()
            continue
        if buf:
            chunks.append(buf)
        if len(p) <= size:
            buf = p
        else:
            for i in range(0, len(p), size - overlap):
                chunks.append(p[i : i + size])
            buf = ""
    if buf:
        chunks.append(buf)
    return chunks


def load() -> None:
    global _encoder, _chunks, _embeddings
    _encoder = SentenceTransformer(config.EMBED_MODEL)
    text = config.CORPUS_PATH.read_text(encoding="utf-8")
    _chunks = _split(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    if config.EMBEDDINGS_CACHE.exists():
        cached = np.load(config.EMBEDDINGS_CACHE, allow_pickle=True)
        if int(cached["count"]) == len(_chunks):
            _embeddings = cached["matrix"]
            _encoder.encode(["warmup"], normalize_embeddings=True)
            return

    _embeddings = _encoder.encode(
        _chunks, normalize_embeddings=True, show_progress_bar=False
    )
    np.savez(config.EMBEDDINGS_CACHE, matrix=_embeddings, count=len(_chunks))


def retrieve(query: str, k: int = config.TOP_K) -> tuple[list[str], float]:
    if _encoder is None or _embeddings is None:
        raise RuntimeError("rag.load() must be called before retrieve()")
    q = _encoder.encode([query], normalize_embeddings=True)[0]
    scores = _embeddings @ q
    top = np.argsort(-scores)[:k]
    return [_chunks[i] for i in top], float(scores[top[0]])
