from datetime import datetime, timezone
from app.models.post import Post
from app.matching.engine import calculate_match_score, rank_matches, score_location

def test_matching_complementary_types_and_category():
    """Verify offer and request in same category receive high compatibility score."""
    p_req = Post(
        id=1,
        user_id=10,
        post_type='request',
        category='Books',
        title='Need Class 10 NCERT Science and Maths',
        description='Looking for science textbook for exam preparation',
        location='Hyderabad',
        status='open'
    )
    p_off = Post(
        id=2,
        user_id=20,
        post_type='offer',
        category='Books',
        title='Offering Class 10 NCERT Science Book',
        description='Science textbook available for donation to students',
        location='Hyderabad',
        status='open'
    )

    score, factors, summary = calculate_match_score(p_req, p_off)

    # Score should be >= 80 (40 type + 30 category + kw + 10 location)
    assert score >= 80
    assert len(factors) == 4
    
    # Check factor weights
    f_dict = {f['factor']: f['score'] for f in factors}
    assert f_dict['Type Compatibility'] == 40
    assert f_dict['Category Relevance'] == 30
    assert f_dict['Geographic Proximity'] == 10
    assert f_dict['Keyword Similarity'] > 0


def test_matching_same_type_penalty():
    """Verify offer-vs-offer receives 0 type compatibility."""
    p1 = Post(id=1, user_id=1, post_type='offer', category='Food', title='Bread', description='Extra bread', location='Hyderabad', status='open')
    p2 = Post(id=2, user_id=2, post_type='offer', category='Food', title='Rice', description='Extra rice', location='Hyderabad', status='open')

    score, factors, _ = calculate_match_score(p1, p2)
    f_dict = {f['factor']: f['score'] for f in factors}
    assert f_dict['Type Compatibility'] == 0


def test_matching_excludes_closed_or_same_author():
    """Verify closed candidate posts or same-user posts are strictly excluded."""
    target = Post(id=1, user_id=1, post_type='request', category='Books', title='Books', description='desc', location='Hyderabad', status='open')
    closed_cand = Post(id=2, user_id=2, post_type='offer', category='Books', title='Books', description='desc', location='Hyderabad', status='closed')
    same_user_cand = Post(id=3, user_id=1, post_type='offer', category='Books', title='Books', description='desc', location='Hyderabad', status='open')

    score_closed, _, _ = calculate_match_score(target, closed_cand)
    assert score_closed == 0

    score_same_user, _, _ = calculate_match_score(target, same_user_cand)
    assert score_same_user == 0


def test_location_scoring_nuances():
    """Verify location exact, substring, and mismatch scoring."""
    score_exact, _ = score_location('Hyderabad', 'hyderabad')
    assert score_exact == 10

    score_sub, _ = score_location('Hyderabad', 'Hyderabad, Madhapur')
    assert score_sub == 8

    score_diff, _ = score_location('Mumbai', 'Delhi')
    assert score_diff == 0


def test_rank_matches_deterministic_ordering():
    """Verify ranking orders by score DESC and tie-breaks by date."""
    now = datetime.now(timezone.utc)
    target = Post(id=1, user_id=10, post_type='request', category='Food', title='Meals', description='Meals', location='Hyderabad', status='open')

    cand1 = Post(id=2, user_id=20, post_type='offer', category='Food', title='Meals', description='Meals', location='Hyderabad', status='open', created_at=now)
    cand2 = Post(id=3, user_id=30, post_type='offer', category='Books', title='Other', description='Other', location='Hyderabad', status='open', created_at=now)

    ranked = rank_matches(target, [cand2, cand1], min_score=30)
    assert len(ranked) >= 1
    # cand1 should rank first due to higher score
    assert ranked[0]['post'].id == 2
