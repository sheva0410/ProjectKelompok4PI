from app.config import settings
from app.services import llm_check


def _set(monkeypatch, key, model, daftar=None, error=None):
    monkeypatch.setattr(settings, "gemini_api_key", key)
    monkeypatch.setattr(settings, "gemini_model", model)

    def palsu(k):
        if error:
            raise error
        return daftar or []

    monkeypatch.setattr(llm_check, "_daftar_model", palsu)


def test_key_kosong(monkeypatch):
    _set(monkeypatch, "", "gemini-x")
    assert llm_check.cek_gemini() is False
    assert llm_check.LLM_TERSEDIA is False


def test_model_kosong(monkeypatch):
    _set(monkeypatch, "kunci", "")
    assert llm_check.cek_gemini() is False


def test_gagal_panggil_tidak_crash(monkeypatch):
    _set(monkeypatch, "kunci", "gemini-x", error=RuntimeError("401"))
    assert llm_check.cek_gemini() is False


def test_model_tidak_ada(monkeypatch):
    _set(monkeypatch, "kunci", "gemini-x", daftar=["models/gemini-x-lite"])
    assert llm_check.cek_gemini() is False


def test_berhasil(monkeypatch):
    _set(monkeypatch, "kunci", "gemini-x", daftar=["models/gemini-x"])
    assert llm_check.cek_gemini() is True
    assert llm_check.LLM_TERSEDIA is True
