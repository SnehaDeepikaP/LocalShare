# User & Administrator Manual — LocalShare

**Document Identifier:** UGM-LS-2026-V2.0  
**Target Audience:** Community Members & Platform Administrators  
**Platform Version:** LocalShare Production v2.0.0  

---

## PART 1: COMMUNITY MEMBER MANUAL

### 1. Getting Started

#### 1.1 Account Registration
1. Navigate to the top navigation bar and click **Register**.
2. Fill in:
   - **Full Name:** Your real name or community display name (2–100 characters).
   - **Email Address:** Your active email address (used for logging in).
   - **Password:** Minimum 6 characters, must include at least 1 uppercase letter and 1 digit. Observe the dynamic password strength bar.
   - **Location:** Your general neighbourhood, municipality, or landmark (e.g. *Hyderabad, Banjara Hills*). Do *not* enter your private flat or door number.
3. Click **Create Free Account**. Upon success, you will be redirected to the login screen.

#### 1.2 Logging In
1. Click **Log In** in the navigation bar.
2. Enter your registered email address and password.
3. *(Demo Testing Accounts)*:
   - `priya@example.com` / `Test@123` (Resource Giver)
   - `rahul@example.com` / `Test@123` (Resource Seeker)

---

### 2. Discovering & Filtering Resources

1. Click **Browse** in the top navigation bar (`/posts`).
2. Utilize the search and filter strip:
   - **Keyword:** Enter words like *physics*, *clothes*, *maths*, or *meal*.
   - **Type:** Filter by *Request* (people needing help) or *Offer* (people sharing resources).
   - **Category:** Choose *Food*, *Clothes*, *Books*, *Services*, or *Other*.
   - **Location:** Filter by city or area name.
   - **Sort By:** Sort by *Newest First*, *Oldest First*, or *Title (A-Z)*.
3. Click the filter button to apply. Click the &times; button to reset.
4. Use the pagination controls at the bottom (`<< Prev`, `1`, `2`, `Next >>`) to navigate large result sets.

---

### 3. Creating & Managing Posts

#### 3.1 Creating a Post
1. Click **Create Post** in the navbar.
2. Select **Post Type**:
   - **Offer Help:** You have items or volunteer time you wish to gift.
   - **Request Help:** You are looking for resources or mutual aid.
3. Choose the appropriate **Category**.
4. Enter a descriptive **Title** (4–200 characters) and detailed **Description** (minimum 10 characters).
5. Specify your general **Location**.
6. Click **Publish Post**. You will be redirected to the confirmation screen with a direct link to your live post.

#### 3.2 Managing Your Posts
1. Visit **My Dashboard** from the user dropdown in the navbar.
2. Under the **My Posts** tab, you can view all active, in-progress, completed, and closed posts.
3. Click the **View** icon to see public details, the **Edit** icon to update title/description/category, or the **Close / Reopen** button to toggle availability.

---

### 4. User-to-User Mutual Aid Handover Workflow

#### 4.1 Expressing Interest in a Post
1. On any post authored by another member, review the description and location.
2. Scroll to the **Connect & Exchange** card on the right side.
3. Enter a friendly **Note** explaining your interest and how you can pick up the item.
4. *(Optional)* Provide safe **Contact / Coordination Info** (e.g. WhatsApp, phone number, or preferred meeting times). This will *only* be revealed if the author accepts your request.
5. Click **Send Interest Request**.

#### 4.2 Reviewing Incoming Requests (Post Authors)
1. When another neighbour requests your post, a red badge appears on your **Incoming Requests** tab in **My Dashboard**.
2. Click **Incoming Requests** to review the requester's name, general location, and message.
3. Click **Accept** to approve the request and optionally provide meeting instructions (e.g. *"Meet me at the community library lobby on Saturday at 3 PM"*).
4. Click **Decline** if the item is no longer available.

#### 4.3 Finalizing & Completing an Exchange
1. After meeting in person and completing the physical handover, either user can click **Mark Completed** in their dashboard or on the post detail page.
2. The post and request transition to **Completed**, incrementing verified community impact statistics!

---

### 5. Smart Recommendations & Matching

1. Click **Matches** in the top navigation bar (`/matches`).
2. The platform automatically analyzes your active posts against complementary listings in your area.
3. Each match displays a compatibility score (e.g. `90% Match`) along with a full explainable factor breakdown showing points awarded for Type Compatibility, Category Relevance, Keyword Overlap, and Location Proximity.

---

## PART 2: ADMINISTRATOR OPERATIONS MANUAL

### 1. Administrative Portal Access
1. Log in with an administrator account (e.g. `admin@localshare.dev` / `Admin@123`).
2. An **Admin** badge appears next to your name in the navbar. Click the user dropdown and select **Admin Dashboard** (`/admin`).

### 2. Moderating Posts
1. Click **Moderate Posts** (`/admin/posts`).
2. Search posts by keyword or filter by status.
3. Administrators can:
   - **Close Post:** Prevents new interest requests.
   - **Reopen Post:** Restores a closed listing back to open status.
   - **Remove Post (Delete):** Permanently purges inappropriate, commercial, or prohibited listings.
   - Every action is automatically logged in the immutable audit trail.

### 3. User Governance & Suspensions
1. Click **Manage Users** (`/admin/users`).
2. Search by member name or email.
3. To suspend a disruptive or violating user, click **Suspend**. The user is immediately blocked from logging in.
4. To restore an account, click **Restore**.
5. To grant or revoke administrative privileges, click **Make Admin** or **Demote**.

### 4. Reviewing Community Reports
1. Click **Review Reports** (`/admin/reports`).
2. Filter by *Open Reports*, *Action Taken*, or *Dismissed*.
3. Click **Resolve (Action Taken)** after moderating offending content, or **Dismiss** if the report is unfounded.

### 5. Inspecting Audit Logs
1. Click **Audit Logs** (`/admin/audit-logs`).
2. Review chronological records of every moderation action, including administrator name, action name, target record ID, details, and UTC timestamps.
