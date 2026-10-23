"""Bangun korpus dan indeks embedding RAG (AI-05) dari dataset Turnbackhoax.

Sumber: Dataset/raw/dataset_turnbackhoax_10_cleaned.xlsx (Kaggle "Indonesian Fact
and Hoax Political News", ada di branch ragil). Isinya artikel cek fakta asli dari
turnbackhoax.id, jadi korpus berisi hoax yang benar-benar pernah beredar.

Jalankan dari folder hoaxscan-backend (butuh pandas dan openpyxl):
    python -m scripts.build_rag_index PATH_KE_XLSX
Hasil: app/data/rag/korpus.json dan app/data/rag/embeddings.npy
"""
import json
import re
import sys
import time

import numpy as np

MAX_RINGKASAN = 400


def judul_bersih(judul: str) -> str:
    """Buang label di depan judul, misalnya "[SALAH] "."""
    return re.sub(r"^\s*\[[^\]]*\]\s*", "", str(judul)).strip()


def ringkas(fullteks: str) -> str:
    """Ambil paragraf 'Faktanya, ...' dari hasil periksa fakta Turnbackhoax."""
    t = re.sub(r"^\s*Hasil Periksa Fakta[^\n]*\n", "", str(fullteks))
    t = t.split("=====")[0].replace("Selengkapnya ada di penjelasan.", "")
    t = " ".join(t.split())
    if not t:  # format lama tanpa ringkasan di awal: pakai bagian penjelasan
        m = re.search(r"\[PENJELASAN\]:?\s*(.+)", str(fullteks), re.S)
        t = " ".join(m.group(1).split()) if m else ""
    return t[:MAX_RINGKASAN]


def teks_embedding(judul: str) -> str:
    """Teks yang di-encode: judul tanpa label saja.

    Uji Oktober 2026: menambahkan narasi hoaks justru menurunkan ketepatan,
    karena narasi sering berisi ejekan tanpa menyebut nama atau peristiwa.
    """
    return judul_bersih(judul)


def main(path_xlsx: str) -> None:
    import pandas as pd

    from app.services import rag

    df = pd.read_excel(path_xlsx).drop_duplicates(subset="Url")
    korpus, teks = [], []
    for _, r in df.iterrows():
        ringkasan = ringkas(r["FullText"])
        if not ringkasan:
            continue
        korpus.append({
            "judul": str(r["Title"]).strip(),
            "ringkasan": ringkasan,
            "link": str(r["Url"]).strip(),
            "tanggal": str(r["Timestamp"]).strip(),
        })
        teks.append(teks_embedding(r["Title"]))
    print(f"{len(korpus)} entri dari {len(df)} baris, encode dimulai...")

    mulai = time.time()
    emb = rag.encode(teks)
    print(f"Encode selesai dalam {time.time() - mulai:.0f} detik, dimensi {emb.shape}")

    rag.DATA.mkdir(parents=True, exist_ok=True)
    rag.KORPUS.write_text(json.dumps(korpus, ensure_ascii=False), encoding="utf-8")
    np.save(rag.EMBEDDINGS, emb.astype(np.float16))  # float16: separuh ukuran, akurasi cukup
    print(f"Tersimpan: {rag.KORPUS} dan {rag.EMBEDDINGS}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
