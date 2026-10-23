"""Uji manual AI-06: jalankan analyze() asli (IndoBERT, gerbang, RAG, Gemini) pada link berita.

Jalankan dari folder hoaxscan-backend:
    python -m scripts.test_analyze URL1 URL2 ...
Opsi --tanpa-media membuang gambar dan video hasil scraping, untuk menguji lapis 2
(hanya skor IndoBERT yang menentukan apakah Gemini dipanggil).
Keputusan gerbang tercetak sebagai baris log "Gerbang: ...".
"""
import logging
import sys

from app.services import llm_check
from app.services.analyzer import AnalysisError, analyze
from app.services.scraper import ScrapeError, extract_article

logging.basicConfig(level=logging.WARNING)
logging.getLogger("app.services.analyzer").setLevel(logging.INFO)

tanpa_media = "--tanpa-media" in sys.argv
urls = [a for a in sys.argv[1:] if not a.startswith("--")]
if not urls:
    sys.exit(__doc__)

print("LLM_TERSEDIA =", llm_check.cek_gemini())
for i, url in enumerate(urls, 1):
    try:
        artikel = extract_article(url)
        if tanpa_media:
            artikel.top_image, artikel.video_urls = None, []
        out = analyze(artikel)
    except (ScrapeError, AnalysisError) as e:
        print(f"{i}. GAGAL {url}: {e}")
        continue
    print(f"{i}. {artikel.title}\n   {out.label} {out.confidence} {out.modalitas_dinilai}"
          f"\n   {out.explanation}")
    for s in out.sources:
        print("   Sumber:", s["url"])
