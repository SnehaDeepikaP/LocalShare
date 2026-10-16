# Security & Privacy Policy Specification — LocalShare

**Document Identifier:** SPS-LS-2026-V2.0  
**Security Posture:** Hardened Production Baseline  
**Auditor:** Antigravity Cybersecurity & Privacy Engineering Group  

---

## 1. Threat Model & STRIDE Analysis

| Threat Category | Potential Attack Vector | Implemented Countermeasure | Verification Status |
| :--- | :--- | :--- | :---: |
| **Spoofing** | Forging user sessions or impersonating admins | Cryptographically random `SECRET_KEY` from env; signed session cookies; role-based `@admin_required` checks. | **Verified** |
| **Tampering** | Modifying other users' posts or exchange requests | Server-side authorization checks verifying `post.user_id == session['user_id']`. Parameterized ORM queries. | **Verified** |
| **Repudiation** | Denying administrative actions or content removal | Immutable `AuditLog` records containing admin ID, action name, target type/ID, and UTC timestamp. | **Verified** |
| **Information Disclosure** | Exposing private passwords, phone numbers, or addresses | Werkzeug Scrypt/PBKDF2 hashing; contact details withheld until request accepted; no precise street addresses collected. | **Verified** |
| **Denial of Service** | Credential stuffing and brute-force password guessing | In-memory sliding-window rate limiting (max 5 failed attempts per 300s window per IP/email). | **Verified** |
| **Elevation of Privilege** | Standard user triggering admin moderation endpoints | Server-side role check inspecting `session['role'] == 'admin'` on every admin route. | **Verified** |

---

## 2. Cryptographic Architecture & Password Management

1. **Password Hashing:**
   - Werkzeug `generate_password_hash` generates salt and hashes using Scrypt / PBKDF2:SHA256 (`scrypt:32768:8:1$...`).
   - Plaintext passwords are never stored in memory longer than necessary for authentication verification.
2. **Transparent Legacy Account Migration:**
   - If an existing database contains legacy plaintext credentials, `User.check_password` matches the plaintext string, immediately hashes it via `set_password()`, commits the updated hash to the database, and completes the login transparently.
   - Verified via unit test `test_legacy_plaintext_password_auto_upgrade`.

---

## 3. Web Application Security Controls

### 3.1 CSRF (Cross-Site Request Forgery)
- Session-bound cryptographic tokens generated via `os.urandom(32).hex()`.
- Validated on all state-mutating requests (`POST`, `PUT`, `DELETE`, `PATCH`).
- Prevents cross-origin forged requests from closing or deleting user posts.

### 3.2 Cross-Site Scripting (XSS)
- Jinja2 auto-escapes all context-rendered HTML variables by default.
- Tested and verified with injection strings `<script>alert("XSS")</script>` rendering as `&lt;script&gt;`.

### 3.3 Security Response Headers
Attached on every HTTP response via `@app.after_request`:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net https://code.jquery.com 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; font-src 'self' https://cdn.jsdelivr.net; img-src 'self' data: https:;
```

---

## 4. Privacy & Data Protection Architecture

1. **Minimization of Personal Data:**
   - The platform collects only: Full Name, Email Address, Password, and General City/Municipality.
   - Exact home flat numbers or GPS coordinates are explicitly excluded from public listings.
2. **Coordination Data Confidentiality:**
   - The optional `contact_info` provided during an interest request is stored in `exchange_requests` and revealed *only* after the post author explicitly clicks `Accept`.
3. **Data Retention & Deletion:**
   - Deleting a post cascades and permanently deletes all associated exchange requests and report records.
   - Account deletion or deactivation purges active listings from the matching index.

---

## 5. Production Security Checklist

- [x] Flask `DEBUG` mode is disabled in production (`FLASK_DEBUG=false`).
- [x] `SECRET_KEY` is loaded exclusively from environment variables.
- [x] Passwords hashed with Scrypt/PBKDF2.
- [x] CSRF protection enabled on all browser forms.
- [x] Rate limiting active on `/login`.
- [x] Security headers attached to all HTTP responses.
- [x] `SESSION_COOKIE_SECURE=True` enforced under HTTPS.
- [x] No secrets committed to git repository (`.gitignore` excludes `.env` and `*.db`).
- [x] Production server executed under non-root user in Docker container.
- [x] Health check endpoint does not leak stack traces or sensitive credentials.
