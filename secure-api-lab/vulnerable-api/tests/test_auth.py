"""Authentication tests — registration, login, and token-based access."""

import pytest


USER_A = {
    "email": "alice@example.com",
    "password": "alice-password-123",
    "full_name": "Alice Anderson",
}


def _register(client, user: dict) -> dict:
    resp = client.post("/api/v1/auth/register", json=user)
    assert resp.status_code == 201
    return resp.json()


def _login(client, email: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegistration:

    def test_register_success(self, client):
        data = _register(client, USER_A)
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        _register(client, USER_A)
        resp = client.post("/api/v1/auth/register", json=USER_A)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:

    def test_login_success(self, client):
        _register(client, USER_A)
        data = _login(client, USER_A["email"], USER_A["password"])
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        _register(client, USER_A)
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": USER_A["email"], "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "any"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Authenticated access
# ---------------------------------------------------------------------------

class TestAuthenticatedAccess:

    def test_get_me(self, client):
        token = _register(client, USER_A)["access_token"]
        resp = client.get("/api/v1/users/me", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == USER_A["email"]
        assert data["full_name"] == USER_A["full_name"]
        assert "password" not in data

    def test_unauthenticated_access_rejected(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code in (401, 403)

    def test_invalid_token_rejected(self, client):
        resp = client.get(
            "/api/v1/users/me",
            headers=_auth_header("invalid.token.value"),
        )
        assert resp.status_code == 401

