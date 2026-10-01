import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
import trafilatura

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HoaxScanBot/1.0)"}
TIMEOUT = 10
MAX_BYTES = 5 * 1024 * 1024
MIN_TEXT_LEN = 200


class ScrapeError(Exception):
    """Gagal mengambil atau membaca artikel."""


@dataclass
class Article:
    title: str | None
    text: str


def _check_url(url: str) -> None:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise ScrapeError("URL harus diawali http:// atau https://")
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        raise ScrapeError("Domain tidak ditemukan")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ScrapeError("Alamat URL tidak diizinkan")


def fetch_html(url: str) -> str:
    _check_url(url)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.Timeout:
        raise ScrapeError("Situs terlalu lama merespons")
    except requests.RequestException:
        raise ScrapeError("Gagal mengakses URL")

    if resp.status_code >= 400:
        raise ScrapeError(f"Situs menolak akses (HTTP {resp.status_code})")
    if "html" not in resp.headers.get("content-type", ""):
        raise ScrapeError("URL bukan halaman web")
    if len(resp.content) > MAX_BYTES:
        raise ScrapeError("Halaman terlalu besar")

    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    return resp.text


def extract_article(url: str) -> Article:
    html = fetch_html(url)
    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not text or len(text) < MIN_TEXT_LEN:
        raise ScrapeError(
            "Isi artikel tidak ditemukan (halaman kosong, terkunci, atau butuh login)"
        )
    meta = trafilatura.extract_metadata(html)
    title = meta.title if meta and meta.title else None
    return Article(title=title, text=text)