"""IDOR / Broken Object-Level Authorization tests.

These tests demonstrate the intentional BOLA/IDOR vulnerability in the
vulnerable API.  Every test in this module is *expected to pass* against
the vulnerable implementation — that is the point.

    Expected secure behavior → 403 Forbidden
    Actual vulnerable behavior → 200 OK

A secure implementation would enforce object-level authorization:

    if current_user.id != requested_user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

Affected endpoint:
    GET   /api/v1/users/{user_id}
    PATCH /api/v1/users/{user_id}
"""

USER_A = {
    "email": "alice@example.com",
    "password": "alice-password-123",
    "full_name": "Alice Anderson",
}

USER_B = {
    "email": "bob@example.com",
    "password": "bob-password-456",
    "full_name": "Bob Baker",
}


def _register(client, user: dict) -> dict:
    resp = client.post("/api/v1/auth/register", json=user)
    assert resp.status_code == 201
    return resp.json()


def _get_user_id(client, token: str) -> int:
    resp = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    return resp.json()["id"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestIDOR:
    """Broken Object-Level Authorization (BOLA/IDOR) vulnerability tests."""

    def test_user_can_access_another_users_profile_idor(self, client):
        """Demonstrate IDOR: User A reads User B's profile.

        Expected secure behavior:
            HTTP 403 Forbidden

        Actual vulnerable behavior:
            HTTP 200 OK — User B's profile is returned.

        This test intentionally passes against the vulnerable
        implementation to prove the flaw exists.
        """
        # 1. Register both users
        token_a = _register(client, USER_A)["access_token"]
        token_b = _register(client, USER_B)["access_token"]

        # 2. Discover User B's ID
        user_b_id = _get_user_id(client, token_b)

        # 3. User A requests User B's profile
        resp = client.get(
            f"/api/v1/users/{user_b_id}",
            headers=_auth_header(token_a),
        )

        # 4. VULNERABLE: Returns 200 with User B's data
        assert resp.status_code == 200, (
            "Expected 200 (vulnerable behavior). "
            "A secure API would return 403."
        )
        data = resp.json()
        assert data["email"] == USER_B["email"]
        assert data["full_name"] == USER_B["full_name"]
        # Verify no credentials are leaked
        assert "password" not in data

    def test_user_can_modify_another_users_profile_idor(self, client):
        """Demonstrate IDOR: User A modifies User B's profile.

        Expected secure behavior:
            HTTP 403 Forbidden

        Actual vulnerable behavior:
            HTTP 200 OK — User B's profile is updated by User A.
        """
        token_a = _register(client, USER_A)["access_token"]
        token_b = _register(client, USER_B)["access_token"]
        user_b_id = _get_user_id(client, token_b)

        # User A changes User B's name
        resp = client.patch(
            f"/api/v1/users/{user_b_id}",
            json={"full_name": "Hacked By Alice"},
            headers=_auth_header(token_a),
        )

        assert resp.status_code == 200, (
            "Expected 200 (vulnerable behavior). "
            "A secure API would return 403."
        )
        assert resp.json()["full_name"] == "Hacked By Alice"

    def test_own_profile_access_works(self, client):
        """Baseline: A user can access their own profile (this is always valid)."""
        token_a = _register(client, USER_A)["access_token"]
        user_a_id = _get_user_id(client, token_a)

        resp = client.get(
            f"/api/v1/users/{user_a_id}",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == USER_A["email"]

    def test_nonexistent_user_returns_404(self, client):
        """Requesting a non-existent user returns 404, not a data leak."""
        token_a = _register(client, USER_A)["access_token"]

        resp = client.get(
            "/api/v1/users/99999",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 404

