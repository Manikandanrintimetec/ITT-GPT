from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_invalid_route():

    response = client.get("/invalid")

    assert response.status_code == 404


def test_missing_required_fields():

    response = client.post(
        "/conversations",
        json={}
    )

    assert response.status_code == 422