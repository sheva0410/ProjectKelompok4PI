from urllib.parse import urljoin, urlparse

from lxml import html as lxml_html

MAX_VIDEOS = 3
IMAGE_META = (
    "og:image", "og:image:url", "og:image:secure_url",
    "twitter:image", "twitter:image:src",
)
VIDEO_META = ("og:video", "og:video:url", "og:video:secure_url")
EMBED_HOSTS = ("youtube.com", "youtube-nocookie.com", "vimeo.com", "dailymotion.com")


def _parse(html: str):
    try:
        parser = lxml_html.HTMLParser(encoding="utf-8")
        return lxml_html.fromstring(html.encode("utf-8"), parser=parser)
    except Exception:
        return None


def _meta(tree, names):
    for name in names:
        for el in tree.xpath("//meta[@property=$n or @name=$n]", n=name):
            content = (el.get("content") or "").strip()
            if content:
                yield content


def _absolute(base: str, link: str | None) -> str | None:
    if not link:
        return None
    full = urljoin(base, link.strip())
    p = urlparse(full)
    if p.scheme in ("http", "https") and p.hostname:
        return full
    return None


def _is_embed(url: str) -> bool:
    p = urlparse(url)
    host = (p.hostname or "").lower()
    for h in EMBED_HOSTS:
        if host == h or host.endswith("." + h):
            if h.startswith("youtube"):
                return p.path.startswith("/embed/")
            return True
    return False


def find_top_image(tree, base: str) -> str | None:
    for link in _meta(tree, IMAGE_META):
        url = _absolute(base, link)
        if url:
            return url
    for el in tree.xpath("//link[@rel='image_src']"):
        url = _absolute(base, el.get("href"))
        if url:
            return url
    for el in tree.xpath("//article//img[@src]"):
        url = _absolute(base, el.get("src"))
        if url:
            return url
    return None


def find_videos(tree, base: str) -> list[str]:
    found: list[str] = []

    def add(link):
        url = _absolute(base, link)
        if url and url not in found:
            found.append(url)

    for link in _meta(tree, VIDEO_META):
        add(link)
    for el in tree.xpath("//video[@src] | //video/source[@src]"):
        add(el.get("src"))
    for el in tree.xpath("//iframe[@src]"):
        url = _absolute(base, el.get("src"))
        if url and _is_embed(url):
            add(url)
    return found[:MAX_VIDEOS]


def find_media(html: str, base_url: str) -> tuple[str | None, list[str]]:
    tree = _parse(html)
    if tree is None:
        return None, []
    return find_top_image(tree, base_url), find_videos(tree, base_url)