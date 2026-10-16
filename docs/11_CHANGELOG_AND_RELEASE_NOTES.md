# Changelog & Release Notes — LocalShare

All notable changes to the **LocalShare** platform are documented in this file in adherence to the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

---

## [2.0.0] — 2026-10-16

### Summary of Major Architectural Upgrade
Transformed the initial single-file proof-of-concept (`app.py`, 227 lines) into a modular, production-ready community mutual aid platform with an Application Factory architecture, SQLAlchemy 2.0 ORM, secure password hashing, full user-to-user exchange workflow, deterministic smart matching, trust and safety moderation, live community impact metrics, and 100% automated test verification.

### Added
- **Modular Monolith Structure:** Created application package (`app/`) with 6 distinct domain Blueprints: `auth`, `posts`, `exchange`, `matching`, `admin`, `main`.
- **Relational Domain Entities:** Introduced SQLAlchemy 2.0 models: `User`, `Post`, `ExchangeRequest`, `Report`, and `AuditLog`.
- **Database Schema Upgrades:** Created tables `exchange_requests`, `reports`, and `audit_logs`. Added `role`, `is_active`, `is_suspended`, and `updated_at` columns.
- **Automated Password Migration:** Implemented `app/migrations_helper.py` to transparently upgrade existing plaintext user accounts to Werkzeug Scrypt hashes upon system startup and on-demand during login.
- **Deterministic Smart Matching Engine:** Built 100-point explainable scoring algorithm evaluating post type compatibility, category relevance, Jaccard keyword overlap, and location proximity (`app/matching/engine.py`).
- **User-to-User Exchange Workflow:** Implemented interest requests, owner accept/decline actions, coordination notes, and handover completion tracking.
- **Trust & Safety Portal:** Implemented post reporting, user reporting, administrative moderation dashboard, user suspension, and immutable audit logging.
- **User Dashboard (`/dashboard`):** Created multi-tab personal dashboard tracking active posts, incoming requests, sent requests, and personalized recommendations.
- **Verified Community Impact Dashboard (`/impact`):** Live database metrics distinguishing verified completed exchanges from closed/cancelled listings.
- **Community Safety Guidelines (`/guidelines`):** Policy document specifying mutual aid principles, permitted vs prohibited goods, and handover safety.
- **Automated QA Test Suite:** Built comprehensive 34-test pytest suite with 72% coverage (`tests/test_*.py`).
- **Production DevOps Assets:** Added `wsgi.py`, `Procfile`, multi-stage `Dockerfile`, `docker-compose.yml`, `pytest.ini`, and `.env.example`.
- **Custom Error Handlers:** Added responsive, branded error templates for HTTP 400, 403, 404, and 500.

### Changed
- **Entry Points:** Refactored root `app.py` to instantiate `app = create_app('development')` and run automatic database schema migrations. Added `wsgi.py` for Waitress/Gunicorn execution.
- **Security Posture:** Eliminated hardcoded secret keys; disabled Flask debug mode in production; attached security headers (`X-Frame-Options`, `nosniff`, `CSP`); implemented sliding-window rate limiting on `/login`.
- **State Mutation Semantics:** Replaced insecure `GET /post/close/<id>` route with authenticated, CSRF-protected `POST /post/<id>/status` and `POST /post/<id>/delete` endpoints.
- **Frontend Templates & Styling:** Upgraded all templates to accessible HTML5, responsive Bootstrap 5 grids, semantic ARIA attributes, and visible focus rings.

### Fixed
- **Plaintext Password Storage:** Remediated critical vulnerability where user passwords were saved in raw text. All credentials are now salted and hashed with Scrypt.
- **CSRF Vulnerability:** Integrated cryptographic CSRF session tokens on all browser form submissions.
- **Unvalidated Input:** Enforced server-side length and type validation across all user inputs.

---

## [1.0.0] — Initial Prototype Baseline
- Single-file monolithic script `app.py` using raw SQLite queries.
- Basic registration, session login, post listing, and closing.
- Hardcoded secret key and debug mode enabled.
- Plaintext passwords stored in SQLite database.
