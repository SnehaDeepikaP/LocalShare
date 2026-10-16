import os
import hmac
import hashlib
import time
from functools import wraps
from flask import session, request, abort, redirect, url_for, flash, current_app

# ─── CSRF Protection ─────────────────────────────────────────────────────────

def generate_csrf_token():
    """Generate or retrieve a cryptographically secure CSRF token for the session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(32).hex()
    return session['_csrf_token']


def validate_csrf_token(token):
    """Validate submitted token against session token."""
    expected = session.get('_csrf_token')
    if not expected or not token:
        return False
    return hmac.compare_digest(str(expected), str(token))


def require_csrf(f):
    """Decorator to require CSRF token on POST/PUT/DELETE routes if enabled."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('TESTING') and not current_app.config.get('WTF_CSRF_ENABLED', True):
            return f(*args, **kwargs)

        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            if not token or not validate_csrf_token(token):
                flash('Security check failed (CSRF token missing or expired). Please try again.', 'danger')
                # Redirect back to referrer if available, else home
                return redirect(request.referrer or url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Rate Limiting (In-Memory Sliding Window) ────────────────────────────────

# Store: { ip_or_key: [(timestamp)] }
_rate_limit_records = {}

def is_rate_limited(key, max_attempts=5, window_seconds=300):
    """
    Check if key (e.g. IP address or email) has exceeded max_attempts within window_seconds.
    Returns (True, remaining_wait_seconds) if limited, otherwise (False, remaining_attempts).
    """
    now = time.time()
    attempts = _rate_limit_records.get(key, [])
    # Filter attempts strictly within the sliding window
    attempts = [t for t in attempts if now - t < window_seconds]
    _rate_limit_records[key] = attempts

    if len(attempts) >= max_attempts:
        oldest = attempts[0]
        wait = int(window_seconds - (now - oldest))
        return True, max(1, wait)

    return False, max_attempts - len(attempts)


def record_failed_attempt(key):
    """Record a failed attempt for rate limiting."""
    now = time.time()
    if key not in _rate_limit_records:
        _rate_limit_records[key] = []
    _rate_limit_records[key].append(now)


def clear_rate_limit(key):
    """Clear attempts on successful authentication."""
    _rate_limit_records.pop(key, None)


# ─── Auth & Role Decorators ──────────────────────────────────────────────────

def login_required(f):
    """Enforce login requirement for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Enforce administrator role for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in with administrator credentials.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


# ─── Security Headers ────────────────────────────────────────────────────────

def add_security_headers(response):
    """Attach enterprise security headers to every HTTP response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content-Security-Policy permitting Bootstrap CDN, Bootstrap Icons, jQuery
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://code.jquery.com 'unsafe-inline'; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    response.headers['Content-Security-Policy'] = csp
    return response
