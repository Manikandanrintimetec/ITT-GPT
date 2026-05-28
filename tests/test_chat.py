from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200


def test_invalid_conversation():

    response = client.get(
        "/conversations/99999"
    )

    assert response.status_code == 404