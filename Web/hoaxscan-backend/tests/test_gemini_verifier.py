from types import SimpleNamespace

from google.genai import errors

from app.services import gemini_verifier as gv
from app.services import llm_check
from app.services.scraper import ScrapeError

RUJUKAN = [{"judul": "J1", "ringkasan": "R1", "link": "https://contoh.id/1"}]
OK = '{"label":"hoax","confidence":0.8,"penjelasan":"Klaim X dibantah.","sumber_rujukan":[1]}'
GAMBAR = gv.types.Part.from_bytes(data=b"\xff\xd8gambar", mime_type="image/jpeg")


def _palsu(monkeypatch, teks=None, error=None, gagal_dulu=0):
    """Client Gemini palsu. Simpan argumen panggilan terakhir di Client.dikirim."""
    status = {"sisa_gagal": gagal_dulu}

    class Client:
        dikirim = None

        def __init__(self, **kw):
            pass

        class models:
            @staticmethod
            def generate_content(**kw):
                Client.dikirim = kw
                if error:
                    raise error
                if status["sisa_gagal"]:
                    status["sisa_gagal"] -= 1
                    raise errors.APIError(503, {"error": {"message": "sibuk", "status": "UNAVAILABLE"}})
                return SimpleNamespace(text=teks)

    monkeypatch.setattr(gv.genai, "Client", Client)
    monkeypatch.setattr(gv.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm_check, "LLM_TERSEDIA", True)
    return Client


# --- AI-02: teks ------------------------------------------------------------

def test_berhasil(monkeypatch):
    _palsu(monkeypatch, OK)
    h = gv.verifikasi("teks", None, RUJUKAN)
    assert h == {"label": "hoax", "confidence": 0.8, "penjelasan": "Klaim X dibantah.",
                 "sumber_rujukan": RUJUKAN, "modalitas_dinilai": ["teks"]}


def test_pagar_blok_kode_terurai(monkeypatch):
    _palsu(monkeypatch, "```json\n" + OK + "\n```")
    assert gv.verifikasi("teks", None, RUJUKAN)["label"] == "hoax"


def test_json_rusak_jadi_none(monkeypatch):
    _palsu(monkeypatch, "bukan json")
    assert gv.verifikasi("teks") is None


def test_field_hilang_jadi_none(monkeypatch):
    _palsu(monkeypatch, '{"label":"hoax"}')
    assert gv.verifikasi("teks") is None


def test_label_asing_jadi_none(monkeypatch):
    _palsu(monkeypatch, OK.replace('"hoax"', '"Hoax"'))
    assert gv.verifikasi("teks", None, RUJUKAN) is None


def test_confidence_di_luar_rentang(monkeypatch):
    _palsu(monkeypatch, OK.replace("0.8", "1.5"))
    assert gv.verifikasi("teks", None, RUJUKAN) is None


def test_nomor_rujukan_palsu_dibuang(monkeypatch):
    _palsu(monkeypatch, OK.replace("[1]", "[1, 9]"))
    assert gv.verifikasi("teks", None, RUJUKAN)["sumber_rujukan"] == RUJUKAN


def test_panggilan_gagal_jadi_none(monkeypatch):
    _palsu(monkeypatch, error=RuntimeError("putus"))
    assert gv.verifikasi("teks") is None


def test_llm_tidak_tersedia(monkeypatch):
    monkeypatch.setattr(llm_check, "LLM_TERSEDIA", False)
    assert gv.verifikasi("teks") is None


# --- AI-03: gambar ----------------------------------------------------------

def test_gambar_dikirim_dalam_satu_prompt(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    monkeypatch.setattr(gv, "unduh_gambar", lambda url: GAMBAR)
    h = gv.verifikasi("teks", None, RUJUKAN, gambar_url="https://contoh.id/a.jpg")
    contents = Client.dikirim["contents"]
    assert contents[0] is GAMBAR and "1 gambar utama artikel" in contents[1]
    assert h["modalitas_dinilai"] == ["teks", "gambar"]


def test_gambar_gagal_tetap_nilai_teks(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    monkeypatch.setattr(gv, "unduh_gambar", lambda url: None)
    h = gv.verifikasi("teks", gambar_url="https://contoh.id/a.jpg")
    assert isinstance(Client.dikirim["contents"], str)
    assert h["modalitas_dinilai"] == ["teks"]


def test_503_diulang_lalu_berhasil(monkeypatch):
    _palsu(monkeypatch, OK, gagal_dulu=2)
    assert gv.verifikasi("teks", None, RUJUKAN)["label"] == "hoax"


def test_503_terus_jadi_none(monkeypatch):
    _palsu(monkeypatch, OK, gagal_dulu=gv.RETRY_503)
    assert gv.verifikasi("teks") is None


def test_error_selain_503_tidak_diulang(monkeypatch):
    Client = _palsu(monkeypatch, error=errors.APIError(400, {"error": {"message": "x"}}))
    assert gv.verifikasi("teks") is None


# --- AI-04: video -----------------------------------------------------------

YT = "https://www.youtube.com/embed/dQw4w9WgXcQ"


def _video(monkeypatch, layak=True):
    monkeypatch.setattr(gv.gemini_video, "video_layak", lambda url: layak)


def test_youtube_dikirim_sebagai_link(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    _video(monkeypatch)
    h = gv.verifikasi("teks", video_url=YT)
    part = Client.dikirim["contents"][0]
    assert part.file_data.file_uri == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert "1 video dari halaman artikel" in Client.dikirim["contents"][-1]
    assert h["modalitas_dinilai"] == ["teks", "video"]


def test_youtube_ditolak_jatuh_ke_files_api(monkeypatch):
    panggilan = []

    class Client:
        def __init__(self, **kw):
            pass

        class models:
            @staticmethod
            def generate_content(**kw):
                panggilan.append(kw["contents"])
                if len(panggilan) == 1:
                    raise errors.ClientError(400, {"error": {"message": "link ditolak"}})
                return SimpleNamespace(text=OK)

    monkeypatch.setattr(gv.genai, "Client", Client)
    monkeypatch.setattr(llm_check, "LLM_TERSEDIA", True)
    _video(monkeypatch)
    berkas = object()

    class Upload:
        def __init__(self, client, url):
            pass

        def __enter__(self):
            return berkas

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(gv.gemini_video, "upload_video", Upload)
    h = gv.verifikasi("teks", video_url=YT)
    assert panggilan[1][0] is berkas
    assert h["modalitas_dinilai"] == ["teks", "video"]


def test_video_terlalu_panjang_dinilai_tanpa_video(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    _video(monkeypatch, layak=False)
    h = gv.verifikasi("teks", video_url=YT)
    assert isinstance(Client.dikirim["contents"], str)
    assert h["modalitas_dinilai"] == ["teks"]


def test_upload_gagal_dinilai_tanpa_video(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    _video(monkeypatch)

    def gagal(client, url):
        raise RuntimeError("download gagal")

    monkeypatch.setattr(gv.gemini_video, "upload_video", gagal)
    h = gv.verifikasi("teks", video_url="https://20.detik.com/embed/1")
    assert isinstance(Client.dikirim["contents"], str)
    assert h["modalitas_dinilai"] == ["teks"]


def test_gambar_dan_video_bersama(monkeypatch):
    Client = _palsu(monkeypatch, OK)
    _video(monkeypatch)
    monkeypatch.setattr(gv, "unduh_gambar", lambda url: GAMBAR)
    h = gv.verifikasi("teks", gambar_url="https://contoh.id/a.jpg", video_url=YT)
    contents = Client.dikirim["contents"]
    assert contents[0] is GAMBAR and contents[1].file_data is not None
    assert h["modalitas_dinilai"] == ["teks", "gambar", "video"]


# --- unduh_gambar -----------------------------------------------------------

class _Respon:
    def __init__(self, status=200, tipe="image/jpeg", isi=b"\xff\xd8gambar"):
        self.status_code = status
        self.headers = {"content-type": tipe}
        self.content = isi


def _unduh(monkeypatch, respon=None, alamat_ok=True):
    def cek(url):
        if not alamat_ok:
            raise ScrapeError("Alamat URL tidak diizinkan")

    monkeypatch.setattr(gv, "_check_url", cek)
    monkeypatch.setattr(gv.requests, "get", lambda *a, **k: respon)
    return gv.unduh_gambar("https://contoh.id/a.jpg")


def test_unduh_gambar_berhasil(monkeypatch):
    part = _unduh(monkeypatch, _Respon(tipe="image/jpeg; charset=binary"))
    assert part.inline_data.mime_type == "image/jpeg"


def test_unduh_gambar_format_tidak_didukung(monkeypatch):
    assert _unduh(monkeypatch, _Respon(tipe="image/svg+xml")) is None


def test_unduh_gambar_http_error(monkeypatch):
    assert _unduh(monkeypatch, _Respon(status=404)) is None


def test_unduh_gambar_terlalu_besar(monkeypatch):
    monkeypatch.setattr(gv, "MAX_GAMBAR", 3)
    assert _unduh(monkeypatch, _Respon()) is None


def test_unduh_gambar_alamat_internal_ditolak(monkeypatch):
    assert _unduh(monkeypatch, _Respon(), alamat_ok=False) is None
