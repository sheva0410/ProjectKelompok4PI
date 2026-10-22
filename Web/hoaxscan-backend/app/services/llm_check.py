import logging

from google import genai

from app.config import settings

log = logging.getLogger(__name__)

# Baca lewat `from app.services import llm_check` lalu `llm_check.LLM_TERSEDIA`.
# `from ... import LLM_TERSEDIA` menyalin nilainya dan tidak ikut berubah.
LLM_TERSEDIA = False


def _daftar_model(key: str) -> list[str]:
    # Client harus disimpan di variabel selama iterasi. Bila tidak, client
    # sudah ditutup sebelum halaman berikutnya diambil.
    client = genai.Client(api_key=key)
    return [m.name for m in client.models.list()]


def cek_gemini() -> bool:
    """Cek key dan model Gemini sekali saat startup. Tidak pernah melempar error.

    Bila gagal, LLM_TERSEDIA bernilai False dan aplikasi tetap jalan dalam
    mode classifier saja.
    """
    global LLM_TERSEDIA
    LLM_TERSEDIA = False
    key, model = settings.gemini_api_key.strip(), settings.gemini_model.strip()
    if not key:
        log.error("GEMINI_API_KEY kosong, jalan dalam mode classifier saja")
        return False
    if not model:
        log.error("GEMINI_MODEL kosong, isi di .env")
        return False
    try:
        tersedia = _daftar_model(key)
    except Exception:
        log.exception("Validasi Gemini gagal, jalan dalam mode classifier saja")
        return False
    log.info("Model Gemini tersedia: %s", tersedia)
    if model not in tersedia and f"models/{model}" not in tersedia:
        log.error("GEMINI_MODEL '%s' tidak ada di daftar model", model)
        return False
    log.info("Gemini siap dengan model %s", model)
    LLM_TERSEDIA = True
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not settings.gemini_model:
        # Mode bantu: tampilkan daftar model untuk dipilih sebagai GEMINI_MODEL
        print("\n".join(_daftar_model(settings.gemini_api_key)))
    print("LLM_TERSEDIA =", cek_gemini())
