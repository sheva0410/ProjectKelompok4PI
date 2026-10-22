import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.models import AnalysisResult, Submission


def buat_submission(db, url="https://detik.com/a"):
    s = Submission(url=url, normalized_url=url, url_hash="hash-" + url)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_submission_nilai_default(db):
    s = buat_submission(db)
    assert s.status == "pending"
    assert s.created_at is not None
    assert s.title is None
    assert s.error_message is None


def test_relasi_hasil_analisis(db):
    s = buat_submission(db)
    db.add(
        AnalysisResult(
            submission_id=s.id,
            label="hoax",
            confidence=0.91,
            explanation="uji",
            sources=[{"title": "x", "url": "https://x.com"}],
        )
    )
    db.commit()
    db.refresh(s)
    assert s.result.label == "hoax"
    assert s.result.sources == [{"title": "x", "url": "https://x.com"}]


def test_modalitas_dinilai_default_kosong(db):
    s = buat_submission(db)
    db.add(
        AnalysisResult(
            submission_id=s.id, label="fakta", confidence=0.5, explanation="uji", sources=[]
        )
    )
    db.commit()
    db.refresh(s)
    assert s.result.modalitas_dinilai == []


def test_modalitas_dinilai_default_di_level_database(db):
    """Insert SQL mentah tanpa kolom itu: default harus datang dari database (migrasi)."""
    s = buat_submission(db)
    db.execute(
        text(
            "INSERT INTO analysis_results (submission_id, label, confidence, explanation, sources) "
            "VALUES (:id, 'hoax', 0.9, 'uji', '[]')"
        ),
        {"id": s.id},
    )
    db.commit()
    nilai = db.execute(text("SELECT modalitas_dinilai FROM analysis_results")).scalar()
    assert nilai == []


def test_modalitas_dinilai_bisa_diisi(db):
    s = buat_submission(db)
    db.add(
        AnalysisResult(
            submission_id=s.id,
            label="hoax",
            confidence=0.8,
            explanation="uji",
            sources=[],
            modalitas_dinilai=["teks", "gambar"],
        )
    )
    db.commit()
    db.refresh(s)
    assert s.result.modalitas_dinilai == ["teks", "gambar"]


def test_satu_submission_satu_hasil(db):
    s = buat_submission(db)
    db.add(AnalysisResult(submission_id=s.id, label="hoax", confidence=0.9, explanation="a", sources=[]))
    db.commit()
    db.add(AnalysisResult(submission_id=s.id, label="fakta", confidence=0.5, explanation="b", sources=[]))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_hapus_submission_hasil_ikut_terhapus(db):
    s = buat_submission(db)
    db.add(AnalysisResult(submission_id=s.id, label="hoax", confidence=0.9, explanation="a", sources=[]))
    db.commit()
    db.delete(s)
    db.commit()
    assert db.scalars(select(AnalysisResult)).all() == []


def test_hasil_tanpa_submission_ditolak(db):
    db.add(AnalysisResult(submission_id=12345, label="hoax", confidence=0.9, explanation="a", sources=[]))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


# --- skema hasil migrasi ----------------------------------------------------

def test_tabel_hasil_migrasi_lengkap(db):
    insp = inspect(db.get_bind())
    assert {"submissions", "analysis_results", "alembic_version"} <= set(insp.get_table_names())


def test_kolom_modalitas_dinilai_hasil_migrasi(db):
    insp = inspect(db.get_bind())
    kolom = {c["name"]: c for c in insp.get_columns("analysis_results")}
    assert "modalitas_dinilai" in kolom
    assert kolom["modalitas_dinilai"]["nullable"] is False
    assert "jsonb" in str(kolom["modalitas_dinilai"]["type"]).lower()


def test_indeks_untuk_trending_ada(db):
    insp = inspect(db.get_bind())
    diindeks = {c for idx in insp.get_indexes("submissions") for c in idx["column_names"]}
    assert {"url_hash", "created_at", "status"} <= diindeks