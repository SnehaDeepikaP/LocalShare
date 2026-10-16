import re
from datetime import datetime
from app.models.post import Post
from app.models.user import User

# Common stop words for keyword extraction
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
    'any', 'are', 'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being',
    'below', 'between', 'both', 'but', 'by', 'can', 'cannot', 'could', 'did', 'do',
    'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
    'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
    'let', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out',
    'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that',
    'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
    'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
    'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves'
}

def extract_keywords(text):
    """Normalize text into lowercase alphanumeric tokens excluding stopwords."""
    if not text:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}


def calculate_jaccard_similarity(tokens_a, tokens_b):
    """Compute Jaccard similarity coefficient between two token sets."""
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    if not union:
        return 0.0
    return len(intersection) / len(union)


def score_location(loc_a, loc_b):
    """
    Compute location proximity score (0 to 10 points).
    10: Exact match (case-insensitive)
    8:  Sub-string containment (e.g. 'Hyderabad' and 'Hyderabad, Gachibowli')
    5:  Common location tokens
    0:  No overlap
    """
    if not loc_a or not loc_b:
        return 0, "No location data"
    
    clean_a = loc_a.strip().lower()
    clean_b = loc_b.strip().lower()

    if clean_a == clean_b:
        return 10, f"Same location area ({loc_a})"
    
    if clean_a in clean_b or clean_b in clean_a:
        return 8, f"Nearby location match ({loc_a} ~ {loc_b})"

    tokens_a = set(re.findall(r'[a-zA-Z0-9]+', clean_a))
    tokens_b = set(re.findall(r'[a-zA-Z0-9]+', clean_b))
    overlap = tokens_a.intersection(tokens_b)
    if overlap:
        return 5, f"Shared location keywords: {', '.join(overlap)}"

    return 0, f"Different locations ({loc_a} vs {loc_b})"


def calculate_match_score(target_post, candidate_post):
    """
    Calculate deterministic matching score (0 to 100) and explainable factors
    between a target post and a candidate post.
    """
    # Exclusion criteria:
    # 1. Candidate must be open
    if candidate_post.status != 'open':
        return 0, [], "Candidate post is not open"

    # 2. Cannot match a post with itself or the same author
    if target_post.id == candidate_post.id or target_post.user_id == candidate_post.user_id:
        return 0, [], "Cannot match post against same user or post"

    score = 0
    factors = []

    # Factor 1: Post Type Compatibility (Weight: 40 points)
    if (target_post.post_type == 'request' and candidate_post.post_type == 'offer') or \
       (target_post.post_type == 'offer' and candidate_post.post_type == 'request'):
        type_score = 40
        type_reason = f"Complementary need and supply: {target_post.post_type.capitalize()} matches {candidate_post.post_type.capitalize()}."
    else:
        type_score = 0
        type_reason = f"Same post type ({target_post.post_type}): not directly complementary."
    score += type_score
    factors.append({
        'factor': 'Type Compatibility',
        'score': type_score,
        'max_score': 40,
        'reason': type_reason
    })

    # Factor 2: Category Match (Weight: 30 points)
    if target_post.category == candidate_post.category:
        cat_score = 30
        cat_reason = f"Exact category match: {target_post.category}."
    else:
        cat_score = 0
        cat_reason = f"Different categories ({target_post.category} vs {candidate_post.category})."
    score += cat_score
    factors.append({
        'factor': 'Category Relevance',
        'score': cat_score,
        'max_score': 30,
        'reason': cat_reason
    })

    # Factor 3: Text & Keyword Similarity (Weight: 20 points)
    target_tokens = extract_keywords(f"{target_post.title} {target_post.description}")
    candidate_tokens = extract_keywords(f"{candidate_post.title} {candidate_post.description}")
    shared_tokens = target_tokens.intersection(candidate_tokens)
    jaccard = calculate_jaccard_similarity(target_tokens, candidate_tokens)
    
    if shared_tokens:
        kw_score = min(20, max(5, int(round(jaccard * 40))))
        kw_reason = f"Shared keywords: {', '.join(sorted(shared_tokens)[:4])} (similarity index {jaccard:.2f})."
    else:
        kw_score = 0
        kw_reason = "No overlapping resource keywords found in titles/descriptions."
    score += kw_score
    factors.append({
        'factor': 'Keyword Similarity',
        'score': kw_score,
        'max_score': 20,
        'reason': kw_reason
    })

    # Factor 4: Geographic Proximity (Weight: 10 points)
    loc_score, loc_reason = score_location(target_post.location, candidate_post.location)
    score += loc_score
    factors.append({
        'factor': 'Geographic Proximity',
        'score': loc_score,
        'max_score': 10,
        'reason': loc_reason
    })

    return score, factors, "Calculated based on type, category, keyword, and location similarity."


def rank_matches(target_post, candidate_posts, min_score=30, limit=6):
    """
    Ranks candidate posts against the target post, applying minimum score threshold
    and deterministic tie-breaking.
    """
    results = []
    for cand in candidate_posts:
        score, factors, summary = calculate_match_score(target_post, cand)
        if score >= min_score:
            results.append({
                'post': cand,
                'score': score,
                'factors': factors,
                'summary': summary
            })

    # Deterministic sorting
    results.sort(
        key=lambda item: (
            -item['score'],
            -item['post'].created_at.timestamp() if item['post'].created_at else 0,
            item['post'].id
        )
    )

    return results[:limit]


def get_matches_for_post(post, limit=6, min_score=30):
    """
    Find best matching candidate posts for a given post.
    Filters only open posts by active, non-suspended users.
    """
    if not post or post.status != 'open':
        return []

    candidates = Post.query.join(User, Post.user_id == User.id)\
        .filter(
            Post.id != post.id,
            Post.user_id != post.user_id,
            Post.status == 'open',
            User.is_suspended == False
        ).all()

    return rank_matches(post, candidates, min_score=min_score, limit=limit)


def get_user_dashboard_matches(user_id, limit=6):
    """
    Aggregate best matches across all active posts owned by the user.
    """
    user_posts = Post.query.filter_by(user_id=user_id, status='open').all()
    if not user_posts:
        return []

    aggregated_matches = {}
    for post in user_posts:
        matches = get_matches_for_post(post, limit=limit, min_score=30)
        for m in matches:
            cand_id = m['post'].id
            if cand_id not in aggregated_matches or m['score'] > aggregated_matches[cand_id]['score']:
                m['matched_with_my_post'] = post
                aggregated_matches[cand_id] = m

    sorted_list = sorted(
        aggregated_matches.values(),
        key=lambda x: -x['score']
    )
    return sorted_list[:limit]
