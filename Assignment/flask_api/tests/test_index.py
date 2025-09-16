# assignment/flask_api/tests/test_index.py
from urllib.parse import urlparse

def _norm_endpoint(ep: str) -> str:
    """Convert absolute or relative endpoint into a normalized relative path."""
    p = urlparse(ep)
    path = p.path if p.scheme else ep  # absolute -> path; relative -> keep
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path

def test_api_index_lists_expected_routes(client):
    resp = client.get("/")
    assert resp.status_code == 200 and resp.is_json
    data = resp.get_json()
    assert "routes" in data and isinstance(data["routes"], list)

    index = {
        _norm_endpoint(item["endpoint"]): {m.upper() for m in item["methods"]}
        for item in data["routes"]
    }

    expected = {"/", "/devices", "/health", "/dashboard", "/realtime-dashboard"}
    for ep in expected:
        assert ep in index, f"Missing {ep} in API index"
        assert "GET" in index[ep], f"{ep} should allow GET"
