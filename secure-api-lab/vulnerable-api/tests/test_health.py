"""Health endpoint tests."""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert data["application"] == "vulnerable-api"


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"

