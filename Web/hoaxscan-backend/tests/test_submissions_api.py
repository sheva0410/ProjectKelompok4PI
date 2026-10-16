from sqlalchemy import func, select

from app.models import Submission


def jumlah_baris(db) -> int:
    return db.scalar(select(func.count()).select_from(Submission))


# --- POST /api/submissions --------------------------------------------------

def test_post_berhasil(client, scraper_berhasil):
    r = client.post(
        "/api/submissions", json={"url": "https://www.detik.com/a?utm_source=x#top"}
    )
    assert r.status_code == 201
    data = r.json()
    assert data["id"] >= 1
    assert data["status"] == "pending"
    assert data["title"] == "Judul Uji"
    assert data["normalized_url"] == "https://detik.com/a"
    assert data["result"] is None
    assert "url_hash" not in data


def test_post_memanggil_scraper_dengan_url_asli(client, scraper_berhasil):
    client.post("/api/submissions", json={"url": "https://detik.com/a/"})
    assert scraper_berhasil == ["https://detik.com/a/"]


def test_post_url_sama_penulisan_beda_hash_sama(client, db, scraper_berhasil):
    client.post("/api/submissions", json={"url": "https://www.detik.com/a?utm_source=x#top"})
    client.post("/api/submissions", json={"url": "https://detik.com/a/"})
    hashes = db.scalars(select(Submission.url_hash)).all()
    assert len(hashes) == 2
    assert hashes[0] == hashes[1]


def test_post_dua_kali_tetap_dua_baris(client, db, scraper_berhasil):
    """Setiap pengecekan dicatat, dasar untuk menghitung trending."""
    for _ in range(2):
        client.post("/api/submissions", json={"url": "https://detik.com/a"})
    assert jumlah_baris(db) == 2


def test_post_galat_scraping_jadi_422_berbentuk_teks(client, scraper_gagal):
    r = client.post("/api/submissions", json={"url": "https://tidak-ada.com/a"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Domain tidak ditemukan"


def test_post_galat_scraping_tidak_tersimpan(client, db, scraper_gagal):
    client.post("/api/submissions", json={"url": "https://tidak-ada.com/a"})
    assert jumlah_baris(db) == 0


def test_post_skema_salah_422_berbentuk_list(client, db, scraper_berhasil):
    r = client.post("/api/submissions", json={"url": "ftp://contoh.com"})
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)
    assert scraper_berhasil == []
    assert jumlah_baris(db) == 0


def test_post_tanpa_url_422(client, scraper_berhasil):
    r = client.post("/api/submissions", json={})
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)


def test_post_url_terlalu_panjang_422(client, scraper_berhasil):
    r = client.post("/api/submissions", json={"url": "https://detik.com/" + "a" * 3000})
    assert r.status_code == 422


# --- GET /api/submissions/{id} ----------------------------------------------

def test_get_satu_submission(client, scraper_berhasil):
    dibuat = client.post("/api/submissions", json={"url": "https://detik.com/a"}).json()
    r = client.get(f"/api/submissions/{dibuat['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == dibuat["id"]
    assert data["normalized_url"] == dibuat["normalized_url"]
    assert data["title"] == dibuat["title"]


def test_get_id_tidak_ada_404(client):
    r = client.get("/api/submissions/9999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Submission tidak ditemukan"


def test_get_id_bukan_angka_422(client):
    assert client.get("/api/submissions/abc").status_code == 422


# --- GET /api/submissions ---------------------------------------------------

def test_list_terbaru_di_atas(client, scraper_berhasil):
    for i in range(3):
        client.post("/api/submissions", json={"url": f"https://detik.com/a{i}"})
    ids = [s["id"] for s in client.get("/api/submissions").json()]
    assert ids == sorted(ids, reverse=True)
    assert len(ids) == 3


def test_list_limit_dan_offset(client, scraper_berhasil):
    for i in range(3):
        client.post("/api/submissions", json={"url": f"https://detik.com/a{i}"})
    assert len(client.get("/api/submissions?limit=1").json()) == 1
    assert len(client.get("/api/submissions?limit=2&offset=2").json()) == 1


def test_list_limit_di_luar_batas_422(client):
    assert client.get("/api/submissions?limit=500").status_code == 422
    assert client.get("/api/submissions?limit=0").status_code == 422
    assert client.get("/api/submissions?offset=-1").status_code == 422


def test_list_kosong(client):
    r = client.get("/api/submissions")
    assert r.status_code == 200
    assert r.json() == []