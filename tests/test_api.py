from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_assist_api():
    client = TestClient(app)
    res = client.post("/api/assist", json={"question": "包裹显示签收但用户没收到", "scenario": "ecommerce_support"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["citations"]
