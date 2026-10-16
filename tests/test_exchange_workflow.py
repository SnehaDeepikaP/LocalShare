from app.extensions import db
from app.models.post import Post
from app.models.exchange import ExchangeRequest
from app.services.stats_service import get_community_impact_stats

def test_full_exchange_workflow(client, test_users):
    """
    End-to-end integration test of user-to-user exchange:
    Alice creates offer -> Bob requests interest -> Alice accepts -> Either marks completed.
    """
    # 1. Alice creates offer
    with client.application.app_context():
        alice_post = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Books',
            title='Physics Class 11 Reference Guide',
            description='Comprehensive reference book in great condition',
            location='Hyderabad',
            status='open'
        )
        db.session.add(alice_post)
        db.session.commit()
        post_id = alice_post.id

    # 2. Bob logs in and submits interest request
    with client.session_transaction() as sess:
        sess['user_id'] = test_users['bob'].id
        sess['user_name'] = test_users['bob'].name
        sess['role'] = 'user'

    resp_req = client.post(f'/exchange/request/{post_id}', data={
        'message': 'Hello Alice, I would love to pick this book up for my studies.',
        'contact_info': 'bob@mobile.dev / +91-9876543210'
    }, follow_redirects=True)

    assert resp_req.status_code == 200
    assert b'Interest request submitted' in resp_req.data

    with client.application.app_context():
        req = ExchangeRequest.query.filter_by(post_id=post_id, requester_id=test_users['bob'].id).first()
        assert req is not None
        assert req.status == 'pending'
        req_id = req.id

    # 3. Alice logs in and accepts the request
    with client.session_transaction() as sess:
        sess['user_id'] = test_users['alice'].id
        sess['user_name'] = test_users['alice'].name
        sess['role'] = 'user'

    resp_accept = client.post(f'/exchange/{req_id}/respond', data={
        'action': 'accept',
        'response_note': 'Accepted! Meet me at the library entrance at 4pm on Saturday.'
    }, follow_redirects=True)

    assert resp_accept.status_code == 200
    assert b'Request accepted' in resp_accept.data

    with client.application.app_context():
        updated_req = ExchangeRequest.query.get(req_id)
        assert updated_req.status == 'accepted'
        assert 'library entrance' in updated_req.response_note

    # 4. Mark exchange as completed
    resp_complete = client.post(f'/exchange/{req_id}/complete', follow_redirects=True)
    assert resp_complete.status_code == 200
    assert b'successfully completed' in resp_complete.data

    with client.application.app_context():
        completed_req = ExchangeRequest.query.get(req_id)
        completed_post = Post.query.get(post_id)
        assert completed_req.status == 'completed'
        assert completed_post.status == 'completed'

        # Verify impact statistics reflect the completed exchange
        stats = get_community_impact_stats()
        assert stats['completed_exchanges_count'] >= 1


def test_cannot_request_own_post(auth_client, test_users):
    """Verify user cannot express interest in their own post."""
    with auth_client.application.app_context():
        p = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Food',
            title='Alice Own Food Post',
            description='Delicious extra meal',
            location='Hyderabad',
            status='open'
        )
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    resp = auth_client.post(f'/exchange/request/{p_id}', data={
        'message': 'Expressing interest in my own post'
    }, follow_redirects=True)

    assert b'cannot express interest in your own post' in resp.data


def test_duplicate_pending_request_prevented(client, test_users):
    """Verify duplicate active requests are blocked."""
    with client.application.app_context():
        p = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Clothes',
            title='Baby Clothes Collection',
            description='Warm clothes collection',
            location='Hyderabad',
            status='open'
        )
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    # Bob requests first time
    with client.session_transaction() as sess:
        sess['user_id'] = test_users['bob'].id
        sess['user_name'] = test_users['bob'].name

    client.post(f'/exchange/request/{p_id}', data={'message': 'First interest note'})

    # Bob requests second time
    resp2 = client.post(f'/exchange/request/{p_id}', data={'message': 'Duplicate interest note'}, follow_redirects=True)
    assert b'already have an active request' in resp2.data
