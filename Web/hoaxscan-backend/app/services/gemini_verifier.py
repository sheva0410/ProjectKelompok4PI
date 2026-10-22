import json
import logging
import re

from google import genai
from google.genai import types

from app.config import settings
from app.services import llm_check

log = logging.getLogger(__name__)

# Sama dengan analyzer.VALID_LABELS. Disalin agar analyzer nanti bisa
# meng-import modul ini tanpa import melingkar.
VALID_LABELS = {"hoax", "fakta", "tidak_pasti"}
MAX_TEKS = 20_000  # karakter; artikel lebih panjang dipotong agar hemat kuota
TIMEOUT_MS = 30_000

PROMPT = """Kamu adalah pemeriksa fakta untuk berita berbahasa Indonesia.
Nilai apakah klaim utama pada ARTIKEL di bawah ini hoax, fakta, atau tidak_pasti.
Dasarkan penilaianmu hanya pada RUJUKAN. Jangan memakai ingatanmu sendiri untuk
memutuskan benar atau salah, dan dilarang menyebut sumber yang tidak ada di
daftar RUJUKAN. Bila rujukan tidak cukup untuk memutuskan, jawab tidak_pasti
dan jelaskan alasannya.

[ARTIKEL]
{teks}

[HASIL CLASSIFIER]
{classifier}

[RUJUKAN]
{rujukan}

[FORMAT JAWABAN]
Jawab hanya dengan JSON berikut, tanpa teks lain.
{{"label": "hoax" atau "fakta" atau "tidak_pasti",
 "confidence": angka 0 sampai 1,
 "penjelasan": "2 sampai 4 kalimat Bahasa Indonesia yang menyebut klaim spesifik",
 "sumber_rujukan": [nomor rujukan yang benar-benar dipakai]}}"""


def _format_classifier(c: dict | None) -> str:
    if not c:
        return "Tidak tersedia."
    return (f"IndoBERT menilai teks ini {c['label']} dengan keyakinan "
            f"{c['confidence']:.0%}. Anggap ini petunjuk tambahan, bukan putusan.")


def _format_rujukan(rujukan: list[dict]) -> str:
    if not rujukan:
        return "Tidak ada rujukan yang cukup mirip."
    return "\n".join(
        f"{i}. {r['judul']} | {r['ringkasan']} | {r['link']}"
        for i, r in enumerate(rujukan, 1)
    )


def _urai(raw: str) -> dict:
    # Buang pagar blok kode di awal dan akhir balasan sebelum json.loads
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))


def verifikasi_teks(teks: str, classifier: dict | None = None,
                    rujukan: list[dict] | None = None) -> dict | None:
    """Nilai teks artikel lewat Gemini.

    classifier: {"label": ..., "confidence": ...} dari IndoBERT, boleh None.
    rujukan: list dict berisi judul, ringkasan, link (keluaran AI-05), boleh None.

    Kembalikan {label, confidence, penjelasan, sumber_rujukan}, atau None bila
    Gemini tidak tersedia, panggilan gagal, atau balasan tidak valid.
    """
    if not llm_check.LLM_TERSEDIA:
        return None
    rujukan = rujukan or []
    prompt = PROMPT.format(
        teks=teks[:MAX_TEKS],
        classifier=_format_classifier(classifier),
        rujukan=_format_rujukan(rujukan),
    )
    try:
        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=TIMEOUT_MS),
        )
        resp = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                # Tanpa tool, jadi AFC dimatikan agar tidak muncul peringatan di log
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        raw = resp.text or ""
    except Exception:
        log.exception("Panggilan Gemini gagal")
        return None

    try:
        data = _urai(raw)
        label = data["label"]
        confidence = float(data["confidence"])
        penjelasan = str(data["penjelasan"]).strip()
        nomor = data.get("sumber_rujukan") or []
    except (ValueError, KeyError, TypeError):
        log.error("Balasan Gemini gagal diurai: %r", raw)
        return None
    if label not in VALID_LABELS or not 0.0 <= confidence <= 1.0 or not penjelasan:
        log.error("Balasan Gemini tidak valid: %r", raw)
        return None

    # Nomor yang tidak ada di daftar rujukan dibuang, jadi sumber karangan tidak lolos.
    sumber = [rujukan[n - 1] for n in nomor
              if isinstance(n, int) and 1 <= n <= len(rujukan)]
    return {"label": label, "confidence": confidence,
            "penjelasan": penjelasan, "sumber_rujukan": sumber}
