from app.services.media import find_media

HTML = """
<html><head>
<meta property="og:image" content="/img/cover.jpg">
<meta property="og:video" content="https://cdn.contoh.com/v.mp4">
</head><body><article>
<iframe src="https://www.youtube.com/embed/abc123"></iframe>
<iframe src="https://www.youtube.com/embed/abc123"></iframe>
<iframe src="https://www.facebook.com/plugins/like.php"></iframe>
<video><source src="/media/clip.webm"></video>
<img src="data:image/gif;base64,R0lGOD">
</article></body></html>
"""

img, vids = find_media(HTML, "https://contoh.com/berita/1")
print("IMAGE:", img)
print("VIDEOS:", vids)

print("KOSONG:", find_media("<html><body><p>teks saja</p></body></html>", "https://contoh.com"))
print("RUSAK:", find_media("", "https://contoh.com"))