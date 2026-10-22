import os
from types import SimpleNamespace

import pytest

from app.services import gemini_video as gvid
from app.services.scraper import ScrapeError


# --- youtube_watch ----------------------------------------------------------

@pytest.mark.parametrize("url", [
    "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1",
    "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
])
def test_youtube_watch_dikenali(url):
    assert gvid.youtube_watch(url) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_bukan_youtube():
    assert gvid.youtube_watch("https://20.detik.com/embed/261015043") is None


# --- video_layak ------------------------------------------------------------

def _ydl_palsu(monkeypatch, info=None, error=None, tulis_file=True):
    """YoutubeDL palsu. Bila download=True, tulis file kecil ke outtmpl."""

    class Ydl:
        def __init__(self, opsi):
            self.opsi = opsi

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def extract_info(self, url, download=False):
            if error:
                raise error
            hasil = dict(info or {})
            if download and tulis_file:
                path = self.opsi["outtmpl"].replace("%(ext)s", "mp4")
                with open(path, "wb") as f:
                    f.write(b"video")
                hasil["requested_downloads"] = [{"filepath": path}]
            return hasil

    monkeypatch.setattr(gvid.yt_dlp, "YoutubeDL", Ydl)
    monkeypatch.setattr(gvid, "_check_url", lambda url: None)


def test_video_pendek_layak(monkeypatch):
    _ydl_palsu(monkeypatch, {"duration": 60})
    assert gvid.video_layak("https://contoh.id/v") is True


def test_durasi_tidak_diketahui_tetap_layak(monkeypatch):
    _ydl_palsu(monkeypatch, {})
    assert gvid.video_layak("https://contoh.id/v") is True


def test_video_terlalu_panjang(monkeypatch):
    _ydl_palsu(monkeypatch, {"duration": gvid.MAX_DURASI + 1})
    assert gvid.video_layak("https://contoh.id/v") is False


def test_video_tidak_terbaca(monkeypatch):
    _ydl_palsu(monkeypatch, error=gvid.yt_dlp.utils.DownloadError("tidak didukung"))
    assert gvid.video_layak("https://contoh.id/v") is False


def test_video_alamat_internal(monkeypatch):
    _ydl_palsu(monkeypatch, {"duration": 10})

    def tolak(url):
        raise ScrapeError("Alamat URL tidak diizinkan")

    monkeypatch.setattr(gvid, "_check_url", tolak)
    assert gvid.video_layak("http://127.0.0.1/v") is False


# --- upload_video: file lokal dan Files API selalu dibersihkan ---------------

class _Files:
    def __init__(self, status_akhir="ACTIVE"):
        self.status_akhir = status_akhir
        self.diupload = None
        self.dihapus = []

    def upload(self, file):
        self.diupload = file
        assert os.path.exists(file)
        return SimpleNamespace(name="files/abc", state=SimpleNamespace(name="PROCESSING"))

    def get(self, name):
        return SimpleNamespace(name=name, state=SimpleNamespace(name=self.status_akhir))

    def delete(self, name):
        self.dihapus.append(name)


def _client(files):
    return SimpleNamespace(files=files)


def test_upload_berhasil_lalu_dibersihkan(monkeypatch):
    _ydl_palsu(monkeypatch)
    monkeypatch.setattr(gvid.time, "sleep", lambda s: None)
    files = _Files()
    with gvid.upload_video(_client(files), "https://contoh.id/v") as berkas:
        assert berkas.state.name == "ACTIVE"
    assert files.dihapus == ["files/abc"]
    assert not os.path.exists(files.diupload)


def test_gagal_di_tengah_tetap_dibersihkan(monkeypatch):
    _ydl_palsu(monkeypatch)
    monkeypatch.setattr(gvid.time, "sleep", lambda s: None)
    files = _Files()
    with pytest.raises(RuntimeError):
        with gvid.upload_video(_client(files), "https://contoh.id/v"):
            raise RuntimeError("Gemini gagal")
    assert files.dihapus == ["files/abc"]
    assert not os.path.exists(files.diupload)


def test_status_failed_ditolak_dan_dibersihkan(monkeypatch):
    _ydl_palsu(monkeypatch)
    monkeypatch.setattr(gvid.time, "sleep", lambda s: None)
    files = _Files(status_akhir="FAILED")
    with pytest.raises(RuntimeError, match="FAILED"):
        with gvid.upload_video(_client(files), "https://contoh.id/v"):
            pass
    assert files.dihapus == ["files/abc"]


def test_download_gagal_tidak_upload(monkeypatch):
    _ydl_palsu(monkeypatch, tulis_file=False)
    files = _Files()
    with pytest.raises(RuntimeError, match="tidak ter-download"):
        with gvid.upload_video(_client(files), "https://contoh.id/v"):
            pass
    assert files.diupload is None and files.dihapus == []
