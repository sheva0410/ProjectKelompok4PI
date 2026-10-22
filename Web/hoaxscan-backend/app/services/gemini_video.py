"""Persiapan video untuk Gemini (AI-04).

Dua jalur:
1. Link YouTube dikirim langsung ke Gemini sebagai file_uri, tanpa download.
2. Video lain di-download kualitas rendah dengan yt-dlp, di-upload ke Files API,
   lalu file lokal dan salinan di Google selalu dihapus setelah dipakai.
"""
import logging
import os
import re
import tempfile
import time
from contextlib import contextmanager

import yt_dlp

from app.services.scraper import ScrapeError, _check_url

log = logging.getLogger(__name__)

MAX_DURASI = 180  # detik; video lebih panjang dilewati agar token tidak meledak
MAX_UKURAN = 50 * 1024 * 1024  # byte
TUNGGU_AKTIF = 120  # detik menunggu Files API selesai memproses video
JEDA_CEK = 3  # detik antar pengecekan status file

_YOUTUBE = re.compile(
    r"(?:youtube(?:-nocookie)?\.com/(?:embed/|shorts/|watch\?(?:.*&)?v=)|youtu\.be/)([\w-]{11})"
)
_YDL_DASAR = {"quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True}


def youtube_watch(url: str) -> str | None:
    """Ubah link YouTube (embed, shorts, youtu.be) jadi bentuk watch?v=, atau None."""
    m = _YOUTUBE.search(url)
    return f"https://www.youtube.com/watch?v={m.group(1)}" if m else None


def video_layak(url: str) -> bool:
    """Cek alamat dan durasi tanpa download. False bila video sebaiknya dilewati."""
    try:
        _check_url(url)  # tolak alamat internal, sama seperti scraper
        with yt_dlp.YoutubeDL(_YDL_DASAR) as ydl:
            info = ydl.extract_info(url, download=False)
    except (ScrapeError, yt_dlp.utils.DownloadError) as e:
        log.warning("Video %s tidak bisa dibaca: %s", url, e)
        return False
    durasi = info.get("duration")
    if durasi and durasi > MAX_DURASI:
        log.warning("Video %s dilewati, durasinya %s detik (batas %s)", url, durasi, MAX_DURASI)
        return False
    return True


def _download(url: str, folder: str) -> str:
    opsi = {
        **_YDL_DASAR,
        # Format gabungan video+audio kualitas terendah, supaya file kecil dan upload cepat
        "format": "worst[ext=mp4]/worst",
        "outtmpl": os.path.join(folder, "video.%(ext)s"),
        "max_filesize": MAX_UKURAN,
    }
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=True)
    unduhan = info.get("requested_downloads") or []
    path = unduhan[0].get("filepath") if unduhan else None
    if not path or not os.path.exists(path):
        raise RuntimeError(f"Video tidak ter-download (mungkin lebih dari {MAX_UKURAN} byte)")
    return path


@contextmanager
def upload_video(client, url: str):
    """Download video, upload ke Files API, lalu yield file yang sudah ACTIVE.

    File lokal (folder sementara) dan salinan di Files API selalu dihapus saat
    keluar dari blok with, baik penilaian berhasil maupun gagal di tengah jalan.
    Tanpa ini salinan di Google bertahan sampai 48 jam.
    """
    berkas = None
    with tempfile.TemporaryDirectory(prefix="hoaxscan_video_") as folder:
        try:
            berkas = client.files.upload(file=_download(url, folder))
            batas = time.monotonic() + TUNGGU_AKTIF
            while berkas.state.name == "PROCESSING":
                if time.monotonic() > batas:
                    raise TimeoutError(f"Video belum siap setelah {TUNGGU_AKTIF} detik")
                time.sleep(JEDA_CEK)
                berkas = client.files.get(name=berkas.name)
            if berkas.state.name != "ACTIVE":
                raise RuntimeError(f"Files API menolak video (status {berkas.state.name})")
            yield berkas
        finally:
            if berkas is not None:
                try:
                    client.files.delete(name=berkas.name)
                except Exception:
                    log.exception("Gagal menghapus %s dari Files API", berkas.name)
