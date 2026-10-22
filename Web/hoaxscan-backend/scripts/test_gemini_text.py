"""Uji manual AI-02: scrape beberapa link berita, lalu nilai teksnya lewat Gemini.

Jalankan dari folder hoaxscan-backend:
    python -m scripts.test_gemini_text URL1 URL2 URL3 URL4 URL5
"""
import logging
import sys

from app.services import llm_check
from app.services.gemini_verifier import verifikasi_teks
from app.services.scraper import ScrapeError, extract_article

logging.basicConfig(level=logging.WARNING)

urls = sys.argv[1:]
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
    hasil = verifikasi_teks(artikel.text)
    print(f"{i}. {artikel.title}\n   {hasil}")
    terurai += hasil is not None
print(f"\n{terurai}/{len(urls)} balasan terurai")
