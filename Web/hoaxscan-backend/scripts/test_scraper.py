import sys

from app.services.scraper import ScrapeError, extract_article

url = sys.argv[1]
try:
    a = extract_article(url)
    print("JUDUL:", a.title)
    print("PANJANG TEKS:", len(a.text))
    print("TOP IMAGE:", a.top_image)
    print("VIDEO:", a.video_urls)
except ScrapeError as e:
    print("GAGAL:", e)