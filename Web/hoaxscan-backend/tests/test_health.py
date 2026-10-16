def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_cors_origin_diizinkan(client):
    r = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_origin_tidak_diizinkan(client):
    r = client.get("/api/health", headers={"Origin": "http://evil.com"})
    assert "access-control-allow-origin" not in r.headers