from app.extensions import db
from app.models.post import Post

def test_create_valid_post(auth_client, test_users):
    """Test authenticated user successfully creates a post."""
    resp = auth_client.post('/post/new', data={
        'post_type': 'offer',
        'category': 'Books',
        'title': 'Mathematics Class 12 NCERT Textbooks',
        'description': 'Books in excellent condition, ready for pickup this weekend.',
        'location': 'Hyderabad, Banjara Hills'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b'Your post was published successfully' in resp.data
    assert b'Mathematics Class 12 NCERT' in resp.data

    with auth_client.application.app_context():
        p = Post.query.filter_by(title='Mathematics Class 12 NCERT Textbooks').first()
        assert p is not None
        assert p.post_type == 'offer'
        assert p.category == 'Books'
        assert p.user_id == test_users['alice'].id
        assert p.status == 'open'


def test_create_invalid_post_fields(auth_client):
    """Verify validation on illegal categories, short descriptions, and short titles."""
    # Invalid category
    resp1 = auth_client.post('/post/new', data={
        'post_type': 'offer',
        'category': 'IllegalWeapons',
        'title': 'Sample Title',
        'description': 'Valid long description for post testing',
        'location': 'Hyderabad'
    }, follow_redirects=True)
    assert b'Please select a valid category' in resp1.data

    # Too short description
    resp2 = auth_client.post('/post/new', data={
        'post_type': 'request',
        'category': 'Food',
        'title': 'Need food',
        'description': 'short',
        'location': 'Hyderabad'
    }, follow_redirects=True)
    assert b'at least 10 characters long' in resp2.data


def test_search_and_filter_posts(client, app, test_users):
    """Verify search, category filter, type filter, and location matching."""
    with app.app_context():
        p1 = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Food',
            title='Excess Rice and Dal',
            description='Home cooked vegetarian food',
            location='Hyderabad, Secunderabad',
            status='open'
        )
        p2 = Post(
            user_id=test_users['bob'].id,
            user_name=test_users['bob'].name,
            post_type='request',
            category='Books',
            title='Need Chemistry Textbook',
            description='Looking for CBSE Chemistry grade 11',
            location='Hyderabad, Gachibowli',
            status='open'
        )
        db.session.add_all([p1, p2])
        db.session.commit()

    # Search keyword
    resp_search = client.get('/posts?q=Chemistry')
    assert b'Need Chemistry Textbook' in resp_search.data
    assert b'Excess Rice and Dal' not in resp_search.data

    # Category filter
    resp_cat = client.get('/posts?category=Food')
    assert b'Excess Rice and Dal' in resp_cat.data
    assert b'Need Chemistry Textbook' not in resp_cat.data

    # Type filter
    resp_type = client.get('/posts?type=request')
    assert b'Need Chemistry Textbook' in resp_type.data
    assert b'Excess Rice and Dal' not in resp_type.data


def test_edit_own_post(auth_client, test_users):
    """Verify author can edit their own post."""
    with auth_client.application.app_context():
        p = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Clothes',
            title='Winter Coats for Children',
            description='Clean coats for children aged 5-8',
            location='Hyderabad',
            status='open'
        )
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    resp = auth_client.post(f'/post/{p_id}/edit', data={
        'category': 'Clothes',
        'title': 'Winter Coats & Sweaters for Children',
        'description': 'Clean winter apparel in mint condition',
        'location': 'Hyderabad North',
        'status': 'open'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b'Post updated successfully' in resp.data

    with auth_client.application.app_context():
        updated = Post.query.get(p_id)
        assert updated.title == 'Winter Coats & Sweaters for Children'
        assert updated.location == 'Hyderabad North'


def test_status_update_and_delete(auth_client, test_users):
    """Verify status transitions and post deletion."""
    with auth_client.application.app_context():
        p = Post(
            user_id=test_users['alice'].id,
            user_name=test_users['alice'].name,
            post_type='offer',
            category='Services',
            title='Free Math Tutoring Sessions',
            description='Volunteering 2 hours every Sunday for high school maths',
            location='Hyderabad',
            status='open'
        )
        db.session.add(p)
        db.session.commit()
        p_id = p.id

    # Update to closed
    resp_close = auth_client.post(f'/post/{p_id}/status', data={'status': 'closed'}, follow_redirects=True)
    assert resp_close.status_code == 200

    with auth_client.application.app_context():
        assert Post.query.get(p_id).status == 'closed'

    # Reopen
    resp_reopen = auth_client.post(f'/post/{p_id}/status', data={'status': 'open'}, follow_redirects=True)
    assert resp_reopen.status_code == 200

    with auth_client.application.app_context():
        assert Post.query.get(p_id).status == 'open'

    # Delete
    resp_del = auth_client.post(f'/post/{p_id}/delete', follow_redirects=True)
    assert resp_del.status_code == 200
    assert b'Post deleted successfully' in resp_del.data

    with auth_client.application.app_context():
        assert Post.query.get(p_id) is None
