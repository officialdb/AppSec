"""Functional and security regression tests for user search and SQL injection (VULN-002).

This test module verifies:
1. Legitimate search functionality (normal functional tests).
2. SQL injection regression prevention on the remediated (default) endpoint.
3. Demonstration of VULN-002 SQL injection in isolated lab mode.
"""

import pytest

USER_ALICE = {
    "email": "alice@test.local",
    "password": "alice-password-123",
    "full_name": "Alice",
}

USER_BOB = {
    "email": "bob@test.local",
    "password": "bob-password-456",
    "full_name": "Bob",
}


def _register(client, user: dict) -> dict:
    resp = client.post("/api/v1/auth/register", json=user)
    assert resp.status_code == 201
    return resp.json()


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_token(client):
    """Seed test users Alice and Bob and return Alice's auth token."""
    token_a = _register(client, USER_ALICE)["access_token"]
    _register(client, USER_BOB)
    return token_a


# ---------------------------------------------------------------------------
# 1. Normal Functional Tests
# ---------------------------------------------------------------------------

class TestSearchFunctional:
    """Verify standard legitimate search functionality."""

    def test_search_by_name(self, client, auth_token):
        resp = client.get(
            "/api/v1/users/search?q=Alice",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["email"] == USER_ALICE["email"]
        assert data[0]["full_name"] == USER_ALICE["full_name"]

    def test_search_by_email(self, client, auth_token):
        resp = client.get(
            "/api/v1/users/search?q=bob@test.local",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["email"] == USER_BOB["email"]

    def test_search_multiple_matches(self, client, auth_token):
        resp = client.get(
            "/api/v1/users/search?q=@test.local",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_search_nonexistent_returns_empty(self, client, auth_token):
        resp = client.get(
            "/api/v1/users/search?q=nonexistent_user",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_search_empty_query_returns_empty(self, client, auth_token):
        resp = client.get(
            "/api/v1/users/search?q=",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_search_unauthenticated_rejected(self, client):
        resp = client.get("/api/v1/users/search?q=alice")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 2. Security Regression Tests (Remediated / Default Endpoint)
# ---------------------------------------------------------------------------

class TestSQLInjectionRemediation:
    """Verify that the default search endpoint is protected against SQL injection."""

    def test_single_quote_treated_as_literal_data(self, client, auth_token):
        """Single quote metacharacter must not cause database syntax error."""
        resp = client.get(
            "/api/v1/users/search?q=alice'",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        # No user literally has "alice'" in their name/email
        assert resp.json() == []

    def test_boolean_tautology_does_not_bypass_filter(self, client, auth_token):
        """Boolean tautology must not return unauthorized records."""
        resp = client.get(
            "/api/v1/users/search?q=' OR 1=1 --",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        # In a parameterized query, "' OR 1=1 --" is treated as literal search text
        assert resp.json() == []

    def test_boolean_conditional_inference_neutralized(self, client, auth_token):
        """Injected SQL conditions must not alter query logic."""
        resp_true = client.get(
            "/api/v1/users/search?q=alice' AND '1'='1' --",
            headers=_auth_header(auth_token),
        )
        resp_false = client.get(
            "/api/v1/users/search?q=alice' AND '1'='2' --",
            headers=_auth_header(auth_token),
        )
        assert resp_true.status_code == 200
        assert resp_false.status_code == 200
        assert resp_true.json() == []
        assert resp_false.json() == []


# ---------------------------------------------------------------------------
# 3. Lab Demonstration Tests (Isolated Vulnerable Mode)
# ---------------------------------------------------------------------------

class TestSQLInjectionVulnerableMode:
    """Verify that the isolated lab mode reproduces VULN-002 for training."""

    def test_vulnerable_mode_syntax_error(self, client, auth_token):
        """Single quote in vulnerable mode triggers unhandled database syntax error."""
        with pytest.raises(Exception):
            client.get(
                "/api/v1/users/search?q=alice'&mode=vulnerable",
                headers=_auth_header(auth_token),
            )

    def test_vulnerable_mode_boolean_tautology_dumps_all(self, client, auth_token):
        """Tautology in vulnerable mode bypasses filter and returns all users."""
        resp = client.get(
            "/api/v1/users/search?q=' OR 1=1 --&mode=vulnerable",
            headers=_auth_header(auth_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        # Both Alice and Bob returned due to injected tautology
        assert len(data) == 2

