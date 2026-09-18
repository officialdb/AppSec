# Secure API Lab

A deliberately vulnerable FastAPI application and hardened counterpart designed to demonstrate practical Application Security engineering.

## Objectives

This project demonstrates:

- Secure coding
- API security
- Authentication and authorization
- Vulnerability discovery
- Security testing
- DevSecOps
- Threat modeling
- Secure software development

## Project Structure

- `vulnerable-api/` — intentionally vulnerable implementation
- `secure-api/` — hardened implementation
- `security-tests/` — security and regression tests
- `docs/` — security documentation
- `scripts/` — security and development utilities

## Security Topics

- Broken Access Control / IDOR
- SQL Injection
- XSS
- SSRF
- JWT weaknesses
- Weak password handling
- Rate-limit bypass
- Mass assignment
- Insecure file uploads
- Excessive data exposure

---

## Monorepo Layout

All lab components, services, and documentation reside under the [`secure-api-lab/`](secure-api-lab/) directory:

```text
AppSec/
│
├── .gitignore                         # Monorepo-wide ignore rules
├── README.md                          # Repository overview & objectives
│
└── secure-api-lab/                    # [Project 1 Root]
    ├── docker-compose.yml             # Multi-container orchestration (Postgres & API)
    ├── README.md                      # Dedicated Secure API Lab project guide
    ├── SECURITY.md                    # Project security policy & disclosure rules
    ├── .gitignore                     # Lab-specific ignore rules
    │
    ├── vulnerable-api/                # Intentionally vulnerable FastAPI application
    │   ├── app/                       # Application source code (auth, users, documents)
    │   ├── alembic/                   # PostgreSQL schema migrations
    │   ├── tests/                     # 26 automated functional & vulnerability tests
    │   ├── Dockerfile                 # Container image specification
    │   └── requirements.txt           # Python dependencies
    │
    ├── secure-api/                    # Hardened counterpart service (remediation reference)
    │   └── README.md
    │
    ├── security-tests/                # External regression & health test harness
    │   ├── test_health.py
    │   ├── conftest.py
    │   └── requirements.txt
    │
    ├── docs/                          # Application security assessment documentation
    │   ├── architecture/              # System architecture & threat landscape diagrams
    │   │   └── README.md
    │   ├── vulnerabilities/           # Individual technical vulnerability reports
    │   │   ├── VULN-001-IDOR-BOLA-User-Access.md
    │   │   └── VULN-002-SQL-Injection.md
    │   └── SECURITY-REPORT.md         # Centralized security assessment report
    │
    └── scripts/                       # Operational, seeding & testing utilities
        └── README.md
```

---

## Quick Start

To launch the lab environment:

```bash
# Navigate to the project directory
cd secure-api-lab

# Start the services with Docker Compose
docker compose up -d

# Verify services are healthy
docker compose ps

# Access Swagger UI interactive documentation
open http://localhost:8000/docs

# Run automated tests inside the container
docker compose exec vulnerable-api python -m pytest tests/ -v
```

For complete setup instructions, endpoint guides, vulnerability write-ups, and Burp Suite testing walkthroughs, see the **[secure-api-lab README](secure-api-lab/README.md)**.
