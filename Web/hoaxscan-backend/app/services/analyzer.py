import time
from dataclasses import dataclass, field

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


def analyze(article: Article) -> AnalysisOutput:
    """TITIK SAMBUNG MODUL AI.

    Sementara berisi stub. Tim AI mengganti isi fungsi ini dengan alur
    teks -> IndoBERT -> Gemini (RAG) dan gambar/video -> Gemini (RAG).
    Kontraknya: kembalikan AnalysisOutput, atau lempar AnalysisError
    (pesan aman ditampilkan ke pengguna) bila gagal.
    """
    
    if settings.stub_delay_seconds:
        time.sleep(settings.stub_delay_seconds)  # agar proses terlihat saat polling
        
    return AnalysisOutput(
        label="tidak_pasti",
        confidence=0.0,
        explanation="Modul AI belum terpasang. Hasil ini hanya sementara.",
        sources=[],
        modalitas_dinilai=[],
    )
