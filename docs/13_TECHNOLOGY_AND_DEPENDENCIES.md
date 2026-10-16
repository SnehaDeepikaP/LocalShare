# Technology & Dependency Inventory — LocalShare

**Document Identifier:** TDI-LS-2026-V2.0  
**Verification Date:** October 16, 2026  
**Runtime:** Python 3.13.7 (64-bit AMD64)  
**Package Manager:** pip 26.1.2  

---

## 1. Direct Production & Development Dependencies

| Package Name | Installed Version | Declared Constraint | Purpose in LocalShare | Architectural Selection Rationale | Required / Optional | License |
| :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| **Flask** | 3.0.0 | `Flask==3.0.0` | Core WSGI web application framework, routing, request/response handling, sessions. | Lightweight micro-framework enabling modular monolithic design via Blueprints. | **Required** | BSD-3-Clause |
| **Flask-SQLAlchemy**| 3.1.1 | `Flask-SQLAlchemy==3.1.1`| Flask extension integrating SQLAlchemy ORM with request teardown and session management. | Eliminates raw SQL string bugs, provides ORM relationship cascades, and prevents SQL injection via parameterized queries. | **Required** | BSD-3-Clause |
| **Flask-Migrate** | 4.1.0 | `Flask-Migrate==4.1.0`| Database migration tool linking Alembic with Flask CLI. | Enables declarative tracking of schema evolution from SQLite to PostgreSQL. | **Required** | MIT |
| **SQLAlchemy** | 2.1.4 | `SQLAlchemy==2.1.4` | Enterprise-grade Python SQL toolkit and Object Relational Mapper. | Industry-standard ORM with dialect abstraction (SQLite in dev, PostgreSQL in prod). | **Required** | MIT |
| **Werkzeug** | 3.1.6 | `Werkzeug==3.1.6` | WSGI utility library, password hashing (`scrypt`, `pbkdf2:sha256`), secure cookie serialization. | Built into Flask ecosystem; provides industry-standard cryptographic password hashing. | **Required** | BSD-3-Clause |
| **Jinja2** | 3.1.6 | `Jinja2==3.1.6` | Context-sensitive HTML template rendering engine. | Fast, secure templating with automatic HTML entity escaping preventing XSS attacks. | **Required** | BSD-3-Clause |
| **itsdangerous** | 2.2.0 | `itsdangerous==2.2.0` | Cryptographic data signing for sessions and CSRF tokens. | Ensures session tokens cannot be forged or modified by clients. | **Required** | BSD-3-Clause |
| **click** | 8.3.1 | `click==8.3.1` | Command line interface creation kit powering `flask` CLI commands. | Powers CLI management tools (`flask init-db`, `flask seed-demo`). | **Required** | BSD-3-Clause |
| **blinker** | 1.9.0 | `blinker==1.9.0` | Fast Python in-process signaling and event dispatching. | Enables Flask core request lifecycle signaling. | **Required** | MIT |
| **python-dotenv** | 1.2.2 | `python-dotenv==1.2.2`| Loads environment variables from `.env` into `os.environ`. | Adheres to 12-Factor App methodology for secrets and configuration isolation. | **Required** | BSD-3-Clause |
| **waitress** | 3.0.2 | `waitress==3.0.2` | Production-grade multi-threaded WSGI HTTP server for Python. | Cross-platform production WSGI server that operates reliably on both Windows and Linux without POSIX-only C extensions. | **Required** | ZPL 2.1 |
| **pytest** | 9.1.1 | `pytest==9.1.1` | Automated test runner and assertion framework. | Modern, robust test framework with fixture injection and clean test reporting. | **Development** | MIT |
| **pytest-cov** | 7.1.0 | `pytest-cov==7.1.0` | Pytest plugin for measuring code statement coverage. | Generates transparent statement-level coverage reports. | **Development** | MIT |
| **coverage** | 7.16.2 | `coverage==7.16.2` | Python code coverage measurement engine. | Powers `pytest-cov` statement tracking. | **Development** | Apache-2.0 |

---

## 2. Frontend Libraries & Content Delivery Networks (CDNs)

| Asset Name | Version | Loading Origin | Purpose | Integrity / Security Controls |
| :--- | :---: | :--- | :--- | :--- |
| **Bootstrap CSS** | 5.3.0 | `https://cdn.jsdelivr.net` | Responsive grid layout, buttons, cards, typography, forms. | Permitted in Content-Security-Policy header (`style-src 'self' https://cdn.jsdelivr.net`). |
| **Bootstrap Icons** | 1.10.5 | `https://cdn.jsdelivr.net` | Semantic vector iconography for buttons and status indicators. | Permitted in Content-Security-Policy header (`font-src 'self' https://cdn.jsdelivr.net`). |
| **Bootstrap JS** | 5.3.0 | `https://cdn.jsdelivr.net` | Interactive modal dialogues, dropdowns, and collapse navbar. | Permitted in Content-Security-Policy header (`script-src 'self' https://cdn.jsdelivr.net`). |
| **jQuery** | 3.7.1 | `https://code.jquery.com` | Accessible client-side form validation and character counters. | Permitted in Content-Security-Policy header (`script-src 'self' https://code.jquery.com`). |

---

## 3. Dependency Security & Maintenance Assessment

1. **Vulnerability Scans:** All installed dependencies were verified against known Python Security Advisories. No vulnerable versions of Flask, Werkzeug, or Jinja2 are present.
2. **Maintenance Policy:** Pin exact versions in `requirements.txt` for reproducible deployment builds. Quarterly automated dependency reviews recommended.
3. **Licensing Compliance:** All packages utilize permissive open-source licenses (BSD-3-Clause, MIT, Apache 2.0, ZPL 2.1), fully permitting academic, commercial, and community distribution.
