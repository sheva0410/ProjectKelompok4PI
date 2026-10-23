"""Gerbang dua lapis di analyze() (AI-06). Tanpa model, tanpa database, tanpa Gemini."""
import logging

import pytest

from app.services import analyzer
from app.services.scraper import Article

TEKS = "isi artikel " * 50
RUJUKAN = {"judul": "[SALAH] X", "ringkasan": "r", "link": "https://turnbackhoax.id/x",
           "tanggal": "1 Jan 2023", "skor": 0.8}
HASIL_GEMINI = {"label": "hoax", "confidence": 0.9, "penjelasan": "Gemini menilai hoax.",
                "sumber_rujukan": [RUJUKAN], "modalitas_dinilai": ["teks", "gambar"]}


@pytest.fixture
def pipa(monkeypatch):
    """Classifier, RAG, dan Gemini palsu. Ubah `p.clf` / `p.llm` untuk mengatur keluarannya."""
    class Pipa:
        def __init__(self):
            self.clf = {"label": "hoax", "prob_hoax": 0.95, "confident": True, "status": "ok"}
            self.llm = HASIL_GEMINI
            self.panggilan = []

    p = Pipa()

    class Classifier:
        def classify(self, text):
            return dict(p.clf)

    def verifikasi(teks, **kw):
        p.panggilan.append(kw)
        return p.llm

    monkeypatch.setattr(analyzer, "get_classifier", lambda: Classifier())
    monkeypatch.setattr(analyzer, "verifikasi", verifikasi)
    monkeypatch.setattr(analyzer.rag, "retrieve", lambda teks: [RUJUKAN])
    monkeypatch.setattr(analyzer.llm_check, "LLM_TERSEDIA", True)
    return p


def test_yakin_tanpa_media_selesai_sendiri(pipa, caplog):
    with caplog.at_level(logging.INFO, logger="app.services.analyzer"):
        out = analyzer.analyze(Article("Judul", TEKS))
    assert pipa.panggilan == []
    assert (out.label, out.confidence, out.modalitas_dinilai) == ("hoax", 0.95, ["teks"])
    assert "Gerbang: selesai sendiri" in caplog.text


def test_ragu_tanpa_media_diteruskan_ke_gemini(pipa, caplog):
    pipa.clf.update(label="fakta", prob_hoax=0.3, confident=False)
    with caplog.at_level(logging.INFO, logger="app.services.analyzer"):
        out = analyzer.analyze(Article("Judul", TEKS))
    assert len(pipa.panggilan) == 1
    kw = pipa.panggilan[0]
    assert kw["classifier"] == {"label": "fakta", "confidence": 0.7}
    assert kw["rujukan"] == [RUJUKAN]
    assert kw["gambar_url"] is None and kw["video_url"] is None
    assert out.label == "hoax"
    assert out.sources == [{"title": "[SALAH] X", "url": "https://turnbackhoax.id/x",
                            "tanggal": "1 Jan 2023"}]
    assert "Gerbang: skor rendah" in caplog.text


def test_bergambar_skor_tinggi_tetap_ke_gemini(pipa, caplog):
    with caplog.at_level(logging.INFO, logger="app.services.analyzer"):
        out = analyzer.analyze(Article("Judul", TEKS, top_image="https://contoh.com/a.jpg"))
    assert pipa.panggilan[0]["gambar_url"] == "https://contoh.com/a.jpg"
    assert out.modalitas_dinilai == ["teks", "gambar"]
    assert "Gerbang: ada media" in caplog.text


def test_video_pertama_yang_dikirim(pipa):
    analyzer.analyze(Article("Judul", TEKS, video_urls=["https://v/1", "https://v/2"]))
    assert pipa.panggilan[0]["video_url"] == "https://v/1"


def test_teks_pendek_tanpa_media_tidak_ke_gemini(pipa):
    pipa.clf.update(label=None, prob_hoax=None, confident=False, status="teks_terlalu_pendek")
    out = analyzer.analyze(Article("Judul", "pendek"))
    assert pipa.panggilan == []
    assert (out.label, out.modalitas_dinilai) == ("tidak_pasti", [])


def test_teks_pendek_bergambar_gemini_tanpa_hasil_classifier(pipa):
    pipa.clf.update(label=None, prob_hoax=None, confident=False, status="teks_terlalu_pendek")
    analyzer.analyze(Article("Judul", "pendek", top_image="https://contoh.com/a.jpg"))
    assert pipa.panggilan[0]["classifier"] is None


def test_gemini_tidak_tersedia_tidak_dipanggil(pipa, monkeypatch, caplog):
    monkeypatch.setattr(analyzer.llm_check, "LLM_TERSEDIA", False)
    pipa.clf.update(prob_hoax=0.6, confident=False)
    with caplog.at_level(logging.INFO, logger="app.services.analyzer"):
        out = analyzer.analyze(Article("Judul", TEKS))
    assert pipa.panggilan == []
    assert (out.label, out.confidence) == ("tidak_pasti", 0.6)
    assert "Gemini tidak tersedia" in caplog.text


def test_gemini_gagal_pada_halaman_bergambar_pakai_classifier(pipa):
    pipa.llm = None
    out = analyzer.analyze(Article("Judul", TEKS, top_image="https://contoh.com/a.jpg"))
    assert (out.label, out.confidence, out.modalitas_dinilai) == ("hoax", 0.95, ["teks"])
    assert "belum dinilai" in out.explanation
