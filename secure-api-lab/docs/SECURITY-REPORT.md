# Application Security Assessment Report — secure-api-lab

**Target Application**: secure-api-lab  
**Assessment Period**: Ongoing (Controlled Lab Environment)  
**Assessment Type**: API Security Assessment & Vulnerability Research  
**Lead Engineer**: Application Security Engineer  

---

## 1. Executive Summary

This document serves as the centralized security assessment report for the `secure-api-lab` application. The primary objective of this ongoing assessment is to evaluate the security architecture, authentication integrity, access control enforcement, and data protection mechanisms across the RESTful API endpoints.

During the assessment phases, two primary vulnerability categories have been evaluated and confirmed:
1. **Broken Object Level Authorization (BOLA / IDOR)**: Identified in `GET /api/v1/users/{user_id}`, allowing authenticated users to access peer user records without proper authorization checks.
2. **SQL Injection (SQLi)**: Identified in `GET /api/v1/users/search?q=<search>`, where dynamic string interpolation into an active PostgreSQL query allows error-based syntax manipulation and boolean inference record enumeration.

Additional attack surfaces (including remote content ingestion, file handling, and session mechanics) remain queued for structured evaluation.

---

## 2. Assessment Scope

Testing was strictly confined to the local development and testing environment:

| Scope Dimension | Details |
| :--- | :--- |
| **Application Name** | `secure-api-lab` |
| **Environment** | Local Docker Compose deployment |
| **Target Host** | `http://localhost:8000` |
| **Database** | PostgreSQL 16 (`secure_api_lab`) |
| **Primary Testing Tool** | Burp Suite Professional / Community |
| **Secondary Tools** | Python 3, Pytest, HTTPX, cURL |
| **Operational Constraint**| Authorized local testing only. No public or production systems were in scope. |

---

## 3. Testing Methodology

The assessment follows standard industry frameworks, including the **OWASP API Security Top 10** and the **OWASP Web Security Testing Guide (WSTG)**:

1. **Authentication Testing**:
   - Verification of identity assertion workflows (token issuance, formatting, and validation).
   - Evaluation of credential transmission, hashing algorithms, and session lifetimes.
2. **Authorization Testing**:
   - **Object-Level Authorization (BOLA/IDOR)**: Interception of resource requests via Burp Suite, tampering with entity identifiers (e.g., path parameters, query parameters), and verifying that cross-tenant access is rejected.
   - **Function-Level Authorization (BFLA)**: Assessment of administrative or privileged operations against standard user credentials.
3. **Input Validation & Injection Testing**:
   - Detection of SQL syntax metacharacters, tautological logic, and dynamic statement manipulation.
   - Testing for error-based, boolean-based, and union-based injection vectors.
4. **Traffic Interception & Request Tampering**:
   - Using Burp Proxy to capture HTTP transactions, analyze request headers, and leverage Burp Repeater for parameter manipulation.
5. **Data Layer Inspection**:
   - Direct verification of database records and schemas to correlate API responses with underlying storage states.
6. **Remediation & Retesting Workflow**:
   - Defining clear root-cause diagnoses, proposing defensive code implementations, and tracking findings through re-evaluation.

---

## 4. Findings Summary

| Vulnerability ID | Vulnerability Type | Affected Endpoint | Severity | Lifecycle Status |
| :--- | :--- | :--- | :--- | :--- |
| [VULN-001](vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md) | Broken Object Level Authorization (BOLA / IDOR) | `GET /api/v1/users/{user_id}` | To Be Confirmed | **Open** |
| [VULN-002](vulnerabilities/VULN-002-SQL-Injection.md) | SQL Injection (SQLi) | `GET /api/v1/users/search` | To Be Confirmed | **Open** |

---

## 5. Detailed Findings

### [VULN-001 — Broken Object Level Authorization (BOLA)](vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md)

- **CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)
- **OWASP API Security**: API1:2023
- **Summary**: The endpoint `GET /api/v1/users/{user_id}` validates caller authentication via JWT token but fails to verify that the requesting principal possesses authorization to inspect the requested `user_id`. An authenticated user (e.g., Alice, ID 35) can supply the identifier of another user (e.g., Bob, ID 36) and receive their profile object with status `200 OK`.
- **Severity Note**: Currently recorded as **To Be Confirmed** pending complete data classification of exposed user attributes and verification of related modification endpoints.
- **Full Report**: [VULN-001-IDOR-BOLA-User-Access.md](vulnerabilities/VULN-001-IDOR-BOLA-User-Access.md)

### [VULN-002 — SQL Injection (SQLi)](vulnerabilities/VULN-002-SQL-Injection.md)

- **CWE**: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- **OWASP API Security**: API8:2023 / OWASP A03:2021
- **Summary**: The user search endpoint `GET /api/v1/users/search?q=<search>` concatenates the untrusted `q` parameter directly into an active SQL query string without parameterization. Testing confirms error-based behavior (single quotes triggering HTTP 500 database syntax errors) and boolean-based inference (tautologies like `' OR 1=1 --` dumping all database records).
- **Severity Note**: Currently recorded as **To Be Confirmed** pending evaluation of database user privileges and potential cross-table exfiltration via UNION queries.
- **Full Report**: [VULN-002-SQL-Injection.md](vulnerabilities/VULN-002-SQL-Injection.md)

---

## 6. Remediation Tracking

| Finding ID | Title | Recommended Technical Fix | Current Status | Retest Status |
| :--- | :--- | :--- | :--- | :--- |
| **VULN-001** | BOLA User Profile Access | Enforce server-side identity validation (`current_user.id == user_id`) before database query execution. | Pending | Pending |
| **VULN-002** | SQL Injection in Search | Replace dynamic string formatting with parameterized queries (`text("... ILIKE :pattern")`) or ORM query builders. | **Implemented** | **Passed** |

---

## 7. Retest Results

| Finding ID | Retest Date | Tester | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
| VULN-001 | Pending | — | Pending | Awaiting secure implementation |
| VULN-002 | 2026-09-18 | AppSec Engineer | **Passed** | Default endpoint parameterized via bind parameters; SQL metacharacters handled as literal data; 26/26 regression tests passing. Training flaw preserved under `?mode=vulnerable`. |

---

## 8. Security Assessment Notes

The `secure-api-lab` application is an intentionally vulnerable codebase developed in a local sandbox for Application Security engineering training, threat modeling, security test automation, and portfolio documentation. 

Vulnerabilities are documented with rigorous technical standards to demonstrate end-to-end security workflows from discovery to remediation and verification.

---

## 9. References

- [OWASP API Security Project (2023 Edition)](https://owasp.org/www-project-api-security/)
- [OWASP Web Security Testing Guide (WSTG v4.2)](https://owasp.org/www-project-web-security-testing-guide/)
- [MITRE Common Weakness Enumeration (CWE)](https://cwe.mitre.org/)
- [NIST Special Publication 800-115: Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/publications/detail/sp/800-115/final)

