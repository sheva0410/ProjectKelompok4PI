import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent.parent

# Lokal: dibaca dari file .env.test. Di GitHub Actions: dari environment.
load_dotenv(ROOT / ".env.test")

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.exit(
        "TEST_DATABASE_URL belum di-set. Buat file .env.test (lihat .env.test.example).",
        returncode=2,
    )

# Pengaman: tes menghapus isi tabel, jadi database-nya wajib berakhiran _test.
if not (make_url(TEST_DATABASE_URL).database or "").endswith("_test"):
    pytest.exit(
        "Nama database tes harus berakhiran _test supaya database dev tidak terhapus.",
        returncode=2,
    )

# Harus dilakukan SEBELUM app diimpor, karena app membaca DATABASE_URL saat diimpor.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
# Tes tidak boleh ikut jeda stub dari .env milik development.
os.environ["STUB_DELAY_SECONDS"] = "0"


@pytest.fixture(scope="session", autouse=True)
def _siapkan_database():
    """Bangun skema lewat migrasi Alembic, jadi migrasi ikut teruji."""
    from app.database import engine

    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")
    engine.dispose()


@pytest.fixture(autouse=True)
def _bersihkan_tabel(_siapkan_database):
    """Setiap tes mulai dari tabel kosong."""
    from app.database import engine

    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE analysis_results, submissions RESTART IDENTITY CASCADE")
        )
    yield


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def scraper_berhasil(monkeypatch):
    """Scraper palsu: bentuknya sama dengan aslinya, tapi tanpa internet."""
    from app.services.scraper import Article

    dipanggil = []

    def palsu(url):
        dipanggil.append(url)
        return Article(title="Judul Uji", text="isi artikel " * 50)

    monkeypatch.setattr("app.routers.submissions.extract_article", palsu)
    return dipanggil


@pytest.fixture
def scraper_gagal(monkeypatch):
    from app.services.scraper import ScrapeError

    def palsu(url):
        raise ScrapeError("Domain tidak ditemukan")

    monkeypatch.setattr("app.routers.submissions.extract_article", palsu)


@pytest.fixture
def scraper_dengan_video(monkeypatch):
    """Scraper palsu untuk halaman yang memuat gambar dan video."""
    from app.services.scraper import Article

    def palsu(url):
        return Article(
            title="Judul Video",
            text="isi artikel " * 50,
            top_image="https://contoh.com/a.jpg",
            video_urls=["https://www.youtube.com/embed/abc123"],
        )

    monkeypatch.setattr("app.routers.submissions.extract_article", palsu)