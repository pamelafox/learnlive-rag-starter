import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_do_rag(monkeypatch):
    async def mock_response(messages):
        return {"answer": "This is a mock response"}
    monkeypatch.setattr("main.do_rag", mock_response)

def test_query_success(mock_do_rag):
    response = client.post("/chat", json={
        "messages": [
            {"content": "Hello, how are you?", "role": "user"}
        ]
    })
    assert response.status_code == 200
    assert response.json() == {"answer": "This is a mock response"}

def test_query_failure(mock_do_rag):
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Unprocessable Entity due to validation error