"""Health check tests — verifies the API is running and connected to the database."""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_reports_database(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"

