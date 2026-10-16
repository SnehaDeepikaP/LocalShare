import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.post import Post

@pytest.fixture
def app():
    """Create and configure a clean testing app instance."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_users(app):
    """Create test users in database."""
    with app.app_context():
        user1 = User(
            name='Alice Wonderland',
            email='alice@example.com',
            location='Hyderabad',
            role='user',
            is_active=True,
            is_suspended=False
        )
        user1.set_password('Alice@123')

        user2 = User(
            name='Bob Builder',
            email='bob@example.com',
            location='Hyderabad',
            role='user',
            is_active=True,
            is_suspended=False
        )
        user2.set_password('Bob@1234')

        admin = User(
            name='Admin User',
            email='admin@example.com',
            location='Hyderabad',
            role='admin',
            is_active=True,
            is_suspended=False
        )
        admin.set_password('Admin@123')

        db.session.add_all([user1, user2, admin])
        db.session.commit()

        # Re-query to return fresh instances
        u1 = User.query.filter_by(email='alice@example.com').first()
        u2 = User.query.filter_by(email='bob@example.com').first()
        adm = User.query.filter_by(email='admin@example.com').first()

        return {'alice': u1, 'bob': u2, 'admin': adm}


@pytest.fixture
def auth_client(client, test_users):
    """Client with Alice logged in."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_users['alice'].id
        sess['user_name'] = test_users['alice'].name
        sess['user_email'] = test_users['alice'].email
        sess['role'] = test_users['alice'].role
        sess['location'] = test_users['alice'].location
    return client


@pytest.fixture
def admin_client(client, test_users):
    """Client with Admin logged in."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_users['admin'].id
        sess['user_name'] = test_users['admin'].name
        sess['user_email'] = test_users['admin'].email
        sess['role'] = 'admin'
        sess['location'] = test_users['admin'].location
    return client
