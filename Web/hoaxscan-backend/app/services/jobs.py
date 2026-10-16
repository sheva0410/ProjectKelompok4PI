import logging

from app.database import SessionLocal
from app.models import AnalysisResult, Submission
from app.services.analyzer import (
    VALID_LABELS,
    VALID_MODALITAS,
    AnalysisError,
    AnalysisOutput,
    analyze,
)
from app.services.scraper import Article

log = logging.getLogger(__name__)


def _validasi(out: AnalysisOutput) -> None:
    if out.label not in VALID_LABELS:
        raise AnalysisError("Hasil analisis tidak valid (label tidak dikenal)")
    if not 0.0 <= out.confidence <= 1.0:
        raise AnalysisError("Hasil analisis tidak valid (skor di luar 0 sampai 1)")
    if not set(out.modalitas_dinilai) <= VALID_MODALITAS:
        raise AnalysisError("Hasil analisis tidak valid (modalitas tidak dikenal)")


def _tandai_gagal(db, submission_id: int, pesan: str) -> None:
    sub = db.get(Submission, submission_id)
    if sub is not None:
        sub.status = "failed"
        sub.error_message = pesan
        db.commit()


def run_analysis(submission_id: int, article: Article) -> None:
    """Berjalan di latar belakang, memakai sesi database sendiri.

    Sesi milik request sudah ditutup ketika fungsi ini berjalan.
    """
    db = SessionLocal()
    try:
        sub = db.get(Submission, submission_id)
        if sub is None:
            return
        sub.status = "processing"
        db.commit()

        try:
            out = analyze(article)
            _validasi(out)
            db.add(
                AnalysisResult(
                    submission_id=submission_id,
                    label=out.label,
                    confidence=out.confidence,
                    explanation=out.explanation,
                    sources=out.sources,
                    modalitas_dinilai=out.modalitas_dinilai,
                )
            )
            sub.status = "done"
            sub.error_message = None
            db.commit()
        except AnalysisError as e:
            db.rollback()
            _tandai_gagal(db, submission_id, str(e))
        except Exception:
            db.rollback()
            log.exception("Analisis submission %s gagal", submission_id)
            _tandai_gagal(db, submission_id, "Analisis gagal. Coba lagi nanti.")
    finally:
        db.close()