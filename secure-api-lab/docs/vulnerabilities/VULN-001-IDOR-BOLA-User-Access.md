# VULN-001 — Broken Object Level Authorization (BOLA)

## Executive Summary

An authorization vulnerability exists within the user profile retrieval endpoint of the `secure-api-lab` application. Specifically, the application implements authentication to verify client identity, but fails to implement an authorization control mechanism before resolving and returning user profile objects.

An authenticated user can supply arbitrary identifier values within the `user_id` path parameter and retrieve records belonging to other users. Authentication succeeds, but authorization is entirely absent at the object level, resulting in horizontal privilege escalation.

---

## Vulnerability Classification

- **Vulnerability**: Broken Object Level Authorization (BOLA)
- **Common Name**: Insecure Direct Object Reference (IDOR)
- **OWASP API Security Classification**: API1:2023 — Broken Object Level Authorization
- **CWE**: CWE-639: Authorization Bypass Through User-Controlled Key
- **Affected Endpoint**: `GET /api/v1/users/{user_id}`
- **Authentication Required**: Yes
- **Authorization Required**: Yes
- **Severity**: **To Be Confirmed**
  - *Severity Determination Factors*: The definitive severity rating for this finding depends on the data classification of the attributes returned by the endpoint (e.g., whether PII or contact information is exposed), the sensitivity of the user population, the predictability of the object identifiers (which currently use sequential integers), and whether corresponding state-modifying endpoints (such as `PATCH /api/v1/users/{user_id}`) share the same defect.

---

## Affected Component

- **Affected Endpoint**: `GET /api/v1/users/{user_id}`
- **HTTP Method**: `GET`
- **Affected Parameter**: `user_id` (Path Parameter)
- **Source File**: `vulnerable-api/app/api/routes/users.py`

---

## Test Environment

- **Application**: `secure-api-lab`
- **Environment**: Local Docker environment
- **Database**: PostgreSQL 16
- **Testing Tool**: Burp Suite
- **Authenticated User**: Alice
- **Authenticated User ID**: 35
- **Target User**: Bob
- **Target User ID**: 36

> *Note: In accordance with responsible testing and reporting practices, no passwords, JSON Web Tokens (JWTs), API keys, session secrets, or password hashes are included in this report.*

---

## Preconditions

Exploitation of this vulnerability requires the following conditions:

1. A valid authenticated account within the application.
2. A valid authentication token or session issued by the authentication service.
3. Knowledge of, or the ability to discover or enumerate, another user's object identifier (facilitated in this environment by sequential integer keys).

---

## Reproduction Steps

1. Authenticate to the API as Alice (User ID: 35) via the authentication endpoint.
2. Intercept and capture the authenticated HTTP request traffic using Burp Suite.
3. Send the profile retrieval request to **Burp Repeater**.
4. Issue the baseline request:
   ```http
   GET /api/v1/users/35
   ```
5. Confirm and record the baseline response verifying Alice's profile data.
6. Retain Alice's authentication token unchanged in the `Authorization` header.
7. Modify only the path parameter from `35` to `36`:
   ```http
   GET /api/v1/users/36
   ```
8. Dispatch the modified request via Burp Repeater.
9. Observe that the server returns HTTP `200 OK` and exposes the resource belonging to Bob (User ID: 36).

---

## Evidence

### Baseline Request (Self-Access — Authorized)

```http
GET /api/v1/users/35 HTTP/1.1
Host: localhost:<PORT>
Authorization: Bearer [REDACTED]
Accept: application/json
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

[RESPONSE BODY TO BE INSERTED FROM BURP SUITE]
```

---

### Unauthorized Object Request (Cross-Account Access — BOLA/IDOR)

```http
GET /api/v1/users/36 HTTP/1.1
Host: localhost:<PORT>
Authorization: Bearer [REDACTED]
Accept: application/json
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

[RESPONSE BODY TO BE INSERTED FROM BURP SUITE]
```

*Confirmed Fact: The identical Bearer token belonging to User 35 was used in both requests.*

---

## Expected Behavior

The application should validate whether the authenticated subject (the principal represented by the authentication token) has explicit permission to view the specific user object identified by the request parameter.

For a self-service profile endpoint:
- `User 35` requesting `/api/v1/users/35` $\rightarrow$ `200 OK` (Access allowed)
- `User 35` requesting `/api/v1/users/36` $\rightarrow$ Authorization Failure

The expected failure response should be either:
- **`403 Forbidden`**: Explicitly denying access to the foreign object when access control is violated.
- **`404 Not Found`**: Indicating that the resource is unavailable or non-existent to the requester, which has the added security advantage of preventing resource enumeration.

---

## Actual Behavior

- **Authenticated User**: User 35 (Alice)
- **Requested Object**: User 36 (Bob)
- **Authentication Token Used**: Token issued to User 35
- **HTTP Response Status**: `200 OK`
- **Observed Result**: The API successfully retrieved and transmitted the profile object belonging to User 36 without evaluating the requester's authorization entitlements.

---

## Security Impact

The confirmed security impact of this vulnerability includes:

- **Unauthorized Information Disclosure**: Any authenticated user can read profile data belonging to other registered users.
- **Horizontal Privilege Escalation**: A user operating at standard user privileges can access peers' resources at the same privilege tier.
- **Account & Identity Enumeration**: Because user identifiers are sequential integers (`35`, `36`, etc.), an authenticated actor could programmatically iterate across the ID space to discover active accounts.
- **Privacy Exposure**: Personal data associated with user profiles is accessible across account boundaries.

### Items Not Confirmed / Out of Scope
Testing has **not** demonstrated exposure of passwords, password hashes, administrative consoles, cryptographic secrets, or financial data through this specific endpoint. Assertions of impact are strictly confined to the attributes returned by `GET /api/v1/users/{user_id}`.

---

## Root Cause Analysis

Inspection of the backend implementation in `vulnerable-api/app/api/routes/users.py` reveals the exact mechanism of the flaw:

```python
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # The application verifies identity via get_current_user,
    # but never checks if current_user is authorized to access user_id.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Architectural Distinction: Authentication vs. Authorization

```
+-----------------------------------------------------------------------+
| Authentication ("Who are you?")                                       |
| -> Handled by Depends(get_current_user)                                |
| -> Decodes JWT signature, extracts user identity                      |
| -> Result: SUCCESS (Identity confirmed as User 35)                   |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
| Authorization ("Are you allowed to access this object?")              |
| -> Missing entirely from route logic                                  |
| -> Database query executes directly: WHERE id = user_id               |
| -> Result: BYPASSED (No check comparing current_user.id with user_id) |
+-----------------------------------------------------------------------+
```

The defect stems from treating successful identity verification as sufficient permission to access any entity requested by the client.

---

## Remediation

### 1. Server-Side Object-Level Authorization Check

Enforce strict relationship verification on the server before querying or returning the object:

```python
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Enforce object-level authorization
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 2. Contextual Access Control

For applications where users legitimately access resources outside their direct identity (e.g., team members, shared workspaces):
- Implement an explicit policy enforcement point (PEP) evaluating **Subject**, **Action**, **Resource**, and **Context**.
- Validate access through defined authorization models (Role-Based Access Control / Attribute-Based Access Control).

### 3. Critical Architecture Principles
- **Enforce Server-Side**: Authorization checks must always execute on the server backend. Never rely on frontend UI gating or hidden elements.
- **Do Not Rely on Obscurity**: Replacing sequential integer IDs with UUIDs/GUIDs introduces non-predictability, but does **not** replace authorization. UUIDs without authorization checks remain vulnerable to BOLA.

---

## Verification & Retest Procedure

Following the implementation of the remediation in the codebase, execute the following verification steps:

1. Authenticate as User 35 (Alice).
2. Execute `GET /api/v1/users/35` $\rightarrow$ Verify that status `200 OK` is returned and Alice's profile is accessible.
3. Execute `GET /api/v1/users/36` $\rightarrow$ Verify that the request is rejected with `403 Forbidden` (or `404 Not Found`).
4. Execute `GET /api/v1/users/{random_id}` across multiple integer values to verify consistent rejection.
5. Verify that error responses do not leak internal diagnostic details or user existence states.

### Status Tracking
- **Vulnerability Status**: `Open`
- **Remediation Status**: `Pending`
- **Retest Status**: `Pending`

---

## References

1. **OWASP API Security Top 10 (2023)**:
   - [API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
2. **Common Weakness Enumeration (CWE)**:
   - [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
   - [CWE-285: Improper Authorization](https://cwe.mitre.org/data/definitions/285.html)
3. **OWASP Web Security Testing Guide (WSTG)**:
   - [WSTG-ATHZ-04: Testing for Insecure Direct Object References](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
4. **NIST Special Publication**:
   - [NIST SP 800-95: Guide to Secure Web Services](https://csrc.nist.gov/publications/detail/sp/800-95/final)

