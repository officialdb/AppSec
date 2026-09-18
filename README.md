# Application Security (AppSec) Engineering Portfolio

A comprehensive, production-grade Application Security engineering monorepo demonstrating practical offensive vulnerability research, defensive architecture, automated DevSecOps pipelines, container/cloud hardening, and threat modeling across five specialized projects.

---

## Portfolio Projects Overview

This repository is organized into **five core projects**, each addressing a critical pillar of modern Application Security engineering:

| # | Project | Domain | Core Focus | Status |
| :-: | :--- | :--- | :--- | :-: |
| **01** | [**Secure API Lab**](secure-api-lab/) | API Security & Code Remediation | Intentionally vulnerable FastAPI service + hardened counterpart (OWASP API Top 10, BOLA/IDOR, SQLi, SSRF) | **Active** |
| **02** | **DevSecOps Pipeline** | CI/CD Security & Automation | Automated security pipeline with SAST, SCA, Secret Scanning, DAST, and SARIF triage in GitHub Actions | *Planned* |
| **03** | **Cloud & Container Hardening** | Infrastructure & Runtime Defense | Hardened container images, Kubernetes security policies, OPA/Rego enforcement, and IaC scanning | *Planned* |
| **04** | **Threat Modeling & Architecture** | Proactive System Design | STRIDE & PASTA threat models, data flow diagrams, trust boundary analysis, and security design reviews | *Planned* |
| **05** | **Custom AppSec Tooling** | Security Automation & Engineering | Custom AST-based static analysis rules, authorization testing utilities, and vulnerability triage scripts | *Planned* |

---

## 1. Project Summaries

### [Project 1: Secure API Lab](secure-api-lab/) (`secure-api-lab/`) — *Active*
A dual-service security testing laboratory containing an intentionally vulnerable REST API alongside a hardened, defensive reference implementation.
- **Objectives**: Demonstrate vulnerability discovery using Burp Suite, root-cause code analysis, defense-in-depth remediation, and automated regression testing.
- **Key Vulnerabilities**: Broken Object Level Authorization (BOLA/IDOR), SQL Injection, SSRF, XSS, Insecure File Uploads, JWT Weaknesses, Rate-Limit Bypass.
- **Technology Stack**: Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2, Alembic, Docker Compose, Pytest, HTTPX, Burp Suite.
- **Documentation**: Detailed architecture, endpoint catalogs, and finding reports are available in [`secure-api-lab/README.md`](secure-api-lab/README.md).

### Project 2: DevSecOps CI/CD Pipeline (`devsecops-pipeline/`) — *Planned*
A fully automated, shift-left security testing pipeline integrating continuous security checks into developer workflows.
- **Objectives**: Prevent vulnerabilities from reaching production through automated quality gates, triage workflows, and policy enforcement.
- **Key Capabilities**: Static Application Security Testing (SAST), Software Composition Analysis (SCA / dependency vulnerability scanning), automated secret detection with pre-commit hooks, Dynamic Application Security Testing (DAST) baselines, and centralized SARIF reporting.
- **Technology Stack**: GitHub Actions, Semgrep, Trivy, Gitleaks, OWASP ZAP, SARIF, Docker.

### Project 3: Cloud & Container Security Hardening (`cloud-container-security/`) — *Planned*
A security engineering project focused on container supply-chain security, runtime isolation, and Infrastructure as Code (IaC) governance.
- **Objectives**: Implement least-privilege security configurations from container build to runtime orchestration.
- **Key Capabilities**: Multi-stage distroless container builds, non-root user execution, Linux capability dropping, Kubernetes Pod Security Standards, OPA/Rego policy-as-code enforcement, and CIS Benchmark compliance.
- **Technology Stack**: Docker, Kubernetes, Terraform, Open Policy Agent (OPA/Rego), Trivy IaC, Linux namespaces/cgroups.

### Project 4: Threat Modeling & Security Architecture Review (`threat-modeling/`) — *Planned*
A collection of comprehensive security architecture reviews, threat models, and risk assessment methodologies applied to modern distributed systems.
- **Objectives**: Identify architectural flaws and design weaknesses prior to code implementation.
- **Key Capabilities**: STRIDE and PASTA threat modeling methodologies, Data Flow Diagrams (DFDs) with trust boundaries, attack tree modeling, and Security Architecture Decision Records (ADRs).
- **Deliverables**: Architectural diagrams, threat matrices, mitigation strategies, and executive risk summaries.

### Project 5: Custom AppSec Tooling & Automation (`security-tooling/`) — *Planned*
Custom security utilities and developer-focused automation tools developed to solve specific application security testing challenges.
- **Objectives**: Build high-signal, developer-friendly internal security tools that augment commercial and open-source scanners.
- **Key Capabilities**: Custom AST (Abstract Syntax Tree) linting rules for dangerous sink detection, automated authorization matrix test generators, and vulnerability notification integrations.
- **Technology Stack**: Python, tree-sitter / AST, Click/Typer, Requests, FastAPI.

---

## 2. Monorepo Layout

```text
AppSec/
│
├── .gitignore                         # Monorepo-wide ignore rules
├── README.md                          # Portfolio index & five-project overview (this document)
│
├── secure-api-lab/                    # [Project 1] Secure API Engineering Lab (Active)
│   ├── README.md                      # Dedicated Secure API Lab project documentation
│   ├── SECURITY.md                    # Lab security policy & disclosure rules
│   ├── docker-compose.yml             # Local PostgreSQL & API runtime orchestration
│   ├── vulnerable-api/                # Deliberately vulnerable FastAPI service
│   ├── secure-api/                    # Hardened reference implementation
│   ├── security-tests/                # Automated DAST & security regression harness
│   ├── docs/                          # Vulnerability reports & threat architecture
│   └── scripts/                       # Database seeding & testing helper scripts
│
├── devsecops-pipeline/                # [Project 2] CI/CD Security Pipeline (Planned)
├── cloud-container-security/          # [Project 3] Cloud & Container Hardening (Planned)
├── threat-modeling/                   # [Project 4] Threat Models & Architecture (Planned)
└── security-tooling/                  # [Project 5] Custom AppSec Tools & Automation (Planned)
```

---

## 3. Core Competencies Demonstrated

- **Offensive Security & Vulnerability Research**: Manual API penetration testing, Burp Suite workflows, root-cause vulnerability analysis, and exploit proof-of-concept development.
- **Defensive Engineering & Secure Coding**: Implementing robust input validation, parameterization, cryptographic controls, and fine-grained authorization checks.
- **DevSecOps & Automation**: Integrating automated security gates (SAST, SCA, secrets, DAST) into CI/CD pipelines without blocking developer velocity.
- **Cloud & Container Security**: Enforcing container hygiene, least-privilege principles, policy-as-code, and infrastructure security baselines.
- **Threat Modeling & Governance**: Conducting structured architecture risk assessments (STRIDE/PASTA) and documenting actionable security requirements.

---

## 4. Security Policy & Disclaimer

All code, configurations, and vulnerabilities contained in this repository are strictly intended for **authorized local security testing, vulnerability research, and educational purposes**.

- Vulnerable components must **never be deployed to public, production, or cloud-facing environments**.
- Offensive techniques and scripts must only be used against systems with explicit, documented authorization.
- Never commit real credentials, sensitive personal data, or production secrets to this repository.
