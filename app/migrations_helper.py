import sqlite3
import os
from werkzeug.security import generate_password_hash

def upgrade_existing_sqlite_database(db_path):
    """
    Safely inspects and migrates existing localshare.db:
    1. Adds missing columns (role, is_active, is_suspended) if not present.
    2. Hashes any legacy plaintext passwords stored in users.
    3. Ensures exchange_requests, reports, and audit_logs tables exist.
    """
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check columns of users table
    cur.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cur.fetchall()]

    if 'role' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    if 'is_active' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
    if 'is_suspended' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT 0")

    if 'google_id' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN google_id TEXT DEFAULT NULL")
    if 'avatar_url' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT NULL")
    if 'bio' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT NULL")

    # Hash any plaintext passwords
    cur.execute("SELECT id, password FROM users")
    users = cur.fetchall()
    for u_id, pwd in users:
        if pwd and not pwd.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
            hashed = generate_password_hash(pwd)
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, u_id))

    # Check if admin user exists, if not create one
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' OR email = 'admin@localshare.dev'")
    if cur.fetchone()[0] == 0:
        admin_pwd = generate_password_hash('Admin@123')
        cur.execute(
            "INSERT INTO users (name, email, password, location, role, is_active, is_suspended) VALUES (?,?,?,?,?,?,?)",
            ('Platform Administrator', 'admin@localshare.dev', admin_pwd, 'Hyderabad', 'admin', 1, 0)
        )

    # Check columns of posts table
    cur.execute("PRAGMA table_info(posts)")
    post_cols = [row[1] for row in cur.fetchall()]
    if 'updated_at' not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN updated_at TEXT DEFAULT NULL")
    if 'urgency' not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN urgency TEXT DEFAULT 'normal'")
    if 'condition' not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN condition TEXT DEFAULT NULL")
    if 'intent' not in post_cols:
        cur.execute("ALTER TABLE posts ADD COLUMN intent TEXT DEFAULT 'giveaway'")

    # Create new tables if not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exchange_requests (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id       INTEGER NOT NULL,
            requester_id  INTEGER NOT NULL,
            message       TEXT    NOT NULL,
            contact_info  TEXT,
            status        TEXT    NOT NULL DEFAULT 'pending',
            response_note TEXT,
            created_at    TEXT    DEFAULT (datetime('now','localtime')),
            updated_at    TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id      INTEGER,
            post_id          INTEGER,
            reported_user_id INTEGER,
            reason           TEXT NOT NULL,
            details          TEXT NOT NULL,
            status           TEXT NOT NULL DEFAULT 'open',
            action_taken     TEXT,
            created_at       TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id    INTEGER,
            action      TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id   INTEGER NOT NULL,
            details     TEXT,
            created_at  TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS saved_listings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            post_id    INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS exchange_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange_id INTEGER NOT NULL,
            sender_id   INTEGER NOT NULL,
            content     TEXT    NOT NULL,
            is_read     BOOLEAN DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (exchange_id) REFERENCES exchange_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS exchange_reviews (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange_id          INTEGER NOT NULL,
            reviewer_id          INTEGER NOT NULL,
            reviewee_id          INTEGER NOT NULL,
            rating               INTEGER NOT NULL,
            comment              TEXT,
            was_reused_or_repaired BOOLEAN DEFAULT 0,
            created_at           TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(exchange_id, reviewer_id),
            FOREIGN KEY (exchange_id) REFERENCES exchange_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            link       TEXT,
            is_read    BOOLEAN DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
