"""RAG retrieval (AI-05): cari artikel cek fakta yang paling mirip dengan klaim.

Korpus dan embedding dibuat sekali oleh scripts/build_rag_index.py lalu disimpan
di app/data/rag/. Di sini hanya dimuat (sekali, saat pertama dipakai) dan dicari.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

DATA = Path(__file__).resolve().parent.parent / "data" / "rag"
KORPUS = DATA / "korpus.json"
EMBEDDINGS = DATA / "embeddings.npy"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
K = 3
# Uji 6 klaim (Oktober 2026): rujukan yang tepat berskor 0,73 sampai 0,80, sedangkan
# klaim tanpa padanan di korpus berskor tertinggi sekitar 0,46 sampai 0,69.
# ponytail: ambang dari 6 klaim saja; kalibrasi ulang dengan data uji yang lebih besar
AMBANG = 0.7
MAX_QUERY = 1000  # karakter; MiniLM hanya membaca sekitar 128 token pertama


@lru_cache(maxsize=1)
def _model():
    # Diimpor di sini supaya torch hanya dimuat saat RAG benar-benar dipakai
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL)


@lru_cache(maxsize=1)
def _indeks() -> tuple[list[dict], np.ndarray]:
    korpus = json.loads(KORPUS.read_text(encoding="utf-8"))
    emb = np.load(EMBEDDINGS).astype(np.float32)  # disimpan float16, sudah dinormalisasi
    if len(korpus) != len(emb):
        raise ValueError(f"Korpus {len(korpus)} entri, embedding {len(emb)} baris")
    return korpus, emb


def encode(teks: list[str]) -> np.ndarray:
    # Huruf kecil: model ini membedakan kapital, dan banyak judul Turnbackhoax
    # ditulis kapital semua sehingga tidak cocok dengan klaim berhuruf biasa.
    return _model().encode([t.lower() for t in teks],
                           normalize_embeddings=True, convert_to_numpy=True)


def retrieve(teks: str, k: int = K, ambang: float = AMBANG) -> list[dict]:
    """Kembalikan paling banyak k rujukan {judul, ringkasan, link, tanggal, skor}.

    Rujukan dengan skor di bawah ambang dibuang: lebih baik tanpa rujukan daripada
    rujukan yang tidak nyambung. Bila indeks atau model gagal dimuat, kembalikan []
    supaya penilaian tetap jalan tanpa rujukan.
    """
    try:
        korpus, emb = _indeks()
        q = encode([teks[:MAX_QUERY]])[0].astype(np.float32)
    except Exception:
        log.exception("RAG tidak tersedia, penilaian berjalan tanpa rujukan")
        return []
    skor = emb @ q  # cosine similarity karena semua vektor sudah dinormalisasi
    teratas = np.argsort(-skor)[:k]
    return [{**korpus[i], "skor": round(float(skor[i]), 4)}
            for i in teratas if skor[i] >= ambang]
