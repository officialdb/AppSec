# Secure API Lab — Project Guide

A deliberately vulnerable FastAPI application and hardened counterpart designed to demonstrate practical Application Security engineering, vulnerability discovery, threat modeling, and defensive code remediation.

---

## 1. Overview & Architecture

The **Secure API Lab** provides a self-contained local environment modeling a Document Management RESTful API backed by PostgreSQL. The project follows a dual-implementation pattern:
- **`vulnerable-api/`**: Implements intentionally vulnerable endpoints representing common OWASP API Security Top 10 flaws for discovery and exploitation.
- **`secure-api/`**: The hardened counterpart providing secure coding reference implementations.

```
+-------------------------------------------------------------------------+
|                               Host System                               |
|                                                                         |
|  +-----------------------+              +----------------------------+  |
|  |   Security Tester /   |              |         PostgreSQL         |  |
|  |      Burp Suite       |              |        Client / DB         |  |
|  +-----------+-----------+              +-------------+--------------+  |
+--------------|----------------------------------------|-----------------+
               | HTTP (Port 8000)                       | Port 5433:5432
               v                                        v
+-------------------------------------------------------------------------+
|                       Docker Bridge Network (lab)                       |
|                                                                         |
|  +--------------------------------+     +----------------------------+  |
|  |        vulnerable-api          |     |             db             |  |
|  |     (FastAPI / Uvicorn)        |     |      (PostgreSQL 16)       |  |
|  |                                |     |                            |  |
|  |  * Authentication: PyJWT       |     |  * Database:               |  |
|  |  * ORM: SQLAlchemy 2.x (Sync)  +---->+    secure_api_lab          |  |
|  |  * Driver: psycopg 3           |     |  * Tables: users,          |  |
|  |  * Migrations: Alembic         |     |    documents, files,       |  |
|  |  * Hot-Reload: Volume Mounted  |     |    audit_logs              |  |
|  +--------------------------------+     +----------------------------+  |
+-------------------------------------------------------------------------+
```

### Technology Stack
- **API Engine**: Python 3.12, FastAPI, Uvicorn
- **Data Layer**: PostgreSQL 16 Alpine, SQLAlchemy 2.x, Alembic, psycopg 3
- **Authentication**: JWT (PyJWT), SHA-256 password handling (intentionally weak baseline)
- **Containerization**: Docker Compose
- **Security Tools**: Burp Suite, Pytest, HTTPX

---

## 2. Project Structure

```text
secure-api-lab/
├── docker-compose.yml                 # Multi-container orchestration (API + PostgreSQL)
├── README.md                          # Project documentation & vulnerability guide
├── SECURITY.md                        # Security policy & local lab disclaimer
├── .gitignore                         # Project-specific ignore rules
│
├── vulnerable-api/                    # Intentionally vulnerable implementation
│   ├── app/
│   │   ├── api/routes/                # auth.py, users.py, documents.py, files.py, import_url.py
│   │   ├── core/                      # Settings & configuration (config.py)
│   │   ├── db/                        # Database engine, sessionmaker & SQLAlchemy models
│   │   ├── schemas/                   # Pydantic v2 request/response models
│   │   └── main.py                    # FastAPI application instance & health endpoints
│   ├── alembic/                       # Schema migrations
│   ├── tests/                         # 26 automated unit, auth & vulnerability tests
│   ├── Dockerfile                     # Python 3.12-slim image definition
│   ├── requirements.txt               # Service dependencies
│   └── README.md                      # Service-level technical overview
│
├── secure-api/                        # Hardened implementation (remediation counterpart)
│   └── README.md
│
├── security-tests/                    # Standalone DAST & health test harness
│   ├── test_health.py
│   ├── conftest.py
│   └── requirements.txt
│
├── docs/                              # AppSec assessment documentation
│   ├── architecture/                  # Data flow diagrams & threat landscapes
│   │   └── README.md
│   ├── vulnerabilities/               # Technical vulnerability reports
│   │   ├── VULN-001-IDOR-BOLA-User-Access.md
│   │   └── VULN-002-SQL-Injection.md
│   └── SECURITY-REPORT.md             # Consolidated security assessment report
│
└── scripts/                           # Database seeding & testing helper scripts
    └── README.md
```

---

## 3. Quick Start

### Start Services
```bash
docker compose up -d
```

### Verify Service Health
```bash
# Check container status
docker compose ps

# Verify API liveness
curl http://localhost:8000/health

# Verify Database connectivity
curl http://localhost:8000/health/db
```

### Interactive Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 4. API Endpoints Directory

| Method | Endpoint | Description | Auth Required | Status |
| :--- | :--- | :--- | :---: | :--- |
| `GET` | `/health` | Application liveness probe | No | Functional |
| `GET` | `/health/db` | Database connectivity probe | No | Functional |
| `POST` | `/api/v1/auth/register` | Register new user account & issue JWT | No | Functional |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT | No | Functional |
| `GET` | `/api/v1/users/me` | Retrieve authenticated user's own profile | Yes | Functional |
| `GET` | `/api/v1/users/search` | Search users by name/email | Yes | **VULN-002 (SQLi)** |
| `GET` | `/api/v1/users/{user_id}` | Retrieve profile by user ID | Yes | **VULN-001 (BOLA)** |
| `PATCH`| `/api/v1/users/{user_id}` | Modify profile by user ID | Yes | **VULN-001 (BOLA)** |
| `POST` | `/api/v1/documents/` | Create a new document | Yes | Functional |
| `GET` | `/api/v1/documents/` | List current user's documents | Yes | Functional |
| `GET` | `/api/v1/documents/{id}` | Retrieve document by ID | Yes | Functional |
| `PATCH`| `/api/v1/documents/{id}` | Update document by ID | Yes | Functional |
| `DELETE`| `/api/v1/documents/{id}`| Delete document by ID | Yes | Functional |
| `POST` | `/api/v1/files/upload` | File ingestion endpoint | Yes | Stub (Staged) |
| `POST` | `/api/v1/import/url` | Remote content retrieval endpoint | Yes | Stub (Staged) |

---

## 5. Vulnerability Catalog

### VULN-001 — Broken Object Level Authorization (BOLA / IDOR)
- **Classification**: CWE-639 | OWASP API1:2023
- **Endpoints**: `GET /api/v1/users/{user_id}`, `PATCH /api/v1/users/{user_id}`
- **Vulnerability**: The endpoint verifies authentication but fails to verify authorization. User A (Alice, ID 35) can retrieve and modify User B's profile (Bob, ID 36).
- **Report**: [docs/vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md](docs/vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md)

### VULN-002 — SQL Injection (SQLi)
- **Classification**: CWE-89 | OWASP A03:2021 / API8:2023
- **Endpoint**: `GET /api/v1/users/search?q=<search>`
- **Vulnerability**: Dynamic string interpolation of parameter `q` into raw SQL allows error-based syntax manipulation (500) and boolean tautology table dumping (`' OR 1=1 --`).
- **Remediation**: Remediated via parameterized queries (`text("... ILIKE :pattern")`) by default; training vulnerability preserved under `mode=vulnerable`.
- **Report**: [docs/vulnerabilities/VULN-002-SQL-Injection.md](docs/vulnerabilities/VULN-002-SQL-Injection.md)

---

## 6. Testing & Quality Assurance

### Automated Pytest Suite (26 Tests)
Run the full test harness inside the container environment:

```bash
docker compose exec vulnerable-api python -m pytest tests/ -v
```

**Test Breakdown**:
- `tests/test_health.py` (3 tests): Liveness, response payload format, database check.
- `tests/test_auth.py` (8 tests): Registration, duplicate handling, login, wrong passwords, token extraction, unauthorized access rejection.
- `tests/test_idor.py` (4 tests): Cross-user unauthorized read, cross-user unauthorized modify, own profile baseline, 404 validation.
- `tests/test_sqli.py` (11 tests): Normal search (name, email, domain, empty), SQLi regression prevention (parameterization), lab mode injection validation.

---

## 7. Security Topics & Roadmap

| Topic | OWASP Mapping | Status |
| :--- | :--- | :---: |
| **Broken Access Control / IDOR** | API1:2023 / A01:2021 | **Implemented & Documented (VULN-001)** |
| **SQL Injection** | API8:2023 / A03:2021 | **Implemented & Documented (VULN-002)** |
| **Cross-Site Scripting (XSS)** | A03:2021 | Planned |
| **Server-Side Request Forgery (SSRF)** | API7:2023 / A10:2021 | Planned (`/api/v1/import/url`) |
| **JWT Weaknesses** | API2:2023 / A07:2021 | Baseline Implemented |
| **Weak Password Handling** | A07:2021 | Baseline Implemented |
| **Rate-Limit Bypass** | API4:2023 | Planned |
| **Mass Assignment** | API3:2023 | Planned |
| **Insecure File Uploads** | A08:2021 | Planned (`/api/v1/files/upload`) |
| **Excessive Data Exposure** | API3:2023 | Planned |

---

## 8. Security Policy & Disclaimer

This software is intentionally vulnerable and created solely for **authorized local security testing, vulnerability research, and secure software development education**.

- **Do not deploy** to production, public, or cloud-facing environments.
- **Do not use** tools or techniques against systems without explicit authorization.
- Never store real credentials or sensitive personal information in this lab.
