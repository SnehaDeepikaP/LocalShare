from app.models.user import User

def test_registration_success(client, app):
    """Verify new user registration with properly hashed password."""
    response = client.post('/register', data={
        'name': 'Charlie Chaplin',
        'email': 'charlie@example.com',
        'password': 'Charlie@123',
        'location': 'Hyderabad'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful' in response.data

    with app.app_context():
        user = User.query.filter_by(email='charlie@example.com').first()
        assert user is not None
        assert user.name == 'Charlie Chaplin'
        # Crucial security assertion: password must NOT be plaintext
        assert user.password != 'Charlie@123'
        assert user.password.startswith(('scrypt:', 'pbkdf2:'))
        assert user.check_password('Charlie@123') is True
        assert user.check_password('WrongPass') is False


def test_registration_duplicate_email(client, test_users):
    """Verify duplicate email registration is rejected."""
    response = client.post('/register', data={
        'name': 'Alice Copycat',
        'email': 'alice@example.com',
        'password': 'Alice@123',
        'location': 'Hyderabad'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'already registered' in response.data


def test_registration_validation_rules(client):
    """Verify password strength and field length enforcement."""
    # Too short password
    resp = client.post('/register', data={
        'name': 'Shorty',
        'email': 'short@example.com',
        'password': '123',
        'location': 'Hyderabad'
    }, follow_redirects=True)
    assert b'at least 6 characters' in resp.data

    # Missing uppercase/number
    resp2 = client.post('/register', data={
        'name': 'NoNum',
        'email': 'nonum@example.com',
        'password': 'password',
        'location': 'Hyderabad'
    }, follow_redirects=True)
    assert b'uppercase' in resp2.data


def test_login_success_and_session(client, test_users):
    """Verify valid login establishes session."""
    response = client.post('/login', data={
        'email': 'alice@example.com',
        'password': 'Alice@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back, Alice Wonderland' in response.data

    with client.session_transaction() as sess:
        assert sess.get('user_id') == test_users['alice'].id
        assert sess.get('user_name') == 'Alice Wonderland'
        assert sess.get('role') == 'user'


def test_login_invalid_password(client, test_users):
    """Verify login failure with incorrect credentials."""
    response = client.post('/login', data={
        'email': 'alice@example.com',
        'password': 'WrongPassword@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_login_suspended_user_blocked(client, app, test_users):
    """Verify suspended accounts cannot log in."""
    with app.app_context():
        u = User.query.filter_by(email='bob@example.com').first()
        u.is_suspended = True
        from app.extensions import db
        db.session.commit()

    response = client.post('/login', data={
        'email': 'bob@example.com',
        'password': 'Bob@1234'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'account has been suspended' in response.data


def test_logout(client, auth_client):
    """Verify logout clears session."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out successfully' in response.data

    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_protected_route_redirects_unauthenticated(client):
    """Verify unauthenticated access to protected routes redirects to login."""
    resp = client.get('/post/new', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']

    resp_dash = client.get('/dashboard', follow_redirects=False)
    assert resp_dash.status_code == 302
    assert '/login' in resp_dash.headers['Location']
