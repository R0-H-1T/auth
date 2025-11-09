from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_home():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"hello": "world"}
