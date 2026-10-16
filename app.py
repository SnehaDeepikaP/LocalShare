from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'localshare_sqlite_secret_2024'

# ─── Database Path ────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'localshare.db')

# ─── DB Helpers ───────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # allows dict-like access: row['column']
    return conn

def init_db():
    """Create tables and seed sample data if DB is new."""
    conn = get_db()
    cur  = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            location   TEXT    NOT NULL,
            created_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            user_name   TEXT    NOT NULL,
            post_type   TEXT    NOT NULL CHECK(post_type IN ('request','offer')),
            category    TEXT    NOT NULL,
            title       TEXT    NOT NULL,
            description TEXT    NOT NULL,
            location    TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'open',
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Seed sample data only once
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO users (name, email, password, location) VALUES (?,?,?,?)",
            [
                ('Priya Sharma', 'priya@example.com', 'Test@123', 'Hyderabad'),
                ('Rahul Verma',  'rahul@example.com', 'Test@123', 'Hyderabad'),
            ]
        )
        cur.executemany(
            '''INSERT INTO posts (user_id, user_name, post_type, category, title, description, location)
               VALUES (?,?,?,?,?,?,?)''',
            [
                (1, 'Priya Sharma', 'offer',   'Food',
                 'Home cooked meals on weekends',
                 'I cook extra food every weekend and happy to share. Vegetarian only.',
                 'Hyderabad'),
                (2, 'Rahul Verma',  'request', 'Books',
                 'Need CBSE Class 10 textbooks',
                 'Looking for Science and Maths books for my younger sibling. Any edition works.',
                 'Hyderabad'),
                (1, 'Priya Sharma', 'offer',   'Clothes',
                 "Kids clothes (2–5 years), free to take",
                 'My child has outgrown these. Good condition, free for anyone who needs them.',
                 'Hyderabad'),
            ]
        )

    conn.commit()
    conn.close()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    conn = get_db()
    recent_posts = conn.execute(
        "SELECT * FROM posts WHERE status='open' ORDER BY created_at DESC LIMIT 6"
    ).fetchall()
    user_count  = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    post_count  = conn.execute("SELECT COUNT(*) FROM posts WHERE status='open'").fetchone()[0]
    offer_count = conn.execute("SELECT COUNT(*) FROM posts WHERE post_type='offer'").fetchone()[0]
    conn.close()
    return render_template('index.html',
                           recent_posts=recent_posts,
                           user_count=user_count,
                           post_count=post_count,
                           offer_count=offer_count)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        location = request.form['location'].strip()
        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name, email, password, location) VALUES (?,?,?,?)",
                (name, email, password, location)
            )
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please login.', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?", (email, password)
        ).fetchone()
        conn.close()
        if user:
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['location']  = user['location']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        flash('Please login to create a post.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute(
            '''INSERT INTO posts (user_id, user_name, post_type, category, title, description, location)
               VALUES (?,?,?,?,?,?,?)''',
            (session['user_id'], session['user_name'],
             request.form['post_type'], request.form['category'],
             request.form['title'].strip(), request.form['description'].strip(),
             request.form['location'].strip())
        )
        conn.commit()
        post_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        flash('Your post was published!', 'success')
        return redirect(url_for('success', post_id=post_id))
    return render_template('new_post.html')


@app.route('/success/<int:post_id>')
def success(post_id):
    conn = get_db()
    post = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    conn.close()
    return render_template('success.html', post=post)


@app.route('/posts')
def posts():
    post_type = request.args.get('type', '')
    category  = request.args.get('category', '')
    location  = request.args.get('location', '').strip()

    query  = "SELECT * FROM posts WHERE status='open'"
    params = []
    if post_type:
        query += " AND post_type=?";  params.append(post_type)
    if category:
        query += " AND category=?";   params.append(category)
    if location:
        query += " AND location LIKE ?"; params.append(f'%{location}%')
    query += " ORDER BY created_at DESC"

    conn       = get_db()
    all_posts  = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('posts.html',
                           posts=all_posts,
                           selected_type=post_type,
                           selected_category=category,
                           location_filter=location)


@app.route('/post/close/<int:post_id>')
def close_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute(
        "UPDATE posts SET status='closed' WHERE id=? AND user_id=?",
        (post_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    flash('Post marked as closed.', 'info')
    return redirect(url_for('posts'))


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
