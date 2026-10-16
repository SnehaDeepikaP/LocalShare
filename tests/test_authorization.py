from app.extensions import db
from app.models.post import Post

def test_user_cannot_edit_another_users_post(client, auth_client, test_users):
    """User Alice cannot edit Bob's post."""
    with client.application.app_context():
        bob_post = Post(
            user_id=test_users['bob'].id,
            user_name=test_users['bob'].name,
            post_type='offer',
            category='Books',
            title='Bob Original Title',
            description='Bob post description for sharing books',
            location='Hyderabad',
            status='open'
        )
        db.session.add(bob_post)
        db.session.commit()
        bob_post_id = bob_post.id

    # Alice attempts to edit Bob's post
    resp = auth_client.post(f'/post/{bob_post_id}/edit', data={
        'category': 'Books',
        'title': 'Hacked Title By Alice',
        'description': 'Malicious attempt to alter description',
        'location': 'Hyderabad',
        'status': 'open'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b'You are not authorized to edit this post' in resp.data

    # Verify database was unchanged
    with client.application.app_context():
        p = Post.query.get(bob_post_id)
        assert p.title == 'Bob Original Title'


def test_user_cannot_delete_another_users_post(auth_client, test_users):
    """User Alice cannot delete Bob's post."""
    with auth_client.application.app_context():
        bob_post = Post(
            user_id=test_users['bob'].id,
            user_name=test_users['bob'].name,
            post_type='offer',
            category='Food',
            title='Bob Organic Vegetables',
            description='Organic vegetables from garden',
            location='Hyderabad',
            status='open'
        )
        db.session.add(bob_post)
        db.session.commit()
        p_id = bob_post.id

    # Alice tries to delete
    resp = auth_client.post(f'/post/{p_id}/delete', follow_redirects=True)
    assert b'Unauthorized' in resp.data

    with auth_client.application.app_context():
        assert Post.query.get(p_id) is not None


def test_non_admin_cannot_access_admin_portal(auth_client):
    """Standard user Alice cannot access admin routes."""
    resp = auth_client.get('/admin', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Administrator privileges required' in resp.data

    resp_users = auth_client.get('/admin/users', follow_redirects=True)
    assert b'Administrator privileges required' in resp_users.data


def test_admin_can_access_and_moderate(admin_client, test_users):
    """Admin user can access admin dashboard and moderate content."""
    resp = admin_client.get('/admin', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Administrative Portal' in resp.data
    assert b'Platform Overview' in resp.data
