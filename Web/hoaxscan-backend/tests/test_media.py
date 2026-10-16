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


def test_gambar_utama_dari_og_image_dan_jadi_url_penuh():
    img, _ = find_media(HTML, "https://contoh.com/berita/1")
    assert img == "https://contoh.com/img/cover.jpg"


def test_video_dikumpulkan_tanpa_duplikat_dan_tanpa_iframe_asing():
    _, vids = find_media(HTML, "https://contoh.com/berita/1")
    assert vids == [
        "https://cdn.contoh.com/v.mp4",
        "https://contoh.com/media/clip.webm",
        "https://www.youtube.com/embed/abc123",
    ]


def test_maksimal_tiga_video():
    html = "<html><body>" + "".join(
        f'<video src="/v{i}.mp4"></video>' for i in range(6)
    ) + "</body></html>"
    _, vids = find_media(html, "https://contoh.com")
    assert len(vids) == 3


def test_gambar_data_uri_diabaikan():
    html = '<html><body><article><img src="data:image/gif;base64,R0lGOD"></article></body></html>'
    img, _ = find_media(html, "https://contoh.com")
    assert img is None


def test_halaman_tanpa_media():
    assert find_media("<html><body><p>teks saja</p></body></html>", "https://contoh.com") == (None, [])


def test_html_kosong_tidak_error():
    assert find_media("", "https://contoh.com") == (None, [])