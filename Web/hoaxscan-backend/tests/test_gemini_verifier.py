from types import SimpleNamespace

from app.services import gemini_verifier as gv
from app.services import llm_check

RUJUKAN = [{"judul": "J1", "ringkasan": "R1", "link": "https://contoh.id/1"}]
OK = '{"label":"hoax","confidence":0.8,"penjelasan":"Klaim X dibantah.","sumber_rujukan":[1]}'


def _palsu(monkeypatch, teks=None, error=None):
    class Client:
        def __init__(self, **kw):
            pass

        class models:
            @staticmethod
            def generate_content(**kw):
                if error:
                    raise error
                return SimpleNamespace(text=teks)

    monkeypatch.setattr(gv.genai, "Client", Client)
    monkeypatch.setattr(llm_check, "LLM_TERSEDIA", True)


def test_berhasil(monkeypatch):
    _palsu(monkeypatch, OK)
    h = gv.verifikasi_teks("teks", None, RUJUKAN)
    assert h == {"label": "hoax", "confidence": 0.8,
                 "penjelasan": "Klaim X dibantah.", "sumber_rujukan": RUJUKAN}


def test_pagar_blok_kode_terurai(monkeypatch):
    _palsu(monkeypatch, "```json\n" + OK + "\n```")
    assert gv.verifikasi_teks("teks", None, RUJUKAN)["label"] == "hoax"


def test_json_rusak_jadi_none(monkeypatch):
    _palsu(monkeypatch, "bukan json")
    assert gv.verifikasi_teks("teks") is None


def test_field_hilang_jadi_none(monkeypatch):
    _palsu(monkeypatch, '{"label":"hoax"}')
    assert gv.verifikasi_teks("teks") is None


def test_label_asing_jadi_none(monkeypatch):
    _palsu(monkeypatch, OK.replace('"hoax"', '"Hoax"'))
    assert gv.verifikasi_teks("teks", None, RUJUKAN) is None


def test_confidence_di_luar_rentang(monkeypatch):
    _palsu(monkeypatch, OK.replace("0.8", "1.5"))
    assert gv.verifikasi_teks("teks", None, RUJUKAN) is None


def test_nomor_rujukan_palsu_dibuang(monkeypatch):
    _palsu(monkeypatch, OK.replace("[1]", "[1, 9]"))
    assert gv.verifikasi_teks("teks", None, RUJUKAN)["sumber_rujukan"] == RUJUKAN


def test_panggilan_gagal_jadi_none(monkeypatch):
    _palsu(monkeypatch, error=RuntimeError("503"))
    assert gv.verifikasi_teks("teks") is None


def test_llm_tidak_tersedia(monkeypatch):
    monkeypatch.setattr(llm_check, "LLM_TERSEDIA", False)
    assert gv.verifikasi_teks("teks") is None
