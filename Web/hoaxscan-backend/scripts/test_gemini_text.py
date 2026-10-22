"""Uji manual AI-02 dan AI-03: scrape link berita, lalu nilai teks dan gambar
utamanya lewat Gemini.

Jalankan dari folder hoaxscan-backend:
    python -m scripts.test_gemini_text URL1 URL2 URL3 URL4 URL5
Tambahkan --tanpa-gambar untuk menilai teksnya saja.
"""
import logging
import sys

from app.services import llm_check
from app.services.gemini_verifier import verifikasi
from app.services.scraper import ScrapeError, extract_article

logging.basicConfig(level=logging.WARNING)

pakai_gambar = "--tanpa-gambar" not in sys.argv
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
    hasil = verifikasi(artikel.text, gambar_url=gambar)
    print(f"{i}. {artikel.title}\n   gambar: {gambar}\n   {hasil}")
    terurai += hasil is not None
print(f"\n{terurai}/{len(urls)} balasan terurai")
