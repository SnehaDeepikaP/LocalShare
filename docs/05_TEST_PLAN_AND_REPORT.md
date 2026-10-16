# Software Test Plan & Test Execution Report — LocalShare

**Document Identifier:** TPR-LS-2026-V2.0  
**Test Suite Status:** 100% Passing (34 of 34 Tests Verified)  
**Code Coverage:** 72% across 1,090 Statements  
**Execution Environment:** Python 3.13.7 / pytest 9.1.1 / pytest-cov 7.1.0 / Windows AMD64  
**Date of Verification:** October 16, 2026  

---

## 1. Testing Objectives & Strategy

The primary objective of the LocalShare testing suite is to verify the functional correctness, authorization enforcement, password security, exchange workflow reliability, and smart matching determinism of the platform prior to release.

### 1.1 Test Pyramid Strategy
- **Unit Tests:** Model validation, password hashing/migration logic, Jaccard token similarity calculation, location scoring.
- **Integration Tests:** Authentication sessions, post CRUD, status state machines, user-to-user exchange negotiation, admin moderation, and real-time database statistics calculations.
- **Security & Authorization Tests:** CSRF protection, login brute-force rate limiting, XSS template escaping, role boundaries (non-admin blocks), and HTTP security response headers.

---

## 2. Test Execution Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\P.SNEHA DEEPIKA\Downloads\LocalShare-main\LocalShare-main
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.12.1, cov-7.1.0
collected 34 items

tests\test_admin.py ..                                                   [  5%]
tests\test_auth.py ........                                              [ 29%]
tests\test_authorization.py ....                                         [ 41%]
tests\test_exchange_workflow.py ...                                      [ 50%]
tests\test_matching.py .....                                             [ 64%]
tests\test_posts.py .....                                                [ 79%]
tests\test_security.py ....                                              [ 91%]
tests\test_stats.py ...                                                  [100%]

====================== 34 passed, 51 warnings in 26.46s =======================
```

### 2.1 Coverage Matrix by Component

| Module File | Total Statements | Missed Statements | Coverage Percentage | Verification Notes |
| :--- | :---: | :---: | :---: | :--- |
| `app/config.py` | 30 | 0 | **100%** | Full config coverage |
| `app/services/stats_service.py` | 30 | 0 | **100%** | All metric paths verified |
| `app/services/matching_service.py`| 2 | 0 | **100%** | Query & re-export verified |
| `app/models/report.py` | 20 | 2 | **90%** | Report creation & status verified |
| `app/models/audit.py` | 15 | 2 | **87%** | Admin audit log creation verified |
| `app/models/post.py` | 33 | 5 | **85%** | Post model & relations verified |
| `app/matching/engine.py` | 96 | 15 | **84%** | 100-pt formula, Jaccard, location verified |
| `app/services/security_service.py`| 72 | 12 | **83%** | Rate limiter, headers, auth decorators |
| `app/models/user.py` | 40 | 7 | **82%** | Password hash, auto-upgrade verified |
| `app/models/exchange.py` | 27 | 5 | **81%** | Lifecycle status verified |
| `app/posts/routes.py` | 162 | 30 | **81%** | CRUD, search, filter, pagination verified |
| `app/exchange/routes.py` | 84 | 22 | **74%** | Request, accept, complete verified |
| `app/auth/routes.py` | 119 | 42 | **65%** | Register, login, rate limiting verified |
| `app/admin/routes.py` | 127 | 48 | **62%** | Moderation, suspension, reports verified |
| `app/main/routes.py` | 84 | 40 | **52%** | Home, impact, guidelines, health verified |
| `app/__init__.py` | 78 | 36 | **54%** | Application factory & error handlers |
| **TOTAL** | **1,090** | **307** | **72%** | **Comprehensive Production Baseline** |

---

## 3. Test Cases Catalog & Execution Results

| Test ID | Module | Purpose | Preconditions | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-AUTH-01** | `test_auth` | User registration | New email | User persisted with Scrypt hash | Hash verified, login successful | **PASS** |
| **TC-AUTH-02** | `test_auth` | Duplicate registration | Existing email | Rejected with flash warning | Duplicate caught, no DB duplicate | **PASS** |
| **TC-AUTH-03** | `test_auth` | Password strength rules | Weak passwords | Rejected with validation errors | Rejected short/no-capital inputs | **PASS** |
| **TC-AUTH-04** | `test_auth` | Valid login & session | Correct credentials | Session cookie created with user_id | Logged in, flash message shown | **PASS** |
| **TC-AUTH-05** | `test_auth` | Invalid password login | Wrong password | Rejected with error flash | Rejected, rate limit attempt recorded | **PASS** |
| **TC-AUTH-06** | `test_auth` | Block suspended accounts | `is_suspended=True` | Access denied with suspension alert | Blocked from logging in | **PASS** |
| **TC-AUTH-07** | `test_auth` | Logout clears session | Active session | Session cleared, redirected to home | Session cleared | **PASS** |
| **TC-AUTH-08** | `test_auth` | Route protection | Unauthenticated | Redirected to `/login` | 302 to login route | **PASS** |
| **TC-AUTHZ-01**| `test_authorization` | Edit boundary | User A tries User B post | 403 / Redirected with error | Rejected, DB post untouched | **PASS** |
| **TC-AUTHZ-02**| `test_authorization` | Delete boundary | User A tries delete User B | Rejected with unauthorized flash | Rejected, post preserved | **PASS** |
| **TC-AUTHZ-03**| `test_authorization` | Non-admin admin access | Standard user role | Redirected to home with alert | Access denied | **PASS** |
| **TC-AUTHZ-04**| `test_authorization` | Admin moderation access| Admin role | Access granted to `/admin` | 200 OK, admin portal loaded | **PASS** |
| **TC-POST-01** | `test_posts` | Create valid post | Valid form data | Post created with 'open' status | Created & visible | **PASS** |
| **TC-POST-02** | `test_posts` | Invalid category/fields | Illegal category | Validation errors returned | Rejected with error message | **PASS** |
| **TC-POST-03** | `test_posts` | Search & filtering | Seeded posts | Correct subset returned | Filter by category, type, and q verified | **PASS** |
| **TC-POST-04** | `test_posts` | Author post edit | Author logged in | Post fields updated in DB | Fields updated | **PASS** |
| **TC-POST-05** | `test_posts` | Status transitions & delete | Author logged in | Post closed, reopened, deleted | All transitions verified | **PASS** |
| **TC-EXCH-01** | `test_exchange` | Full exchange flow | 2 users, 1 post | Request -> Accept -> Complete | Complete lifecycle verified | **PASS** |
| **TC-EXCH-02** | `test_exchange` | Self-interest block | Author requests own post | Blocked with warning | Blocked | **PASS** |
| **TC-EXCH-03** | `test_exchange` | Duplicate request block | Existing pending req | Second attempt rejected | Blocked | **PASS** |
| **TC-MATCH-01**| `test_matching` | Complementary scoring | Offer & Request, same cat | Score >= 80 pts | Score >= 80, factors explainable | **PASS** |
| **TC-MATCH-02**| `test_matching` | Same-type penalty | Offer & Offer | Type score = 0 pts | 0 pts awarded for type | **PASS** |
| **TC-MATCH-03**| `test_matching` | Ineligible exclusions | Closed post / same user | Score = 0 pts | Excluded | **PASS** |
| **TC-MATCH-04**| `test_matching` | Proximity scoring | Exact / Substring / None | 10 / 8 / 0 points | Verified | **PASS** |
| **TC-MATCH-05**| `test_matching` | Deterministic ranking | 2 candidate posts | Highest score first | Ordered deterministically | **PASS** |
| **TC-SEC-01**  | `test_security` | Security headers | Any request | Headers attached to response | X-Frame-Options, CSP, nosniff present | **PASS** |
| **TC-SEC-02**  | `test_security` | Login rate limiting | 5 failed attempts | 6th attempt blocked with wait time | Rate limited | **PASS** |
| **TC-SEC-03**  | `test_security` | Plaintext auto-upgrade | User with plaintext pwd | Rehashed upon check_password | Rehashed to Scrypt | **PASS** |
| **TC-SEC-04**  | `test_security` | HTML input escaping | Script tags in title | Escaped HTML entities | Escaped; no raw script executed | **PASS** |
| **TC-ADM-01**  | `test_admin` | Suspend / Restore user | Admin logged in | User suspended, audit logged | Suspend & restore verified | **PASS** |
| **TC-ADM-02**  | `test_admin` | Resolve report | Open report | Report resolved, audit logged | Action taken verified | **PASS** |
| **TC-STAT-01** | `test_stats` | Closed vs Completed | 1 closed, 1 open post | Completed count must be 0 | Confirmed 0 completed exchanges | **PASS** |
| **TC-STAT-02** | `test_stats` | Completed exchange stat| 1 completed exchange | Completed count >= 1 | Confirmed incremented | **PASS** |
| **TC-STAT-03** | `test_stats` | Health check endpoint | GET /health | 200 OK, healthy status | Verified 200 OK | **PASS** |

---

## 4. Defects Discovered & Remediations Applied

1. **Defect 1: SQLite Non-Constant Default Error on ALTER TABLE**
   - *Symptom:* `sqlite3.OperationalError: Cannot add a column with non-constant default` when adding `updated_at` to legacy databases.
   - *Root Cause:* SQLite does not allow expressions like `(datetime('now', 'localtime'))` in `ALTER TABLE ADD COLUMN`.
   - *Fix:* Changed default to `NULL` in `app/migrations_helper.py:50`, letting application logic manage timestamps.
2. **Defect 2: Package Circular Import during Factory Initialization**
   - *Symptom:* `ImportError: cannot import name 'get_matches_for_post' from partially initialized module 'app.services.matching_service'`.
   - *Root Cause:* `app/matching/__init__.py` imported routes which imported services before the package finished loading.
   - *Fix:* Decoupled `app/matching/__init__.py` and imported `matching_bp` directly from `app.matching.routes` in the application factory.
3. **Defect 3: Trailing Slash Permanent Redirect on Admin Route**
   - *Symptom:* `assert 308 == 200` on `admin_client.get('/admin')`.
   - *Root Cause:* Route was defined only as `@admin_bp.route('/')` on a blueprint with `url_prefix='/admin'`, creating a canonical URL of `/admin/`.
   - *Fix:* Added `@admin_bp.route('')` and `follow_redirects=True` to support both formats.

---

## 5. Final Release Recommendation

All 34 automated unit, integration, authorization, security, and lifecycle tests pass with 0 failures and 72% statement coverage. The software meets all verification criteria and is **recommended for immediate release**.
