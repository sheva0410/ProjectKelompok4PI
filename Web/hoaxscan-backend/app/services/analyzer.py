import logging
import os
import threading
from dataclasses import dataclass, field
from functools import lru_cache

from app.config import settings
from app.services import llm_check, rag
from app.services.gemini_verifier import verifikasi
from app.services.scraper import Article

log = logging.getLogger(__name__)

VALID_LABELS = {"hoax", "fakta", "tidak_pasti"}
VALID_MODALITAS = {"teks", "gambar", "video"}


class AnalysisError(Exception):
    """Gagal menganalisis. Pesannya aman ditampilkan ke pengguna."""




@dataclass
class AnalysisOutput:
    label: str
    confidence: float
    explanation: str
    sources: list = field(default_factory=list)
    modalitas_dinilai: list[str] = field(default_factory=list)


_kunci_model = threading.Lock()


def siapkan_model():
    """Pastikan file model ada di model_dir. Bila belum, unduh dari Hugging Face (sekitar 500 MB)."""
    if os.path.isfile(os.path.join(settings.model_dir, "model.safetensors")):
        return
    if not settings.model_repo:
        raise AnalysisError("Model AI belum tersedia di server")
    try:
        from huggingface_hub import snapshot_download

        snapshot_download(settings.model_repo, local_dir=settings.model_dir)
    except Exception as e:
        raise AnalysisError("Model AI belum tersedia di server") from e


@lru_cache(maxsize=1)
def _muat_classifier():
    siapkan_model()
    # diimpor di sini supaya torch hanya dimuat saat model benar-benar dipakai
    from app.services.hoax_classifier import HoaxClassifier

    return HoaxClassifier(settings.model_dir)


def get_classifier():
    """Muat model IndoBERT sekali saja, saat analisis pertama."""
    # kunci supaya dua analisis yang datang bersamaan tidak mengunduh model dua kali
    with _kunci_model:
        return _muat_classifier()


def _dari_classifier(label: str, confidence: float, catatan: str) -> AnalysisOutput:
    return AnalysisOutput(
        label=label,
        confidence=confidence,
        explanation=f"Model IndoBERT menilai teks artikel ini sebagai {label} "
                    f"dengan keyakinan {confidence:.0%}.{catatan}",
        modalitas_dinilai=["teks"],
    )


def analyze(article: Article) -> AnalysisOutput:
    """TITIK SAMBUNG MODUL AI, dengan gerbang dua lapis (AI-06).

    Lapis 1: halaman yang punya gambar atau video selalu diteruskan ke RAG dan
    Gemini, berapa pun skor IndoBERT, karena IndoBERT hanya membaca teks.
    Lapis 2: tanpa media, Gemini dipanggil hanya bila skor IndoBERT di bawah
    ambang ML-06 (hasil["confident"] bernilai False).
    Kontraknya: kembalikan AnalysisOutput, atau lempar AnalysisError
    (pesan aman ditampilkan ke pengguna) bila gagal.
    """
    hasil = get_classifier().classify(article.text)
    ada_media = bool(article.top_image or article.video_urls)
    teks_dinilai = hasil["label"] is not None
    confidence = round(max(hasil["prob_hoax"], 1 - hasil["prob_hoax"]), 4) if teks_dinilai else 0.0
    catatan = ""
    if hasil["status"] == "terpotong":
        catatan = " Artikel sangat panjang, jadi hanya bagian awalnya yang dinilai."

    if ada_media:
        alasan = "ada media"
    elif not teks_dinilai:
        alasan = "teks terlalu pendek"
    elif hasil["confident"]:
        alasan = "selesai sendiri"
    else:
        alasan = "skor rendah"
    lanjut = alasan in ("ada media", "skor rendah")
    if lanjut and not llm_check.LLM_TERSEDIA:
        alasan += ", Gemini tidak tersedia"
        lanjut = False
    log.info("Gerbang: %s (IndoBERT %s, prob_hoax %s, gambar %s, video %s)",
             alasan, hasil["label"], hasil["prob_hoax"],
             bool(article.top_image), len(article.video_urls))

    llm = None
    if lanjut:
        llm = verifikasi(
            "\n\n".join(filter(None, [article.title, article.text])),
            classifier={"label": hasil["label"], "confidence": confidence} if teks_dinilai else None,
            # Korpus RAG diindeks per judul, jadi judul artikel yang paling sebanding
            rujukan=rag.retrieve(article.title or article.text),
            gambar_url=article.top_image,
            video_url=article.video_urls[0] if article.video_urls else None,
        )

    if llm:
        # ponytail: hasil Gemini dipakai apa adanya; AI-07 menggantinya dengan aggregate()
        return AnalysisOutput(
            label=llm["label"],
            confidence=round(llm["confidence"], 4),
            explanation=llm["penjelasan"] + catatan,
            sources=[{"title": r["judul"], "url": r["link"], "tanggal": r.get("tanggal")}
                     for r in llm["sumber_rujukan"]],
            modalitas_dinilai=llm["modalitas_dinilai"],
        )
    if not teks_dinilai:
        return AnalysisOutput("tidak_pasti", 0.0, "Teks artikel terlalu pendek untuk dinilai.")
    if hasil["confident"]:
        if ada_media:
            catatan += " Gambar dan video belum dinilai karena verifikasi lanjutan tidak tersedia."
        return _dari_classifier(hasil["label"], confidence, catatan)
    return AnalysisOutput(
        label="tidak_pasti",
        confidence=confidence,
        explanation="Skor model belum cukup meyakinkan dan verifikasi lanjutan tidak tersedia, "
                    "jadi artikel perlu diperiksa sendiri." + catatan,
        modalitas_dinilai=["teks"],
    )
