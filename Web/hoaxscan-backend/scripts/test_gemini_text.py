"""Uji manual AI-02 sampai AI-04: scrape link berita, lalu nilai teks, gambar
utama, dan video pertamanya lewat Gemini.

Jalankan dari folder hoaxscan-backend:
    python -m scripts.test_gemini_text URL1 URL2 ...
Opsi: --tanpa-gambar dan --tanpa-video untuk melewati media tersebut.
Di akhir, skrip memastikan tidak ada video yang tertinggal di Files API.
"""
import logging
import sys

from google import genai

from app.config import settings
from app.services import llm_check
from app.services.gemini_verifier import verifikasi
from app.services.scraper import ScrapeError, extract_article

logging.basicConfig(level=logging.WARNING)

pakai_gambar = "--tanpa-gambar" not in sys.argv
pakai_video = "--tanpa-video" not in sys.argv
urls = [a for a in sys.argv[1:] if not a.startswith("--")]
if not urls:
    sys.exit(__doc__)

print("LLM_TERSEDIA =", llm_check.cek_gemini())
terurai = 0
for i, url in enumerate(urls, 1):
    try:
        artikel = extract_article(url)
    except ScrapeError as e:
        print(f"{i}. SCRAPE GAGAL {url}: {e}")
        continue
    gambar = artikel.top_image if pakai_gambar else None
    video = artikel.video_urls[0] if pakai_video and artikel.video_urls else None
    hasil = verifikasi(artikel.text, gambar_url=gambar, video_url=video)
    print(f"{i}. {artikel.title}\n   gambar: {gambar}\n   video : {video}\n   {hasil}")
    terurai += hasil is not None
print(f"\n{terurai}/{len(urls)} balasan terurai")

client = genai.Client(api_key=settings.gemini_api_key)
sisa = [f.name for f in client.files.list()]
print("Sisa file di Files API:", sisa or "kosong")
