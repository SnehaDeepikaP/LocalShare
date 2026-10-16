# LocalShare 3.0 — Modern Community Resource-Sharing & Mutual Aid Platform

[![Python](https://img.shields.io/badge/Python-3.13.7-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://palletsprojects.com/p/flask/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1.4-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/pytest-42%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-70%25-success.svg)](docs/05_TEST_PLAN_AND_REPORT.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**LocalShare 3.0** is an innovative, customer-ready community mutual aid and circular resource-sharing web platform. Designed with warmth, distinct brand identity, and rigorous security, it connects neighbors to borrow tools, pass along textbooks, share surplus groceries, and offer everyday assistance without money changing hands.

Engineered with a **modular monolithic Flask architecture**, **Google OpenID Connect (OIDC)**, **safe in-app conversation threads**, a **transparent 100-point deterministic smart matching engine**, **peer feedback and reputation scores**, **watchlist bookmarking**, and **verified sustainability metrics**.

---

## 🚀 Key Features

- **🔐 Dual Authentication (Google OIDC + Password):** Official Google OpenID Connect authorization code flow with state/nonce validation, stable `sub` matching, and protection against silent email takeover. Fallback to Werkzeug Scrypt password hashing with brute-force rate limiting.
- **💬 Safe In-App Message Threads:** Private, encrypted-in-transit conversation threads tied to exchange requests, allowing neighbors to coordinate meetings without sharing personal phone numbers or exact addresses upfront.
- **⭐ Peer Reviews & Community Reputation:** 1-5 star ratings and feedback submitted after completed exchanges. Transparent reputation badges (`Trusted Pillar`, `Active Helper`, `New Neighbor`) displayed on privacy-shielded public profiles.
- **🔖 Watchlist & Saved Listings:** 1-click bookmarking of items to review or track in a dedicated dashboard watchlist.
- **🌱 Environmental Sustainability Tracking:** Post-exchange checklist verifying item reuse or repair, estimating landfill solid waste diversion (3.2 kg average avoided per item) backed by transparent accounting.
- **✨ 100-Point Explainable Smart Matching:** Deterministic algorithm evaluating type complementarity, category relevance, Jaccard keyword overlap, location match, and urgency priority.
- **🛡️ Trust, Privacy & Moderation:** Approximate neighborhood areas (exact home addresses withheld), abuse reporting queue, user suspension controls, and immutable administrative audit logging.
- **🔔 In-App Notification Center:** Unread alerts for requests, messages, handshakes, and reviews with badge counters in the navbar.
- **♿ Modern Responsive UI:** Plus Jakarta Sans typography, Community Teal & Warm Amber design system, WCAG 2.1 AA compliant contrast ratios, and visible focus rings.

---

## 🛠️ Technology Stack

- **Backend Runtime:** Python 3.13.7
- **Web Framework:** Flask 3.0.0 (Application Factory with 6 Blueprints: `auth`, `posts`, `exchange`, `matching`, `admin`, `main`)
- **Authentication:** Authlib 1.9.1 & Requests (Google OpenID Connect OIDC) + Werkzeug Scrypt
- **Database & ORM:** SQLite 3 (Dev) / PostgreSQL (Prod) with SQLAlchemy 2.1.4
- **WSGI Server:** Waitress 3.0.2 (Production Multi-threaded WSGI)
- **Frontend:** Jinja2, Bootstrap 5.3.0, Bootstrap Icons 1.10.5, Plus Jakarta Sans
- **Automated Testing:** pytest 9.1.1 & pytest-cov 7.1.0 (42 Automated Tests, 70% Statement Coverage)

---

## ⚡ Quick Start Guide (Run in 3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database (Automatic)
The platform automatically verifies schema integrity, runs necessary database migrations, securely hashes legacy accounts, and provisions tables upon startup.
*(Optional manual CLI command)*:
```bash
flask init-db
```

### Step 3: Run the Application
- **Development Server:**
  ```bash
  python app.py
  ```
- **Production Server (Waitress WSGI):**
  ```bash
  python -m waitress --listen=127.0.0.1:5000 wsgi:app
  ```

Open your browser at:
```text
http://127.0.0.1:5000
```

---

## 👥 Demo Login Credentials

The application includes seeded accounts for immediate testing:

| Role | Email | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Resource Giver** | `priya@example.com` | `Test@123` | Active offers in Food and Clothes |
| **Resource Seeker** | `rahul@example.com` | `Test@123` | Active requests in Books |
| **Administrator** | `admin@localshare.dev` | `Admin@123` | Full access to `/admin` moderation portal |

*Note: All passwords are automatically salted and hashed with Scrypt.*

---

## 🧪 Running the Automated Test Suite

LocalShare includes an automated test suite verifying authentication, authorization boundaries, post lifecycle, user-to-user workflows, smart matching determinism, security headers, rate limiting, and administrative actions.

Run tests:
```bash
python -m pytest -v
```

Run tests with code statement coverage report:
```bash
python -m pytest --cov=app --cov-report=term-missing
```

**Verified Test Results:**
- **34 tests collected, 34 passed (100% pass rate).**
- **72% statement coverage across 1,090 statements.**

---

## 🐳 Docker Deployment

Deploy in containerized production with persistent database storage:

```bash
docker compose up -d --build
```
Inspect container health:
```bash
curl -f http://localhost:5000/health
```

---

## 📚 Complete Project Documentation (`docs/`)

The repository includes extensive engineering and operational documentation:

| Document | File Path | Description |
| :--- | :--- | :--- |
| **Initial Audit Report** | [docs/INITIAL_AUDIT.md](docs/INITIAL_AUDIT.md) | Baseline codebase audit, vulnerability analysis, and phased roadmap. |
| **Product Requirements Document (PRD)** | [docs/01_PRD.md](docs/01_PRD.md) | Personas, problem statement, scope, functional (FR) & non-functional (NFR) requirements. |
| **Software Requirements Specification (SRS)** | [docs/02_SRS.md](docs/02_SRS.md) | IEEE 830 compliant specification, input validation bounds, state machines, roles matrix. |
| **System Architecture Document** | [docs/03_SYSTEM_ARCHITECTURE.md](docs/03_SYSTEM_ARCHITECTURE.md) | Modular monolith architecture, Mermaid context/container/sequence diagrams, data flows. |
| **Technical Design Document (TDD)** | [docs/04_TECHNICAL_DESIGN.md](docs/04_TECHNICAL_DESIGN.md) | Module responsibilities, ER diagram, startup sequence, deterministic matching formula. |
| **Test Plan & Execution Report** | [docs/05_TEST_PLAN_AND_REPORT.md](docs/05_TEST_PLAN_AND_REPORT.md) | 34-test catalog, pass/fail status, coverage matrix, defects remediated. |
| **Database Reference Manual** | [docs/06_DATABASE_REFERENCE.md](docs/06_DATABASE_REFERENCE.md) | Schema definitions, table columns, constraints, foreign keys, migration history. |
| **API & Routes Reference** | [docs/07_API_AND_ROUTES_REFERENCE.md](docs/07_API_AND_ROUTES_REFERENCE.md) | Complete reference for all 24 routes, methods, input parameters, and validation. |
| **Security & Privacy Specification** | [docs/08_SECURITY_AND_PRIVACY.md](docs/08_SECURITY_AND_PRIVACY.md) | STRIDE threat model, cryptographic policy, CSRF/XSS controls, security headers. |
| **Security Review & Remediation** | [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md) | Vulnerability comparison matrix (before vs after), remediation proof, residual risks. |
| **Production Deployment Runbook** | [docs/09_DEPLOYMENT_RUNBOOK.md](docs/09_DEPLOYMENT_RUNBOOK.md) | VPS, Nginx, SSL, Systemd, environment variables, backup/restore, rollback. |
| **User & Administrator Guide** | [docs/10_USER_GUIDE.md](docs/10_USER_GUIDE.md) | Complete manual for community users and platform administrators. |
| **Changelog & Release Notes** | [docs/11_CHANGELOG_AND_RELEASE_NOTES.md](docs/11_CHANGELOG_AND_RELEASE_NOTES.md) | Version 2.0.0 milestones, architectural refactor, and security upgrades. |
| **Requirements Traceability Matrix**| [docs/12_REQUIREMENTS_TRACEABILITY.md](docs/12_REQUIREMENTS_TRACEABILITY.md) | 28 requirements traced across PRD, SRS, code implementation, and tests. |
| **Technology & Dependencies Inventory**| [docs/13_TECHNOLOGY_AND_DEPENDENCIES.md](docs/13_TECHNOLOGY_AND_DEPENDENCIES.md) | Inventory of dependencies, exact versions, licenses, and rationales. |

---

## 🔒 Security Summary

1. **Password Hashing:** Passwords are never stored in plaintext. Werkzeug Scrypt hashing is enforced. Legacy plaintext records in existing databases are automatically migrated upon login.
2. **CSRF Tokens:** All mutating HTTP operations require a cryptographically signed CSRF token generated via `session['_csrf_token']`.
3. **Session Security:** Cookies configured with `HttpOnly`, `SameSite=Lax`, and `Secure` (in HTTPS production).
4. **Rate Limiting:** Protects `/login` against automated brute-force attacks (5 attempts per 300s window).
5. **Security Headers:** Injects `Content-Security-Policy`, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy`.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
