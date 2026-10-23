import json
import logging
import re
import time

import requests
from google import genai
from google.genai import errors, types

from app.config import settings
from app.services import gemini_video, llm_check
from app.services.scraper import HEADERS, TIMEOUT, ScrapeError, _check_url

log = logging.getLogger(__name__)

# Sama dengan analyzer.VALID_LABELS. Disalin agar analyzer nanti bisa
# meng-import modul ini tanpa import melingkar.
VALID_LABELS = {"hoax", "fakta", "tidak_pasti"}
MAX_TEKS = 20_000  # karakter; artikel lebih panjang dipotong agar hemat kuota
TIMEOUT_MS = 30_000
MAX_GAMBAR = 7 * 1024 * 1024  # batas aman di bawah batas request inline Gemini
# Format gambar yang diterima Gemini. Format lain (svg, gif, avif) dilewati.
MIME_GAMBAR = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
# ponytail: retry 503 sederhana untuk AI-03; AI-08 menggantinya dengan backoff 2-4-8 dan 429
RETRY_503 = 3
JEDA_503 = 2

PROMPT = """Kamu adalah pemeriksa fakta untuk berita berbahasa Indonesia.
Nilai apakah klaim utama pada ARTIKEL di bawah ini hoax, fakta, atau tidak_pasti.
Dasarkan penilaianmu hanya pada RUJUKAN dan pada MEDIA yang dilampirkan. Jangan
memakai ingatanmu sendiri untuk memutuskan benar atau salah, dan dilarang
menyebut sumber yang tidak ada di daftar RUJUKAN. RUJUKAN dicari berdasarkan
kemiripan kata, jadi bisa membahas kejadian lain yang hanya mirip (tokoh,
waktu, atau peristiwanya berbeda). Abaikan rujukan seperti itu dan jangan
cantumkan nomornya. Bila bahan tidak cukup untuk memutuskan, jawab tidak_pasti
dan jelaskan alasannya.

[ARTIKEL]
{teks}

[HASIL CLASSIFIER]
{classifier}

[MEDIA YANG DILAMPIRKAN]
{media}

[RUJUKAN]
{rujukan}

[FORMAT JAWABAN]
Jawab hanya dengan JSON berikut, tanpa teks lain.
{{"label": "hoax" atau "fakta" atau "tidak_pasti",
 "confidence": angka 0 sampai 1,
 "penjelasan": "2 sampai 4 kalimat Bahasa Indonesia yang menyebut klaim spesifik dan isi gambar atau video bila ada",
 "sumber_rujukan": [nomor rujukan yang benar-benar dipakai]}}"""

MEDIA_GAMBAR = (
    "1 gambar utama artikel (dilampirkan). Nilai apakah peristiwa, tempat, dan waktu "
    "yang terlihat di gambar cocok dengan klaim artikel, dan sebutkan bila terlihat "
    "tanda suntingan. Sebut isi gambar secara spesifik di penjelasan."
)
MEDIA_VIDEO = (
    "1 video dari halaman artikel (dilampirkan). Nilai apakah kejadian di video cocok "
    "dengan klaim artikel, dan sebutkan bila video tampak dipotong dari konteksnya atau "
    "hasil rekayasa. Sebut isi video secara spesifik di penjelasan."
)


def _format_classifier(c: dict | None) -> str:
    if not c:
        return "Tidak tersedia."
    return (f"IndoBERT menilai teks ini {c['label']} dengan keyakinan "
            f"{c['confidence']:.0%}. Anggap ini petunjuk tambahan, bukan putusan.")


def _format_rujukan(rujukan: list[dict]) -> str:
    if not rujukan:
        return "Tidak ada rujukan yang cukup mirip."
    return "\n".join(
        f"{i}. {r['judul']} | {r.get('tanggal', 'tanggal tidak diketahui')} | "
        f"{r['ringkasan']} | {r['link']}"
        for i, r in enumerate(rujukan, 1)
    )


def _urai(raw: str) -> dict:
    # Buang pagar blok kode di awal dan akhir balasan sebelum json.loads
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))


def unduh_gambar(url: str) -> types.Part | None:
    """Download gambar lalu bentuk Part inline untuk Gemini, atau None bila gagal.

    Kegagalan di sini tidak menggagalkan penilaian; artikel tetap dinilai dari teks.
    """
    try:
        _check_url(url)  # tolak alamat internal, sama seperti scraper
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except (ScrapeError, requests.RequestException) as e:
        log.warning("Gambar %s gagal di-download: %s", url, e)
        return None
    mime = resp.headers.get("content-type", "").split(";")[0].strip().lower()
    if resp.status_code >= 400:
        log.warning("Gambar %s ditolak server (HTTP %s)", url, resp.status_code)
        return None
    if mime not in MIME_GAMBAR:
        log.warning("Gambar %s dilewati, format %r tidak didukung", url, mime)
        return None
    if len(resp.content) > MAX_GAMBAR:
        log.warning("Gambar %s dilewati, ukurannya %s byte", url, len(resp.content))
        return None
    return types.Part.from_bytes(data=resp.content, mime_type=mime)


def _generate(client, contents):
    for percobaan in range(1, RETRY_503 + 1):
        try:
            return client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    # Tanpa tool, jadi AFC dimatikan agar tidak muncul peringatan di log
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        except errors.APIError as e:
            if e.code != 503 or percobaan == RETRY_503:
                raise
            log.warning("Gemini 503, percobaan %s dari %s, ulangi %s detik lagi",
                        percobaan, RETRY_503, JEDA_503)
            time.sleep(JEDA_503)


def _nilai_dengan_video(client, kirim, video_url: str) -> str | None:
    """Coba nilai artikel bersama video. Kembalikan teks balasan, atau None bila
    video tidak bisa dipakai sehingga pemanggil menilai tanpa video."""
    if not gemini_video.video_layak(video_url):
        return None
    yt = gemini_video.youtube_watch(video_url)
    if yt:
        # Jalur 1: link YouTube langsung, tanpa download
        try:
            return kirim(types.Part(file_data=types.FileData(file_uri=yt)))
        except errors.ClientError as e:
            log.warning("Link YouTube langsung ditolak (%s), coba lewat Files API", e.code)
    # Jalur 2: download lalu upload ke Files API; file selalu dihapus setelahnya
    try:
        with gemini_video.upload_video(client, video_url) as berkas:
            return kirim(berkas)
    except Exception:
        log.exception("Video %s gagal diproses, artikel dinilai tanpa video", video_url)
        return None


def verifikasi(teks: str, classifier: dict | None = None,
               rujukan: list[dict] | None = None,
               gambar_url: str | None = None,
               video_url: str | None = None) -> dict | None:
    """Nilai artikel lewat Gemini, dengan gambar utama dan satu video bila ada.

    classifier: {"label": ..., "confidence": ...} dari IndoBERT, boleh None.
    rujukan: list dict berisi judul, ringkasan, link (keluaran AI-05), boleh None.
    gambar_url: Article.top_image, boleh None.
    video_url: salah satu Article.video_urls, boleh None.

    Kembalikan {label, confidence, penjelasan, sumber_rujukan, modalitas_dinilai},
    atau None bila Gemini tidak tersedia, panggilan gagal, atau balasan tidak valid.
    Gambar atau video yang gagal diproses dilewati; artikel tetap dinilai.
    """
    if not llm_check.LLM_TERSEDIA:
        return None
    rujukan = rujukan or []
    gambar = unduh_gambar(gambar_url) if gambar_url else None

    def kirim(video=None) -> str:
        media = [m for m, ada in ((MEDIA_GAMBAR, gambar), (MEDIA_VIDEO, video)) if ada]
        prompt = PROMPT.format(
            teks=teks[:MAX_TEKS],
            classifier=_format_classifier(classifier),
            media="\n".join(media) or "Tidak ada.",
            rujukan=_format_rujukan(rujukan),
        )
        contents = [p for p in (gambar, video) if p] + [prompt]
        return _generate(client, contents if len(contents) > 1 else prompt).text or ""

    try:
        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=TIMEOUT_MS),
        )
        raw = _nilai_dengan_video(client, kirim, video_url) if video_url else None
        ada_video = raw is not None
        if raw is None:
            raw = kirim()
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
    return {
        "label": label,
        "confidence": confidence,
        "penjelasan": penjelasan,
        "sumber_rujukan": sumber,
        "modalitas_dinilai": ["teks"] + (["gambar"] if gambar else []) + (["video"] if ada_video else []),
    }
