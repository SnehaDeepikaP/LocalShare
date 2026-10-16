# Requirements Traceability Matrix (RTM) — LocalShare

**Document Identifier:** RTM-LS-2026-V2.0  
**Verification Scope:** PRD Requirements &harr; SRS Specifications &harr; Implementation Files &harr; Automated Test Cases  
**Suite Pass Rate:** 100% (34 of 34 Tests Verified)  

---

## 1. Traceability Matrix

| PRD Req ID | SRS Req ID | Feature Requirement | Implementation File(s) & Function(s) | Test Case ID | Test Result |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **FR-001.1** | **SRS-3.1** | Werkzeug Scrypt Password Hashing | `app/models/user.py:set_password` | `TC-AUTH-01` | **PASS** |
| **FR-001.2** | **SRS-5.1** | Transparent Legacy Plaintext Upgrade | `app/models/user.py:check_password` | `TC-SEC-03` | **PASS** |
| **FR-001.3** | **SRS-5.3** | Login Brute-Force Rate Limiting | `app/services/security_service.py:is_rate_limited` | `TC-SEC-02` | **PASS** |
| **FR-001.4** | **SRS-2.2** | Block Suspended Users at Login | `app/auth/routes.py:login` | `TC-AUTH-06` | **PASS** |
| **FR-001.5** | **SRS-5.5** | Session Cookie Security Settings | `app/config.py:Config` | `TC-AUTH-04` | **PASS** |
| **FR-002.1** | **SRS-3.1** | Post Authoring & Field Validation | `app/posts/routes.py:new_post` | `TC-POST-01`, `TC-POST-02` | **PASS** |
| **FR-002.2** | **SRS-2.2** | Post Ownership & Authorization Guard | `app/posts/routes.py:edit_post`, `delete_post` | `TC-AUTHZ-01`, `TC-AUTHZ-02` | **PASS** |
| **FR-002.3** | **SRS-3.1** | Search, Multi-Filter, Sorting & Pagination | `app/posts/routes.py:posts` | `TC-POST-03` | **PASS** |
| **FR-003.1** | **SRS-3.3** | Submit Interest / Exchange Request | `app/exchange/routes.py:create_request` | `TC-EXCH-01` | **PASS** |
| **FR-003.2** | **SRS-3.3** | Prevent Self-Interest on Own Post | `app/exchange/routes.py:create_request` | `TC-EXCH-02` | **PASS** |
| **FR-003.3** | **SRS-3.3** | Prevent Duplicate Pending Requests | `app/exchange/routes.py:create_request` | `TC-EXCH-03` | **PASS** |
| **FR-003.4** | **SRS-3.3** | Author Accept/Decline Coordination | `app/exchange/routes.py:respond_request` | `TC-EXCH-01` | **PASS** |
| **FR-003.5** | **SRS-3.3** | Mark Exchange Completed & Update Post | `app/exchange/routes.py:complete_exchange` | `TC-EXCH-01`, `TC-STAT-02` | **PASS** |
| **FR-004.1** | **SRS-4.1** | Deterministic 100-Point Match Scoring | `app/matching/engine.py:calculate_match_score` | `TC-MATCH-01` | **PASS** |
| **FR-004.2** | **SRS-4.1** | Ineligible Posts Exclusion (Closed/Self) | `app/matching/engine.py:calculate_match_score` | `TC-MATCH-03` | **PASS** |
| **FR-004.3** | **SRS-4.1** | Explainable Factor Breakdown | `app/matching/engine.py:calculate_match_score` | `TC-MATCH-01` | **PASS** |
| **FR-004.4** | **SRS-4.2** | Proximity and Deterministic Ranking | `app/matching/engine.py:rank_matches` | `TC-MATCH-04`, `TC-MATCH-05` | **PASS** |
| **FR-005.1** | **SRS-3.1** | Community Post & User Reporting | `app/main/routes.py:report_post`, `report_user` | `TC-ADM-02` | **PASS** |
| **FR-005.2** | **SRS-2.2** | Admin Role Gate & Privilege Protection | `app/services/security_service.py:admin_required` | `TC-AUTHZ-03`, `TC-AUTHZ-04` | **PASS** |
| **FR-005.3** | **SRS-2.2** | User Suspension & Restoration | `app/admin/routes.py:toggle_suspend_user` | `TC-ADM-01` | **PASS** |
| **FR-005.4** | **SRS-1.1** | Immutable Administrative Audit Trail | `app/admin/routes.py`, `app/models/audit.py` | `TC-ADM-01`, `TC-ADM-02` | **PASS** |
| **FR-006.1** | **SRS-3.2** | Post Status Transitions (Close/Reopen) | `app/posts/routes.py:update_status` | `TC-POST-05` | **PASS** |
| **FR-007.1** | **SRS-4.3** | Verified Community Impact Calculations | `app/services/stats_service.py:get_community_impact_stats` | `TC-STAT-01`, `TC-STAT-02` | **PASS** |
| **FR-007.2** | **SRS-4.3** | Strict Distinction: Closed vs Completed | `app/services/stats_service.py:get_community_impact_stats` | `TC-STAT-01` | **PASS** |
| **NFR-001**  | **SRS-5.1** | Enterprise Security Response Headers | `app/services/security_service.py:add_security_headers` | `TC-SEC-01` | **PASS** |
| **NFR-002**  | **SRS-5.2** | CSRF Protection on Mutating Forms | `app/services/security_service.py:require_csrf` | `TC-POST-01`, `TC-EXCH-01` | **PASS** |
| **NFR-003**  | **SRS-5.4** | XSS Auto-Escaping in Templates | Jinja2 Template Engine Context | `TC-SEC-04` | **PASS** |
| **NFR-004**  | **SRS-4.3** | Operational Health Check Probe | `app/main/routes.py:health_check` | `TC-STAT-03` | **PASS** |

---

## 2. Requirements Compliance Summary
- **Total Functional Requirements Specified:** 24
- **Total Non-Functional Requirements Specified:** 4
- **Implemented & Verified:** 28 / 28 (100%)
- **Unimplemented / Partially Implemented:** 0
- **Regression Defects:** 0
