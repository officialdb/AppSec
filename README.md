# Application Security (AppSec) Engineering Portfolio

A professional Application Security engineering monorepo showcasing practical vulnerability research, secure backend architecture, offensive testing methodologies, and defensive code remediation.

---

## Portfolio Monorepo Structure

```text
AppSec/
│
├── .gitignore                         # Monorepo-wide ignore rules
├── README.md                          # Portfolio index & overview
│
└── secure-api-lab/                    # [PROJECT 1] Secure API Engineering Lab
    ├── docker-compose.yml             # Local multi-container lab environment
    ├── README.md                      # Project 1 documentation & roadmap
    ├── SECURITY.md                    # Project security & responsible disclosure policy
    │
    ├── vulnerable-api/                # FastAPI service with intentional vulnerabilities
    │   ├── app/                       # Modular application code (core, db, schemas, api)
    │   ├── alembic/                   # Database schema migrations
    │   ├── tests/                     # Functional & vulnerability demonstration tests
    │   ├── Dockerfile                 # Python 3.12 container specification
    │   └── requirements.txt           # Service dependencies
    │
    ├── secure-api/                    # Hardened counterpart service (remediated reference)
    │   └── README.md
    │
    ├── security-tests/                # Automated security test harness (DAST & regression)
    │   ├── test_health.py
    │   └── conftest.py
    │
    ├── docs/                          # Comprehensive AppSec documentation
    │   ├── architecture/              # Threat models & system architecture diagrams
    │   ├── vulnerabilities/           # Individual technical vulnerability reports
    │   │   ├── VULN-001-IDOR-BOLA-User-Access.md
    │   │   └── VULN-002-SQL-Injection.md
    │   └── SECURITY-REPORT.md         # Centralized security assessment report
    │
    └── scripts/                       # Development, seeding & security tooling utilities
        └── README.md
```

---

## Projects in this Monorepo

### Project 1: Secure API Lab (`secure-api-lab/`)

A controlled, local security lab environment demonstrating realistic API vulnerabilities and their defensive remediations.

- **Technology Stack**: Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2.x, Alembic, Docker Compose, Burp Suite, Pytest.
- **Vulnerabilities Researched & Documented**:
  - **[VULN-001: Broken Object Level Authorization (BOLA / IDOR)](secure-api-lab/docs/vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md)**:
    - *CWE-639* | *OWASP API1:2023*
    - Demonstrated unauthorized cross-tenant profile retrieval on `GET /api/v1/users/{user_id}`.
  - **[VULN-002: SQL Injection (SQLi)](secure-api-lab/docs/vulnerabilities/VULN-002-SQL-Injection.md)**:
    - *CWE-89* | *OWASP A03:2021 / API8:2023*
    - Demonstrated error-based syntax manipulation and boolean-based inference table dumping on `GET /api/v1/users/search?q=<search>`. Remediated via parameterized queries.
- **Assessment Report**: [SECURITY-REPORT.md](secure-api-lab/docs/SECURITY-REPORT.md)
- **Architecture & Data Flows**: [architecture/README.md](secure-api-lab/docs/architecture/README.md)

---

## Quick Start — Running Project 1

To start the **Secure API Lab** environment:

```bash
# Navigate to Project 1
cd secure-api-lab

# Start the PostgreSQL and vulnerable-api services
docker compose up -d

# Verify container health
docker compose ps

# Access Interactive API Documentation (Swagger UI)
open http://localhost:8000/docs

# Run the automated test suite (26 tests)
docker compose exec vulnerable-api python -m pytest tests/ -v
```

---

## Monorepo Standards & Design Principles

1. **No Duplicated Root Artifacts**: All project-specific runtimes, compose definitions, and source code reside inside their respective project directories (`secure-api-lab/`).
2. **Clean Version Control**: Single unified Git history tracking the monorepo root with no nested `.git` submodules or repositories.
3. **Reproducible Security Research**: Every security finding includes root-cause analysis, proof-of-concept requests, verified defensive fixes, and automated regression tests.
4. **Controlled Lab Safety**: All vulnerable components are strictly isolated to local environments and designed never to target or interact with third-party systems.
