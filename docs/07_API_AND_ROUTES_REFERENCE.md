# API & Routes Reference Manual — LocalShare

**Document Identifier:** ARR-LS-2026-V2.0  
**Total Routes Documented:** 24  
**Architecture:** Server-Rendered Jinja2 Web Application with JSON Health Endpoints  

---

## 1. Route Inventory Overview

| Method | Endpoint URL | Blueprint | Auth Level | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `main` | Public | Homepage with live stats & recent posts |
| `GET` | `/dashboard` | `main` | User | User dashboard with posts, requests, matches |
| `GET` | `/impact` | `main` | Public | Public verified impact dashboard |
| `GET` | `/guidelines` | `main` | Public | Community safety & sharing guidelines |
| `GET, POST` | `/report/post/<id>` | `main` | User | File community report against a post |
| `GET, POST` | `/report/user/<id>` | `main` | User | File community report against a user |
| `GET` | `/health` | `main` | Public | System and database health status (JSON) |
| `GET, POST` | `/register` | `auth` | Anonymous | User account registration |
| `GET, POST` | `/login` | `auth` | Anonymous | User authentication |
| `GET, POST` | `/logout` | `auth` | User | Clears session and logs user out |
| `GET, POST` | `/profile` | `auth` | User | Profile updating & password change |
| `GET` | `/posts` | `posts` | Public | Browse, search, filter, and paginate posts |
| `GET, POST` | `/post/new` | `posts` | User | Create a new community post |
| `GET` | `/post/<id>` | `posts` | Public | View full post details & matching list |
| `GET` | `/success/<id>` | `posts` | Public | Post published confirmation screen |
| `GET, POST` | `/post/<id>/edit` | `posts` | Author / Admin | Edit post information |
| `POST` | `/post/<id>/status`| `posts` | Author / Admin | Change post lifecycle status |
| `GET, POST` | `/post/close/<id>` | `posts` | Author / Admin | Close post (backwards-compatibility) |
| `POST` | `/post/<id>/delete`| `posts` | Author / Admin | Delete post permanently |
| `POST` | `/exchange/request/<id>` | `exchange` | User (Not Owner)| Submit interest request |
| `POST` | `/exchange/<id>/respond` | `exchange` | Post Author | Accept or decline interest request |
| `POST` | `/exchange/<id>/complete`| `exchange` | Participant / Admin | Mark exchange completed |
| `POST` | `/exchange/<id>/cancel` | `exchange` | Requester / Admin | Cancel pending request |
| `GET` | `/matches` | `matching` | User | Smart matches dashboard for user |
| `GET` | `/post/<id>/matches` | `matching` | Public | Detailed match factor breakdown for post |
| `GET` | `/admin/` / `/admin` | `admin` | Administrator | Admin portal overview & quick metrics |
| `GET` | `/admin/users` | `admin` | Administrator | User account management list & filters |
| `POST` | `/admin/user/<id>/toggle-suspend` | `admin` | Administrator | Suspend or restore user account |
| `POST` | `/admin/user/<id>/toggle-role` | `admin` | Administrator | Promote or demote user admin privileges |
| `GET` | `/admin/posts` | `admin` | Administrator | Post moderation list & filters |
| `POST` | `/admin/post/<id>/moderate` | `admin` | Administrator | Moderate post (close, reopen, delete) |
| `GET` | `/admin/reports` | `admin` | Administrator | Moderation queue for community reports |
| `POST` | `/admin/report/<id>/action` | `admin` | Administrator | Resolve report (action taken / dismissed) |
| `GET` | `/admin/audit-logs` | `admin` | Administrator | View immutable administrative audit history |

---

## 2. Route Specifications

### 2.1 Authentication & Accounts (`auth`)

#### `POST /register`
- **Purpose:** Registers a new user account.
- **CSRF Required:** Yes (`csrf_token` in form body).
- **Inputs:** `name` (2–100 chars), `email` (valid format, <=120 chars), `password` (min 6 chars, 1 uppercase, 1 number), `location` (2–120 chars).
- **Validation:** Server-side regex and length bounds; email uniqueness verified via `User.query.filter_by(email=email).first()`.
- **Response:** `302 Redirect` to `/login` on success with flash `'Registration successful! Please log in.'`.

#### `POST /login`
- **Purpose:** Authenticates user credentials.
- **Rate Limiting:** Max 5 attempts per 300s window per client IP/email.
- **Response:** On success, establishes permanent session and redirects to `next` URL or `/`. If account is suspended (`is_suspended=True`), rejects with 403-equivalent alert.

### 2.2 Posts & Discovery (`posts`)

#### `GET /posts`
- **Purpose:** Public exploration of community resources.
- **Query Parameters:**
  - `q`: Free-text search matching `title` or `description` (case-insensitive `LIKE`).
  - `type`: `request` or `offer`.
  - `category`: `Food`, `Clothes`, `Books`, `Services`, `Other`.
  - `location`: Substring match on `location`.
  - `status`: `open` (default), `in_progress`, `completed`, `closed`, `all`.
  - `sort`: `newest` (default), `oldest`, `title`.
  - `page`: Integer page number (default 1; 6 posts per page).
- **Response:** `200 OK` rendering `posts.html` with pagination controls.

#### `POST /post/new`
- **Auth:** `@login_required`.
- **CSRF Required:** Yes.
- **Inputs:** `post_type`, `category`, `title`, `description`, `location`.
- **Response:** `302 Redirect` to `/success/<post_id>`.

### 2.3 User-to-User Exchange (`exchange`)

#### `POST /exchange/request/<int:post_id>`
- **Auth:** `@login_required`.
- **Rules:** Cannot request own post; cannot request non-open post; cannot submit if duplicate pending request exists.
- **Inputs:** `message` (min 5 chars), `contact_info` (optional, max 255 chars).
- **Response:** `302 Redirect` to `/post/<post_id>` with confirmation flash.

#### `POST /exchange/<int:request_id>/complete`
- **Auth:** Post author, requester, or administrator.
- **Effect:** Sets `exchange_requests.status = 'completed'` and `posts.status = 'completed'`.
- **Response:** `302 Redirect` to `/dashboard`.

### 2.4 Health Check API

#### `GET /health`
- **Purpose:** Container orchestration and load balancer liveness/readiness probe.
- **Auth:** Public.
- **Response Example (200 OK):**
```json
{
  "database": "connected",
  "service": "LocalShare Community Platform",
  "status": "healthy"
}
```
