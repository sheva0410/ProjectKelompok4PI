import hashlib
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS = {
    "fbclid", "gclid", "dclid", "msclkid", "yclid",
    "igshid", "mc_cid", "mc_eid", "_ga",
}


def normalize_url(url: str) -> str:
    p = urlparse(url.strip())
    scheme = p.scheme.lower()
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]

    port = p.port
    if port and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        host = f"{host}:{port}"

    path = p.path or "/"
    if len(path) > 1:
        path = path.rstrip("/")

    pairs = [
        (k, v)
        for k, v in parse_qsl(p.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in TRACKING_PARAMS
    ]
    pairs.sort()

    return urlunparse((scheme, host, path, "", urlencode(pairs), ""))


def hash_url(normalized_url: str) -> str:
    return hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()