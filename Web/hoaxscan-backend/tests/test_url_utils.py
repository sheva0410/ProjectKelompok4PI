import pytest

from app.services.url_utils import hash_url, normalize_url


@pytest.mark.parametrize(
    "masuk, keluar",
    [
        (
            "HTTPS://WWW.Detik.com/a/?utm_source=x&b=2&a=1#top",
            "https://detik.com/a?a=1&b=2",
        ),
        ("https://detik.com/a/", "https://detik.com/a"),
        ("https://detik.com/a?fbclid=abc", "https://detik.com/a"),
        ("https://detik.com:443/a", "https://detik.com/a"),
        ("http://detik.com:80/a", "http://detik.com/a"),
        ("https://detik.com:8443/a", "https://detik.com:8443/a"),
        ("https://user:pass@detik.com/a", "https://detik.com/a"),
        ("https://detik.com", "https://detik.com/"),
        ("  https://detik.com/a  ", "https://detik.com/a"),
    ],
)
def test_normalize_url(masuk, keluar):
    assert normalize_url(masuk) == keluar


def test_url_berbeda_penulisan_hash_sama():
    a = normalize_url("https://www.detik.com/a?utm_source=x#top")
    b = normalize_url("https://detik.com/a/")
    assert hash_url(a) == hash_url(b)


def test_url_berbeda_hash_berbeda():
    a = normalize_url("https://detik.com/a")
    b = normalize_url("https://detik.com/b")
    assert hash_url(a) != hash_url(b)


def test_hash_panjang_64():
    assert len(hash_url("https://detik.com/a")) == 64