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


@pytest.fixture
def model_kosong(monkeypatch, tmp_path):
    """Folder model belum ada; unduhan Hugging Face dipalsukan."""
    folder = tmp_path / "model"
    monkeypatch.setattr(analyzer.settings, "model_dir", str(folder))
    monkeypatch.setattr(analyzer.settings, "model_repo", "contoh/model")
    analyzer._muat_classifier.cache_clear()
    yield folder
    analyzer._muat_classifier.cache_clear()


def test_model_belum_ada_dan_tanpa_repo_jadi_analysis_error(model_kosong, monkeypatch):
    monkeypatch.setattr(analyzer.settings, "model_repo", "")
    with pytest.raises(AnalysisError, match="belum tersedia"):
        analyze(ARTIKEL)


def test_model_belum_ada_diunduh_dari_hugging_face(model_kosong, monkeypatch):
    diminta = []
    monkeypatch.setattr("huggingface_hub.snapshot_download",
                        lambda repo, local_dir: diminta.append((repo, local_dir)))
    analyzer.siapkan_model()
    assert diminta == [("contoh/model", str(model_kosong))]


def test_model_sudah_ada_tidak_diunduh_lagi(model_kosong, monkeypatch):
    model_kosong.mkdir()
    (model_kosong / "model.safetensors").write_bytes(b"")
    monkeypatch.setattr("huggingface_hub.snapshot_download",
                        lambda *a, **k: pytest.fail("tidak boleh mengunduh"))
    analyzer.siapkan_model()


def test_unduhan_gagal_jadi_analysis_error(model_kosong, monkeypatch):
    def gagal(*a, **k):
        raise OSError("koneksi putus")

    monkeypatch.setattr("huggingface_hub.snapshot_download", gagal)
    with pytest.raises(AnalysisError, match="belum tersedia"):
        analyze(ARTIKEL)
