import numpy as np

from app.services import rag
from scripts import build_rag_index as build

KORPUS = [
    {"judul": "[SALAH] A", "ringkasan": "ra", "link": "https://t.id/a", "tanggal": "1"},
    {"judul": "[SALAH] B", "ringkasan": "rb", "link": "https://t.id/b", "tanggal": "2"},
    {"judul": "[SALAH] C", "ringkasan": "rc", "link": "https://t.id/c", "tanggal": "3"},
    {"judul": "[SALAH] D", "ringkasan": "rd", "link": "https://t.id/d", "tanggal": "4"},
]
# Vektor satuan; query [1, 0] punya cosine 1.0, 0.8, 0.6, 0.0 terhadap A, B, C, D
EMB = np.array([[1.0, 0.0], [0.8, 0.6], [0.6, 0.8], [0.0, 1.0]], dtype=np.float32)


def _pasang(monkeypatch, query=(1.0, 0.0)):
    monkeypatch.setattr(rag, "_indeks", lambda: (KORPUS, EMB))
    monkeypatch.setattr(rag, "encode", lambda teks: np.array([query], dtype=np.float32))


def test_tiga_teratas_urut_skor(monkeypatch):
    _pasang(monkeypatch)
    hasil = rag.retrieve("klaim", ambang=0.0)
    assert [h["link"] for h in hasil] == ["https://t.id/a", "https://t.id/b", "https://t.id/c"]
    assert hasil[0]["skor"] == 1.0


def test_di_bawah_ambang_dibuang(monkeypatch):
    _pasang(monkeypatch)
    hasil = rag.retrieve("klaim", ambang=0.7)
    assert [h["link"] for h in hasil] == ["https://t.id/a", "https://t.id/b"]


def test_tidak_ada_yang_mirip(monkeypatch):
    _pasang(monkeypatch, query=(-1.0, 0.0))
    assert rag.retrieve("klaim lain") == []


def test_indeks_hilang_tidak_crash(monkeypatch):
    def gagal():
        raise FileNotFoundError("korpus.json")

    monkeypatch.setattr(rag, "_indeks", gagal)
    assert rag.retrieve("klaim") == []


def test_judul_bersih():
    assert build.judul_bersih("[SALAH] Anies Dekat Aliran Sesat") == "Anies Dekat Aliran Sesat"
    assert build.judul_bersih("Tanpa Label") == "Tanpa Label"


def test_ringkas_ambil_paragraf_faktanya():
    full = ("Hasil Periksa Fakta Gabriela (USU)\nFaktanya, foto itu diedit.\n"
            "Selengkapnya ada di penjelasan.\n=====\n[KATEGORI]: X")
    assert build.ringkas(full) == "Faktanya, foto itu diedit."


def test_ringkas_format_lama_pakai_penjelasan():
    full = "=====\n[NARASI]: x\n=====\n[PENJELASAN]:\nVideo itu lama.\n"
    assert build.ringkas(full) == "Video itu lama."


def test_teks_embedding_judul_tanpa_label():
    assert build.teks_embedding("[SALAH] GAMBAR MEGAWATI BERMAIN SLOT") == "GAMBAR MEGAWATI BERMAIN SLOT"


def test_encode_huruf_kecil(monkeypatch):
    diterima = []

    class Model:
        def encode(self, teks, **kw):
            diterima.extend(teks)
            return np.zeros((len(teks), 2), dtype=np.float32)

    monkeypatch.setattr(rag, "_model", lambda: Model())
    rag.encode(["GAMBAR MEGAWATI", "Vaksin"])
    assert diterima == ["gambar megawati", "vaksin"]
