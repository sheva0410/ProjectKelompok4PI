import socket

import pytest
import requests

from app.services import scraper
from app.services.scraper import ScrapeError, _check_url, extract_article, fetch_html

IP_PUBLIK = "93.184.216.34"


def _dns(ip):
    def palsu(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    return palsu


class ResponPalsu:
    def __init__(self, status=200, content_type="text/html", body="", url="https://contoh.com/a"):
        self.status_code = status
        self.headers = {"content-type": content_type}
        self.content = body.encode("utf-8")
        self.text = body
        self.url = url
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"


@pytest.fixture
def dns_publik(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _dns(IP_PUBLIK))


# --- _check_url: pengaman -------------------------------------------------

@pytest.mark.parametrize("url", ["ftp://contoh.com/file", "file:///etc/passwd", "contoh.com", "http://"])
def test_skema_selain_http_ditolak(url):
    with pytest.raises(ScrapeError, match="http:// atau https://"):
        _check_url(url)


@pytest.mark.parametrize(
    "ip",
    ["127.0.0.1", "10.0.0.5", "192.168.1.10", "172.16.0.1", "169.254.169.254"],
)
def test_alamat_internal_ditolak(monkeypatch, ip):
    monkeypatch.setattr(socket, "getaddrinfo", _dns(ip))
    with pytest.raises(ScrapeError, match="Alamat URL tidak diizinkan"):
        _check_url("http://apa-saja.contoh.com/x")


def test_domain_tidak_ada(monkeypatch):
    def gagal(*a, **k):
        raise socket.gaierror()

    monkeypatch.setattr(socket, "getaddrinfo", gagal)
    with pytest.raises(ScrapeError, match="Domain tidak ditemukan"):
        _check_url("https://domain-tidak-ada.contoh.com/a")


def test_alamat_publik_lolos(dns_publik):
    _check_url("https://contoh.com/a")


# --- fetch_html: tanpa internet, requests dipalsukan -------------------------

def test_http_404_ditolak(dns_publik, monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: ResponPalsu(status=404))
    with pytest.raises(ScrapeError, match=r"HTTP 404"):
        fetch_html("https://contoh.com/a")


def test_bukan_html_ditolak(dns_publik, monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: ResponPalsu(content_type="image/png")
    )
    with pytest.raises(ScrapeError, match="bukan halaman web"):
        fetch_html("https://contoh.com/logo.png")


def test_timeout(dns_publik, monkeypatch):
    def lambat(*a, **k):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", lambda *a, **k: lambat())
    with pytest.raises(ScrapeError, match="terlalu lama"):
        fetch_html("https://contoh.com/a")


def test_gagal_koneksi(dns_publik, monkeypatch):
    def putus(*a, **k):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "get", lambda *a, **k: putus())
    with pytest.raises(ScrapeError, match="Gagal mengakses"):
        fetch_html("https://contoh.com/a")


def test_halaman_terlalu_besar(dns_publik, monkeypatch):
    monkeypatch.setattr(scraper, "MAX_BYTES", 10)
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: ResponPalsu(body="x" * 100)
    )
    with pytest.raises(ScrapeError, match="terlalu besar"):
        fetch_html("https://contoh.com/a")


# --- extract_article --------------------------------------------------------

ARTIKEL = """
<html><head><title>Judul Berita Uji</title>
<meta property="og:image" content="/img/cover.jpg"></head>
<body><nav>Menu Beranda Populer</nav><article>
<h1>Judul Berita Uji</h1>
""" + "".join(
    f"<p>Paragraf nomor {i} berisi kalimat yang cukup panjang supaya mesin ekstraksi "
    f"menganggapnya isi artikel sungguhan dan bukan sekadar menu atau iklan.</p>"
    for i in range(1, 8)
) + "</article><footer>Hak cipta</footer></body></html>"


def test_extract_article_berhasil(dns_publik, monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: ResponPalsu(body=ARTIKEL, url="https://contoh.com/a")
    )
    a = extract_article("https://contoh.com/a")
    assert len(a.text) >= 200
    assert "Paragraf nomor 3" in a.text
    assert a.top_image == "https://contoh.com/img/cover.jpg"
    assert a.video_urls == []


def test_halaman_tanpa_isi_ditolak(dns_publik, monkeypatch):
    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: ResponPalsu(body="<html><body><p>pendek</p></body></html>"),
    )
    with pytest.raises(ScrapeError, match="Isi artikel tidak ditemukan"):
        extract_article("https://contoh.com/a")