# LocalShare – Community Help Board Web App

Community help platform using **SQLite** for storage.
No MySQL or any external DB server needed — SQLite is built into Python.

---

## Project Structure
```
localshare/
├── app.py                ← Flask app (routes + SQLite logic)
├── requirements.txt      ← Only Flask needed
├── localshare.db         ← Auto-created SQLite database file
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── register.html
    ├── login.html
    ├── new_post.html
    ├── posts.html
    └── success.html
```

---

## Run in 3 Steps

### Step 1 – Install Flask
```bash
pip install -r requirements.txt
```

### Step 2 – Run
```bash
python app.py
```

### Step 3 – Open Browser
```
http://127.0.0.1:5000
```

The `localshare.db` SQLite file is **created automatically** on first run with tables and sample data. No setup SQL needed.

---

## Demo Login Credentials
| Email                | Password  |
|----------------------|-----------|
| priya@example.com    | Test@123  |
| rahul@example.com    | Test@123  |

---

## Features
- Register / Login / Logout (Flask session)
- Create posts: Request or Offer (Food, Clothes, Books, Services, Other)
- Browse and filter posts by type, category, location
- Mark your own posts as closed
- Community stats (members, active posts, offers)
- jQuery form validation (empty fields, email, password strength)
- Password strength indicator
- Auto-dismiss flash messages
- Data stored persistently in `localshare.db`

## Why SQLite?
- Built into Python — no installation needed
- Single file database (`localshare.db`)
- Perfect for small/medium projects and development
- Zero configuration
