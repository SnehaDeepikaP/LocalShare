from app.extensions import db
from app.models.post import Post
from app.models.exchange import ExchangeRequest
from app.services.stats_service import get_community_impact_stats

def test_closed_post_does_not_count_as_completed(app, test_users):
    """
    Verify strict requirement: A closed post MUST NOT automatically
    count as a completed exchange.
    """
    with app.app_context():
        # Create an open post and a closed post
        open_post = Post(user_id=test_users['alice'].id, user_name='Alice', post_type='offer', category='Food', title='Open Food', description='desc desc desc', location='Hyderabad', status='open')
        closed_post = Post(user_id=test_users['alice'].id, user_name='Alice', post_type='offer', category='Books', title='Closed Book', description='desc desc desc', location='Hyderabad', status='closed')
        db.session.add_all([open_post, closed_post])
        db.session.commit()

        stats = get_community_impact_stats()

        assert stats['active_posts_count'] == 1
        assert stats['closed_posts_count'] == 1
        # Crucial check: completed_exchanges_count must be 0!
        assert stats['completed_exchanges_count'] == 0


def test_completed_exchange_increments_stat(app, test_users):
    """Verify completed exchange properly increments completed metric."""
    with app.app_context():
        post = Post(user_id=test_users['alice'].id, user_name='Alice', post_type='offer', category='Clothes', title='Warm Clothes', description='desc desc desc', location='Hyderabad', status='completed')
        req = ExchangeRequest(post_id=1, requester_id=test_users['bob'].id, message='Thanks', status='completed')
        db.session.add_all([post, req])
        db.session.commit()

        stats = get_community_impact_stats()
        assert stats['completed_exchanges_count'] >= 1


def test_health_check_endpoint(client):
    """Verify /health endpoint returns healthy status and 200 code."""
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
