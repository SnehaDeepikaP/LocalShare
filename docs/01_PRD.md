# Product Requirements Document (PRD) — LocalShare

**Document Identifier:** PRD-LS-2026-V2.0  
**Status:** Implemented & Verified Baseline  
**Target Release:** LocalShare Production v2.0.0  
**Author:** Antigravity Senior Engineering & Product Architecture Team  

---

## 1. Product Overview & Problem Statement

### 1.1 Executive Summary
Local communities often suffer from an artificial scarcity of resources. While some households possess surplus goods—such as outgrown children's clothing, finished textbooks, excess food, and underutilized tools—other neighbours nearby urgently require those exact items. Commercial marketplaces (e.g., eBay, OLX, Craigslist) introduce transaction fees, shipping delays, and security risks, and are ill-suited for non-monetary mutual aid and emergency local assistance.

**LocalShare** is a localized, non-monetary community resource-sharing platform engineered to connect neighbours who need assistance with those who can provide it. It fosters social resilience, minimizes household waste, and democratizes mutual aid through an explainable smart matching engine and a safe, privacy-preserving exchange workflow.

### 1.2 Target Audience & User Personas
1. **Persona 1: Community Giver (Priya)**
   - *Demographics:* 34, working parent in an urban neighbourhood.
   - *Goals:* Share outgrown children's clothes, educational toys, and weekend meals with neighbours who genuinely need them.
   - *Pain Points:* Frustrated by commercial classifieds where buyers haggle; values privacy and does not want her phone number or exact flat address visible to the public.
2. **Persona 2: Community Seeker (Rahul)**
   - *Demographics:* 19, student preparing for board exams.
   - *Goals:* Access textbooks, reference guides, and shared study materials without incurring heavy costs.
   - *Pain Points:* Difficulty knowing which neighbour has spare books; wants a transparent matching interface that notifies him when complementary items appear.
3. **Persona 3: Community Moderator & Platform Admin (Sneha)**
   - *Demographics:* Local community volunteer lead.
   - *Goals:* Ensure platform safety, moderate spam or prohibited items (e.g. hazardous materials, commercial ads), and track community impact.
   - *Pain Points:* Needs a dashboard to review reports, audit moderation actions, and suspend malicious actors.

---

## 2. Product Vision & Goals

### 2.1 Core Pillars
- **Non-Monetary Mutual Aid:** Strictly 100% free community sharing; no currency, fees, or bartering points.
- **Privacy by Default:** Zero public exposure of private home addresses, phone numbers, or passwords.
- **Explainable Smart Matching:** A transparent, deterministic scoring algorithm that recommends relevant exchanges and articulates *why* each match was suggested.
- **Verifiable Community Impact:** Live, database-backed metrics tracking active posts, completed handovers, and category distribution.

### 2.2 Scope & Boundaries
- **In-Scope (Implemented):**
  - Secure authentication with Werkzeug password hashing and auto-migration of legacy accounts.
  - CRUD post lifecycle (Offers & Requests) across 5 core categories (`Food`, `Clothes`, `Books`, `Services`, `Other`).
  - Search, multi-criteria filtering, sorting, and pagination.
  - Full user-to-user interest request, acceptance, and completion tracking.
  - Deterministic smart matching algorithm with explainable factor breakdown.
  - Trust and safety features: post/user reporting, administrative moderation queue, account suspension, audit logging.
  - Verified Community Impact Dashboard and Community Guidelines.
- **Out-of-Scope (Won't / Future Roadmap):**
  - Monetary payments, cryptocurrency, or paid delivery tracking (explicitly prohibited).
  - Real-time WebSockets group video/voice chat (privacy-preserving contact exchange implemented instead).

---

## 3. Feature Priorities (MoSCoW Framework)

| Priority | ID | Feature Description | Status |
| :--- | :--- | :--- | :--- |
| **Must Have** | FR-001 | Secure User Authentication (Scrypt/PBKDF2 hashing, rate limiting, session security) | **Implemented** |
| **Must Have** | FR-002 | Post Management (Create, browse, filter, edit, delete, close, reopen) | **Implemented** |
| **Must Have** | FR-003 | Post Lifecycle & Status Transitions (`open`, `in_progress`, `completed`, `closed`) | **Implemented** |
| **Must Have** | FR-004 | User-to-User Interest Request & Handover Workflow | **Implemented** |
| **Must Have** | FR-005 | Deterministic Smart Matching Engine with Explainable Breakdown | **Implemented** |
| **Must Have** | FR-006 | Trust & Safety (Report Post/User, Admin Moderation, User Suspension) | **Implemented** |
| **Must Have** | FR-007 | Database-Backed Community Impact Dashboard (distinguishing closed vs completed) | **Implemented** |
| **Must Have** | FR-008 | Administrative Dashboard with Audit Logging | **Implemented** |
| **Should Have**| FR-009 | Keyword Search and Pagination across result sets | **Implemented** |
| **Should Have**| FR-010 | Profile Management & In-App Password Changing | **Implemented** |
| **Could Have** | FR-011 | Email notifications via SMTP integration | *Planned (Documented in Runbook)* |
| **Won't Have**  | FR-012 | In-app credit card payment gateway | *Out of Scope by Design* |

---

## 4. Functional Requirements (FR)

### FR-001: Authentication & User Accounts
- **FR-001.1:** System shall securely hash passwords using Werkzeug `generate_password_hash` prior to database persistence. Plaintext passwords must never be stored.
- **FR-001.2:** Existing database accounts with plaintext credentials must be transparently upgraded to secure hashes upon login verification.
- **FR-001.3:** System shall enforce login rate limiting (max 5 failed attempts per 5-minute sliding window per client IP/email).
- **FR-001.4:** Suspended accounts shall be blocked from logging in with a clear explanation message.
- **FR-001.5:** User sessions must use `HttpOnly`, `SameSite=Lax`, and `Secure` cookie attributes in production.

### FR-002: Offers & Requests (Posts)
- **FR-002.1:** Authenticated users can author posts designating `post_type` (`offer` or `request`), `category` (`Food`, `Clothes`, `Books`, `Services`, `Other`), `title` (4–200 characters), `description` (min 10 characters), and `location` (general area).
- **FR-002.2:** Only the post author or an administrator can edit, close, reopen, or delete a post.
- **FR-002.3:** Public browse view (`/posts`) provides keyword text search, category filtering, type filtering, location substring filtering, sorting, and pagination (6 items per page).

### FR-003: User-to-User Exchange Workflow
- **FR-003.1:** A logged-in user can submit an interest request on any open post not authored by themselves.
- **FR-003.2:** System prevents duplicate active requests for the same post by the same user.
- **FR-003.3:** The post author receives incoming requests in their dashboard and can `Accept` (with optional coordination notes) or `Decline`.
- **FR-003.4:** When accepted, safe coordination details are unlocked between participants.
- **FR-003.5:** Either participant can mark the exchange as `Completed`, updating post status and incrementing verified impact metrics.

### FR-004: Deterministic Smart Matching
- **FR-004.1:** System evaluates candidate open posts against a target post using a deterministic 100-point algorithm:
  - *Complementary Type:* Opposing types (`request` &harr; `offer`) = 40 pts. Same type = 0 pts.
  - *Category Relevance:* Exact match = 30 pts. Different = 0 pts.
  - *Keyword Overlap:* Jaccard token similarity scaled up to 20 pts (min 5 pts on token intersection).
  - *Location Proximity:* Exact match = 10 pts; Substring match = 8 pts; Keyword overlap = 5 pts.
- **FR-004.2:** Ineligible posts (closed, completed, author's own posts, suspended users) are strictly excluded (Score = 0).
- **FR-004.3:** Recommendations provide an explainable factor breakdown showing point allocations and reasons.

### FR-005: Trust, Safety & Administration
- **FR-005.1:** Users can report inappropriate posts or users with a categorized reason (`spam`, `inappropriate`, `scam`, `harassment`, `other`) and description.
- **FR-005.2:** Administrators access a dedicated `/admin` portal to review open reports, suspend/restore users, moderate posts, and inspect immutable audit logs.
- **FR-005.3:** Every administrative action is logged in `audit_logs` with admin ID, action name, target type/ID, and timestamp.

---

## 5. Non-Functional Requirements (NFR)

- **NFR-001 (Security):** Zero stored plaintext credentials; signed CSRF protection on all mutating HTTP methods; parameterized queries preventing SQL injection; Jinja HTML auto-escaping preventing XSS; enterprise security response headers attached.
- **NFR-002 (Performance):** Page generation response time under 150ms for local SQLite operations and under 300ms for paginated queries.
- **NFR-003 (Usability & Accessibility):** WCAG 2.1 AA compliant form labels, color contrast ratios, keyboard tab navigation, and responsive layouts across desktop, tablet, and mobile devices.
- **NFR-004 (Reliability):** 100% backward compatibility with existing `localshare.db` databases; persistent database storage; automated recovery via health checks (`/health`).

---

## 6. Success Metrics & Key Performance Indicators (KPIs)

1. **Exchange Completion Rate:** `(Completed Exchanges / Total Active Posts) * 100`. Target: > 35%.
2. **Match Relevance:** Precision of recommended posts meeting user acceptance criteria. Target: > 75% compatibility.
3. **Safety Index:** Percentage of community reports resolved within 24 hours. Target: > 90%.
4. **Platform Reliability:** Automated test pass rate = 100% (Verified: 34/34 passing).
