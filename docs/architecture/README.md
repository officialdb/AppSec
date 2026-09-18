# System Architecture & Threat Landscape

## Overview

The `secure-api-lab` is a modular lab environment designed for practical application security engineering, vulnerability discovery, and secure code remediation.

The initial target service is `vulnerable-api`, a Document Management RESTful API built with Python, FastAPI, SQLAlchemy 2.x, and PostgreSQL, containerized via Docker Compose.

## Architecture Diagram

```
+-------------------------------------------------------------------------+
|                              Host System                                |
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
|  |        vulnerable-api          |     |          lab-db            |  |
|  |     (FastAPI / Uvicorn)        |     |      (PostgreSQL 16)       |  |
|  |                                |     |                            |  |
|  |  * Authentication: PyJWT       |     |  * secure_api_lab          |  |
|  |  * ORM: SQLAlchemy 2.x (Sync)  +---->+    - users                 |  |
|  |  * Driver: psycopg 3           |     |    - documents             |  |
|  |  * Migrations: Alembic         |     |    - files                 |  |
|  |                                |     |    - audit_logs            |  |
|  +--------------------------------+     +----------------------------+  |
+-------------------------------------------------------------------------+
```

## Component Breakdown

1. **API Gateway / Backend (`vulnerable-api`)**:
   - **Framework**: FastAPI (Python 3.12-slim) running on Uvicorn.
   - **Routing Architecture**: Modular APIRouters partitioned under `/api/v1/`:
     - `/auth`: Registration (`/register`) and Authentication (`/login`).
     - `/users`: Current profile (`/me`), user search (`/search`), and ID-targeted profile endpoints (`/{user_id}`).
     - `/documents`: Document lifecycle management.
     - `/files`: File ingestion and management (staged for file-handling tests).
     - `/import`: Remote content retrieval (staged for SSRF testing).
   - **Data Access Layer**: Sync SQLAlchemy 2.x engine utilizing the `psycopg` (v3) PostgreSQL driver.

2. **Persistence Layer (`db`)**:
   - **Engine**: PostgreSQL 16 Alpine.
   - **Schema Management**: Controlled via Alembic migration versions.
   - **Entity Relationships**:
     - `users` (Primary entities: `id`, `email`, `password`, `full_name`, `role`, timestamps).
     - `documents` (`owner_id` foreign key referencing `users.id`).
     - `files` (`owner_id` foreign key referencing `users.id`).
     - `audit_logs` (`user_id` foreign key referencing `users.id`).

3. **Security Testing Surface**:
   - **Proxy / Inspection**: Burp Suite intercepting client traffic bound for `http://localhost:8000`.
   - **Security Boundaries Tested**:
     - Identity verification (Authentication).
     - Resource ownership & entitlement enforcement (Object-level & Function-level Authorization).
     - Data validation & SQL execution boundaries (SQL Injection).

---

## SQL Injection Lab Architecture (VULN-002)

### Vulnerable Data Flow

In the vulnerable implementation, untrusted data flows unvalidated directly from the HTTP request into the SQL query construction:

```
Burp Suite (Attacker Payload)
      │
      ▼ HTTP GET /api/v1/users/search?q=alice%27+OR+1=1+--
FastAPI HTTP Endpoint
      │
      ▼ Extracted parameter: q: str
Route Handler (search_users in app/api/routes/users.py)
      │
      ▼ [VULNERABILITY POINT: Unsafe String Formatting]
query_str = f"SELECT ... WHERE email ILIKE '%{q}%' OR full_name ILIKE '%{q}%'"
      │
      ▼
SQLAlchemy Execution Layer (db.execute(text(query_str)))
      │
      ▼ Raw SQL sent over network connection
PostgreSQL Engine
      │ -> Injected syntax executes with database process privileges
      ▼
Client receives unauthorized records / syntax error
```

### Remediated Data Flow

In the remediated implementation, the application separates the static SQL command template from the dynamic user data:

```
Burp Suite (Attacker Payload)
      │
      ▼ HTTP GET /api/v1/users/search?q=alice%27+OR+1=1+--
FastAPI HTTP Endpoint
      │
      ▼ Extracted parameter: q: str
Route Handler (search_users in app/api/routes/users.py)
      │
      ▼ [REMEDIATION POINT: Parameterized Query Template]
query_template = text("SELECT ... WHERE email ILIKE :pattern OR full_name ILIKE :pattern")
params = {"pattern": f"%{q}%"}
      │
      ▼
SQLAlchemy Execution Layer (db.execute(query_template, params))
      │
      ▼ Driver protocol transmits SQL template and data parameters separately
PostgreSQL Engine
      │ -> Input is treated strictly as literal string data within the pattern
      ▼
Client receives only legitimate search matches (0 rows matching literal payload)
```
