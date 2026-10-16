from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.post import Post, VALID_CATEGORIES
from app.models.exchange import ExchangeRequest
from app.models.report import Report

def get_community_impact_stats():
    """
    Calculate real, verified impact metrics directly from database records.
    Distinguishes strictly between 'closed' posts and 'completed' exchanges.
    """
    members_count = User.query.filter_by(is_active=True, is_suspended=False).count()
    active_posts_count = Post.query.filter_by(status='open').count()
    offers_count = Post.query.filter_by(status='open', post_type='offer').count()
    requests_count = Post.query.filter_by(status='open', post_type='request').count()
    
    # Completed exchanges count from exchange requests marked completed
    completed_exchanges_count = ExchangeRequest.query.filter_by(status='completed').count()
    # Alternatively count posts marked completed
    completed_posts_count = Post.query.filter_by(status='completed').count()
    # Total completed impact events
    total_completed = max(completed_exchanges_count, completed_posts_count)

    pending_requests_count = ExchangeRequest.query.filter_by(status='pending').count()
    closed_posts_count = Post.query.filter_by(status='closed').count()

    # Category breakdown for all posts
    category_counts = {}
    for cat in VALID_CATEGORIES:
        count = Post.query.filter_by(category=cat, status='open').count()
        category_counts[cat] = count

    # Sustainability and Reuse Metrics
    from app.models.review import ExchangeReview
    reused_count = ExchangeReview.query.filter_by(was_reused_or_repaired=True).count()
    # Transparent estimated waste diversion: 3.2 kg average solid waste avoided per reused item
    estimated_waste_diverted_kg = round(reused_count * 3.2, 1)

    return {
        'members_count': members_count,
        'active_posts_count': active_posts_count,
        'offers_count': offers_count,
        'requests_count': requests_count,
        'completed_exchanges_count': total_completed,
        'pending_requests_count': pending_requests_count,
        'closed_posts_count': closed_posts_count,
        'category_counts': category_counts,
        'reused_count': reused_count,
        'estimated_waste_diverted_kg': estimated_waste_diverted_kg
    }


def get_admin_overview_stats():
    """Detailed platform metrics for administrative dashboard."""
    base_stats = get_community_impact_stats()
    base_stats['total_users'] = User.query.count()
    base_stats['suspended_users'] = User.query.filter_by(is_suspended=True).count()
    base_stats['total_posts'] = Post.query.count()
    base_stats['total_requests'] = ExchangeRequest.query.count()
    base_stats['open_reports'] = Report.query.filter_by(status='open').count()
    base_stats['total_reports'] = Report.query.count()
    return base_stats
