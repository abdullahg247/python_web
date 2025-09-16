def test_devices_endpoint_returns_json(client):
    resp = client.get("/devices?n=3&seed=42")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert all("name" in d and "status" in d for d in data)

def test_devices_endpoint_invalid_n(client):
    resp = client.get("/devices?n=zero")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
