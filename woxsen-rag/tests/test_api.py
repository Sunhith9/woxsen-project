from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data

def test_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_docs_list():
    response = client.get("/docs-list")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "total_chunks" in data

def test_chat():
    response = client.post("/chat", json={"message": "What are the library timings?"})
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "answer" in data
    assert len(data["answer"]) > 0
