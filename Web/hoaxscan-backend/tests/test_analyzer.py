import pytest

from app.services import analyzer
from app.services.analyzer import AnalysisError, analyze
from app.services.scraper import Article

ARTIKEL = Article(title="Judul", text="isi artikel " * 50)


def test_skor_yakin_hoax(classifier_palsu):
    classifier_palsu.update(label="hoax", prob_hoax=0.95, confident=True)
    out = analyze(ARTIKEL)
    assert out.label == "hoax"
    assert out.confidence == 0.95
    assert out.modalitas_dinilai == ["teks"]


def test_skor_yakin_fakta_confidence_dari_sisi_fakta(classifier_palsu):
    classifier_palsu.update(label="fakta", prob_hoax=0.02, confident=True)
    out = analyze(ARTIKEL)
    assert out.label == "fakta"
    assert out.confidence == 0.98


def test_skor_ragu_jadi_tidak_pasti(classifier_palsu):
    classifier_palsu.update(label="hoax", prob_hoax=0.6, confident=False)
    out = analyze(ARTIKEL)
    assert out.label == "tidak_pasti"
    assert out.confidence == 0.6


def test_artikel_terpotong_diberi_catatan(classifier_palsu):
    classifier_palsu.update(status="terpotong")
    assert "sangat panjang" in analyze(ARTIKEL).explanation


def test_teks_terlalu_pendek_tidak_menilai_apa_pun(classifier_palsu):
    classifier_palsu.update(label=None, prob_hoax=None, confident=False, status="teks_terlalu_pendek")
    out = analyze(ARTIKEL)
    assert out.label == "tidak_pasti"
    assert out.modalitas_dinilai == []


def test_model_belum_ada_jadi_analysis_error(monkeypatch, tmp_path):
    monkeypatch.setattr(analyzer.settings, "model_dir", str(tmp_path / "tidak-ada"))
    analyzer.get_classifier.cache_clear()
    with pytest.raises(AnalysisError, match="belum tersedia"):
        analyze(ARTIKEL)
