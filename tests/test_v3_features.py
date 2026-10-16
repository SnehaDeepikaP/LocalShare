import pytest
from unittest.mock import patch
from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.exchange import ExchangeRequest
from app.models.message import ExchangeMessage
from app.models.review import ExchangeReview
from app.models.notification import Notification
from app.models.saved_listing import SavedListing

def test_google_unconfigured_behavior(client):
    """When GOOGLE_CLIENT_ID is not configured, /google redirects safely with a clear flash notice."""
    resp = client.get('/google', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Google Sign-In is not currently configured' in resp.data

def test_google_oauth_callback_unconfigured(client):
    """Callback route safely handles unconfigured state."""
    resp = client.get('/google/callback?code=mock_code&state=mock_state', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Google authentication is not configured.' in resp.data

def test_google_oauth_prevents_silent_account_hijack(client, test_users):
    """
    CRITICAL SECURITY TEST:
    If a user already exists with email 'alice@example.com' (password auth),
    Google login with the same email must NEVER silently attach the identity.
    It must block and advise the user to log in with password first.
    """
    mock_userinfo = {
        'sub': 'google-uid-alice-12345',
        'email': 'alice@example.com',
        'email_verified': True,
        'name': 'Alice Google',
        'picture': 'https://example.com/avatar.jpg'
    }

    with patch('app.auth.routes.is_google_auth_configured', return_value=True):
        with patch('app.auth.routes.exchange_google_code_for_userinfo', return_value=(mock_userinfo, None)):
            resp = client.get('/google/callback?code=valid_code&state=valid_state', follow_redirects=True)
            assert resp.status_code == 200
            # Must contain warning preventing silent hijack
            assert b'already exists with password sign-in' in resp.data

            # Verify in DB that Alice's google_id was NOT silently updated
            with client.application.app_context():
                alice = User.query.filter_by(email='alice@example.com').first()
                assert alice.google_id is None

def test_google_oauth_new_user_registration(client):
    """Verifies that an unknown Google identity creates a new account with random password and verified sub."""
    mock_userinfo = {
        'sub': 'google-uid-newuser-99999',
        'email': 'newneighbor@example.com',
        'email_verified': True,
        'name': 'Neighbor Dave',
        'picture': 'https://example.com/dave.jpg'
    }

    with patch('app.auth.routes.is_google_auth_configured', return_value=True):
        with patch('app.auth.routes.exchange_google_code_for_userinfo', return_value=(mock_userinfo, None)):
            resp = client.get('/google/callback?code=code123&state=state123', follow_redirects=True)
            assert resp.status_code == 200
            assert b'Your account has been created with Google' in resp.data

            with client.application.app_context():
                dave = User.query.filter_by(google_id='google-uid-newuser-99999').first()
                assert dave is not None
                assert dave.email == 'newneighbor@example.com'
                assert dave.name == 'Neighbor Dave'
                assert dave.avatar_url == 'https://example.com/dave.jpg'
                assert dave.is_active is True

def test_saved_listing_watchlist_toggle(auth_client, test_users):
    """Test bookmarking and unbookmarking a listing to watchlist."""
    with auth_client.application.app_context():
        post = Post(
            user_id=test_users['bob'].id,
            user_name=test_users['bob'].name,
            post_type='offer',
            category='Tools',
            title='Cordless Hand Drill with Battery',
            description='Working drill available to borrow for home repairs',
            location='Campus Central',
            status='open'
        )
        db.session.add(post)
        db.session.commit()
        p_id = post.id

    # 1. Save listing
    resp = auth_client.post(f'/post/{p_id}/save', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Listing saved to your watchlist!' in resp.data

    with auth_client.application.app_context():
        saved = SavedListing.query.filter_by(user_id=test_users['alice'].id, post_id=p_id).first()
        assert saved is not None

    # 2. Toggle again to remove
    resp2 = auth_client.post(f'/post/{p_id}/save', follow_redirects=True)
    assert resp2.status_code == 200
    assert b'Listing removed from your saved watchlist' in resp2.data

    with auth_client.application.app_context():
        saved = SavedListing.query.filter_by(user_id=test_users['alice'].id, post_id=p_id).first()
        assert saved is None

def test_in_app_conversation_thread_and_authorization(auth_client, test_users):
    """
    Test safe in-app messaging:
    - Initial exchange request creates opening message
    - Participants can chat back and forth
    - Unauthorized third party receives 403 Forbidden
    """
    with auth_client.application.app_context():
        post = Post(
            user_id=test_users['bob'].id,
            user_name=test_users['bob'].name,
            post_type='offer',
            category='Books',
            title='Physics for Scientists and Engineers',
            description='Standard university physics book in good shape',
            location='Hostel B',
            status='open'
        )
        db.session.add(post)
        db.session.commit()
        p_id = post.id

    # Alice requests post
    resp = auth_client.post(f'/exchange/request/{p_id}', data={
        'message': 'Hi Bob, can we meet at the campus library tomorrow at 4 PM?',
        'contact_info': 'In-app chat preferred'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'A private coordination thread has been opened' in resp.data

    with auth_client.application.app_context():
        req = ExchangeRequest.query.filter_by(post_id=p_id, requester_id=test_users['alice'].id).first()
        assert req is not None
        req_id = req.id

        # Verify initial opening message exists
        assert req.messages.count() == 1
        assert 'can we meet at the campus library' in req.messages.first().content

        # Verify notification was generated for Bob
        notif = Notification.query.filter_by(user_id=test_users['bob'].id).first()
        assert notif is not None
        assert 'Physics for Scientists' in notif.title

    # Alice sends follow-up message in thread
    resp_msg = auth_client.post(f'/exchange/{req_id}/thread', data={
        'content': 'I will be wearing a blue backpack near the front desk.'
    }, follow_redirects=True)
    assert resp_msg.status_code == 200
    assert b'Message sent' in resp_msg.data

    with auth_client.application.app_context():
        req = ExchangeRequest.query.get(req_id)
        assert req.messages.count() == 2

    # Unauthorized third-party user test: simulate a different user accessing Alice and Bob's thread
    with auth_client.session_transaction() as sess:
        sess['user_id'] = 999999  # Stranger ID
        sess['user_name'] = 'Stranger'
        sess['role'] = 'user'

    resp_unauth = auth_client.get(f'/exchange/{req_id}/thread')
    assert resp_unauth.status_code == 403

def test_handover_completion_review_and_reputation(auth_client, test_users):
    """
    Test:
    1. Exchange accepted and marked completed
    2. Review and sustainability checkbox submitted
    3. User reputation score updates correctly
    """
    with auth_client.application.app_context():
        post = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Household',
            title='Study Desk Lamp',
            description='Adjustable LED study lamp with USB power port',
            location='Block C',
            status='open'
        )
        db.session.add(post)
        db.session.commit()
        p_id = post.id

        req = ExchangeRequest(
            post_id=p_id,
            requester_id=test_users['bob'].id,
            message='I would love to use this lamp for late night studying!',
            status='accepted'
        )
        db.session.add(req)
        db.session.commit()
        req_id = req.id

    # Alice marks exchange completed
    resp_comp = auth_client.post(f'/exchange/{req_id}/complete', follow_redirects=True)
    assert resp_comp.status_code == 200
    assert b'The community exchange has been completed' in resp_comp.data

    # Alice submits review for Bob
    resp_rev = auth_client.post(f'/exchange/{req_id}/review', data={
        'rating': '5',
        'comment': 'Punctual, friendly, and very respectful neighbor!',
        'was_reused_or_repaired': '1'
    }, follow_redirects=True)
    assert resp_rev.status_code == 200
    assert b'Your review has been recorded' in resp_rev.data

    with auth_client.application.app_context():
        rev = ExchangeReview.query.filter_by(exchange_id=req_id, reviewer_id=test_users['alice'].id).first()
        assert rev is not None
        assert rev.rating == 5
        assert rev.was_reused_or_repaired is True
        assert rev.reviewee_id == test_users['bob'].id

        # Verify Bob's reputation score updated
        bob = User.query.get(test_users['bob'].id)
        rep = bob.reputation
        assert rep['average'] == 5.0
        assert rep['count'] == 1

def test_public_profile_privacy(client, test_users):
    """
    Verify public profile:
    - Shows member name, location, and reputation
    - NEVER reveals password hash or raw private details
    """
    resp = client.get(f'/users/{test_users["alice"].id}')
    assert resp.status_code == 200
    assert b'Alice Wonderland' in resp.data
    assert b'Community Profile' in resp.data
    assert b'scrypt:' not in resp.data
    assert b'pbkdf2:' not in resp.data
