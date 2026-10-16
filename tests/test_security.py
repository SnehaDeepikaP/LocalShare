from app.services.security_service import is_rate_limited, record_failed_attempt, clear_rate_limit
from app.models.user import User
from app.extensions import db

def test_security_headers_present(client):
    """Verify enterprise security response headers."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.headers.get('X-Content-Type-Options') == 'nosniff'
    assert resp.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert 'Content-Security-Policy' in resp.headers
    assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'


def test_login_rate_limiting_triggers():
    """Verify rate limiter blocks after repeated failed attempts."""
    test_key = '192.168.1.100:testrate@example.com'
    clear_rate_limit(test_key)

    # 4 attempts should not be limited (max 5)
    for _ in range(4):
        record_failed_attempt(test_key)
        limited, _ = is_rate_limited(test_key, max_attempts=5, window_seconds=60)
        assert limited is False

    # 5th attempt triggers rate limiting
    record_failed_attempt(test_key)
    limited, wait = is_rate_limited(test_key, max_attempts=5, window_seconds=60)
    assert limited is True
    assert wait > 0

    clear_rate_limit(test_key)


def test_legacy_plaintext_password_auto_upgrade(app):
    """Verify legacy plaintext password is automatically upgraded upon successful verification."""
    with app.app_context():
        legacy_user = User(
            name='Legacy User',
            email='legacy@example.com',
            password='PlaintextPassword@123',  # Stored as raw plaintext
            location='Hyderabad',
            role='user'
        )
        db.session.add(legacy_user)
        db.session.commit()

        # Initial check
        assert legacy_user.password == 'PlaintextPassword@123'

        # Check password verifies
        verified = legacy_user.check_password('PlaintextPassword@123')
        assert verified is True

        # Crucial security assertion: password should now be hashed!
        assert legacy_user.password != 'PlaintextPassword@123'
        assert legacy_user.password.startswith(('scrypt:', 'pbkdf2:'))


def test_html_input_escaping_in_templates(client, app, test_users):
    """Verify Jinja template auto-escapes HTML/script tags in post titles."""
    with app.app_context():
        from app.models.post import Post
        xss_post = Post(
            user_id=test_users['alice'].id,
            user_name='<script>alert(1)</script>',
            post_type='offer',
            category='Food',
            title='<script>alert("XSS")</script>',
            description='<b>Safe bold description</b>',
            location='Hyderabad',
            status='open'
        )
        db.session.add(xss_post)
        db.session.commit()
        p_id = xss_post.id

    resp = client.get(f'/post/{p_id}')
    assert resp.status_code == 200
    # Must be escaped, not rendered as raw unescaped script tag
    assert b'<script>alert("XSS")</script>' not in resp.data
    assert b'&lt;script&gt;alert(&#34;XSS&#34;)&lt;/script&gt;' in resp.data or b'&lt;script&gt;' in resp.data
