import pytest
from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import AnalysisResult, Submission
from app.services.analyzer import AnalysisError, AnalysisOutput
from app.services.jobs import run_analysis
from app.services.scraper import Article


def kirim(client, url="https://detik.com/a"):
    r = client.post("/api/submissions", json={"url": url})
    assert r.status_code == 201
    return r.json()


def status_dan_hasil(client, submission_id):
    return client.get(f"/api/submissions/{submission_id}").json()


def hitung_hasil(db) -> int:
    return db.scalar(select(func.count()).select_from(AnalysisResult))


def analyzer_palsu(monkeypatch, fungsi):
    monkeypatch.setattr("app.services.jobs.analyze", fungsi)


# --- alur normal -----------------------------------------------------------

def test_respons_post_pending_lalu_get_done(client, scraper_berhasil):
    dibuat = kirim(client)
    assert dibuat["status"] == "pending"
    assert dibuat["result"] is None

    sesudah = status_dan_hasil(client, dibuat["id"])
    assert sesudah["status"] == "done"
    assert sesudah["error_message"] is None
    assert sesudah["result"]["label"] == "tidak_pasti"


def test_hasil_sementara_jujur_tidak_menilai_apa_pun(client, scraper_berhasil):
    """Stub tidak menilai teks, gambar, maupun video, jadi daftarnya harus kosong."""
    hasil = status_dan_hasil(client, kirim(client)["id"])["result"]
    assert hasil["confidence"] == 0.0
    assert hasil["modalitas_dinilai"] == []
    assert "belum terpasang" in hasil["explanation"]


def test_link_bervideo_diproses_dan_artikel_sampai_ke_analyzer(
    client, scraper_dengan_video, monkeypatch
):
    diterima = []

    def merekam(article):
        diterima.append(article)
        return AnalysisOutput("fakta", 0.7, "uji", [], ["teks", "video"])

    analyzer_palsu(monkeypatch, merekam)
    sub = status_dan_hasil(client, kirim(client)["id"])

    assert sub["status"] == "done"
    assert diterima[0].video_urls == ["https://www.youtube.com/embed/abc123"]
    assert sub["result"]["modalitas_dinilai"] == ["teks", "video"]


def test_status_processing_terlihat_selama_analisis(client, scraper_berhasil, monkeypatch):
    terekam = []

    def mengintip(article):
        with SessionLocal() as sesi_lain:
            terekam.append(sesi_lain.scalar(select(Submission.status)))
        return AnalysisOutput("fakta", 0.6, "uji", [], ["teks"])

    analyzer_palsu(monkeypatch, mengintip)
    kirim(client)
    assert terekam == ["processing"]


# --- galat -----------------------------------------------------------------

def test_galat_scraping_tidak_menjalankan_job(client, scraper_gagal, monkeypatch):
    dipanggil = []
    monkeypatch.setattr(
        "app.routers.submissions.run_analysis", lambda *a: dipanggil.append(a)
    )
    r = client.post("/api/submissions", json={"url": "https://tidak-ada.com/a"})
    assert r.status_code == 422
    assert dipanggil == []


def test_analyzer_gagal_status_failed_pesan_dari_analyzer(
    client, db, scraper_berhasil, monkeypatch
):
    def gagal(article):
        raise AnalysisError("Kuota Gemini habis")

    analyzer_palsu(monkeypatch, gagal)
    sub = status_dan_hasil(client, kirim(client)["id"])

    assert sub["status"] == "failed"
    assert sub["error_message"] == "Kuota Gemini habis"
    assert sub["result"] is None
    assert hitung_hasil(db) == 0


def test_error_tak_terduga_pesannya_umum_dan_tidak_membocorkan(
    client, scraper_berhasil, monkeypatch
):
    def meledak(article):
        raise RuntimeError("password=rahasia-internal")

    analyzer_palsu(monkeypatch, meledak)
    sub = status_dan_hasil(client, kirim(client)["id"])

    assert sub["status"] == "failed"
    assert sub["error_message"] == "Analisis gagal. Coba lagi nanti."
    assert "rahasia" not in sub["error_message"]


@pytest.mark.parametrize(
    "keluaran, potongan_pesan",
    [
        (AnalysisOutput("mungkin", 0.5, "uji", [], ["teks"]), "label tidak dikenal"),
        (AnalysisOutput("hoax", 1.5, "uji", [], ["teks"]), "skor di luar"),
        (AnalysisOutput("hoax", -0.1, "uji", [], ["teks"]), "skor di luar"),
        (AnalysisOutput("hoax", 0.5, "uji", [], ["audio"]), "modalitas tidak dikenal"),
    ],
)
def test_keluaran_analyzer_tidak_valid_jadi_failed(
    client, db, scraper_berhasil, monkeypatch, keluaran, potongan_pesan
):
    analyzer_palsu(monkeypatch, lambda article: keluaran)
    sub = status_dan_hasil(client, kirim(client)["id"])

    assert sub["status"] == "failed"
    assert potongan_pesan in sub["error_message"]
    assert hitung_hasil(db) == 0


@pytest.mark.parametrize("label", ["hoax", "fakta", "tidak_pasti"])
def test_semua_label_valid_diterima(client, scraper_berhasil, monkeypatch, label):
    analyzer_palsu(monkeypatch, lambda article: AnalysisOutput(label, 0.5, "uji", [], ["teks"]))
    sub = status_dan_hasil(client, kirim(client)["id"])
    assert sub["status"] == "done"
    assert sub["result"]["label"] == label


def test_job_untuk_id_yang_tidak_ada_tidak_error():
    run_analysis(999999, Article(title=None, text="x"))