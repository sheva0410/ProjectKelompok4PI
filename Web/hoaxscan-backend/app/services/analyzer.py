import os
import threading
from dataclasses import dataclass, field
from functools import lru_cache

from app.config import settings
from app.services.scraper import Article

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


def analyze(article: Article) -> AnalysisOutput:
    """TITIK SAMBUNG MODUL AI.

    Teks dinilai IndoBERT (hoax_classifier.py). Skor yang belum meyakinkan
    nantinya diteruskan ke Gemini (RAG); selama bagian itu belum ada, hasilnya
    "tidak_pasti". Gambar dan video belum dinilai.
    Kontraknya: kembalikan AnalysisOutput, atau lempar AnalysisError
    (pesan aman ditampilkan ke pengguna) bila gagal.
    """
    hasil = get_classifier().classify(article.text)
    if hasil["label"] is None:
        return AnalysisOutput("tidak_pasti", 0.0, "Teks artikel terlalu pendek untuk dinilai.")

    p = hasil["prob_hoax"]
    confidence = round(max(p, 1 - p), 4)  # keyakinan pada label yang dipilih
    catatan = ""
    if hasil["status"] == "terpotong":
        catatan = " Artikel sangat panjang, jadi hanya bagian awalnya yang dinilai."

    if hasil["confident"]:
        return AnalysisOutput(
            label=hasil["label"],
            confidence=confidence,
            explanation=f"Model IndoBERT menilai teks artikel ini sebagai {hasil['label']} "
                        f"dengan keyakinan {confidence:.0%}.{catatan}",
            modalitas_dinilai=["teks"],
        )

    # TODO tim AI: teruskan ke Gemini (RAG) untuk verifikasi
    return AnalysisOutput(
        label="tidak_pasti",
        confidence=confidence,
        explanation="Skor model belum cukup meyakinkan, artikel perlu diverifikasi lebih lanjut." + catatan,
        modalitas_dinilai=["teks"],
    )
