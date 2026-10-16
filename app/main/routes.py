from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.extensions import db
from app.models.post import Post
from app.models.exchange import ExchangeRequest
from app.models.report import Report, VALID_REPORT_REASONS
from app.models.user import User
from app.services.security_service import require_csrf, login_required
from app.services.stats_service import get_community_impact_stats
from app.services.matching_service import get_user_dashboard_matches

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    stats = get_community_impact_stats()
    recent_posts = Post.query.filter_by(status='open').order_by(Post.created_at.desc()).limit(6).all()
    return render_template(
        'index.html',
        stats=stats,
        recent_posts=recent_posts,
        user_count=stats['members_count'],
        post_count=stats['active_posts_count'],
        offer_count=stats['offers_count']
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)

    # User's own posts
    my_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    
    # Incoming requests: requests where the post belongs to this user
    incoming_requests = ExchangeRequest.query.join(Post, ExchangeRequest.post_id == Post.id)\
        .filter(Post.user_id == user_id)\
        .order_by(ExchangeRequest.created_at.desc()).all()

    # Outgoing requests: requests filed by this user
    outgoing_requests = ExchangeRequest.query.filter_by(requester_id=user_id)\
        .order_by(ExchangeRequest.created_at.desc()).all()

    # Saved Watchlist
    from app.models.saved_listing import SavedListing
    from app.models.notification import Notification
    saved_listings = SavedListing.query.filter_by(user_id=user_id)\
        .order_by(SavedListing.created_at.desc()).all()

    # In-App Notifications
    notifications = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.created_at.desc()).limit(25).all()

    # Recommended matches for user
    matches = get_user_dashboard_matches(user_id, limit=4)

    return render_template(
        'dashboard.html',
        user=user,
        my_posts=my_posts,
        incoming_requests=incoming_requests,
        outgoing_requests=outgoing_requests,
        saved_listings=saved_listings,
        notifications=notifications,
        matches=matches
    )


@main_bp.route('/impact')
def impact():
    stats = get_community_impact_stats()
    return render_template('impact.html', stats=stats)


@main_bp.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')


@main_bp.route('/report/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@require_csrf
def report_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        details = request.form.get('details', '').strip()

        if reason not in VALID_REPORT_REASONS:
            flash('Please select a valid report reason.', 'danger')
            return render_template('report.html', target_type='post', target=post, reasons=VALID_REPORT_REASONS)

        if not details or len(details) < 10:
            flash('Please describe the issue in at least 10 characters.', 'danger')
            return render_template('report.html', target_type='post', target=post, reasons=VALID_REPORT_REASONS)

        report = Report(
            reporter_id=session['user_id'],
            post_id=post.id,
            reported_user_id=post.user_id,
            reason=reason,
            details=details,
            status='open'
        )
        db.session.add(report)
        db.session.commit()

        flash('Thank you. Your report has been submitted to the moderation team.', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    return render_template('report.html', target_type='post', target=post, reasons=VALID_REPORT_REASONS)


@main_bp.route('/report/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@require_csrf
def report_user(user_id):
    reported_user = User.query.get_or_404(user_id)

    if reported_user.id == session['user_id']:
        flash('You cannot report yourself.', 'warning')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        details = request.form.get('details', '').strip()

        if reason not in VALID_REPORT_REASONS:
            flash('Please select a valid report reason.', 'danger')
            return render_template('report.html', target_type='user', target=reported_user, reasons=VALID_REPORT_REASONS)

        if not details or len(details) < 10:
            flash('Please provide details for the report (at least 10 characters).', 'danger')
            return render_template('report.html', target_type='user', target=reported_user, reasons=VALID_REPORT_REASONS)

        report = Report(
            reporter_id=session['user_id'],
            reported_user_id=reported_user.id,
            reason=reason,
            details=details,
            status='open'
        )
        db.session.add(report)
        db.session.commit()

        flash('Your report against this user has been submitted for moderation.', 'success')
        return redirect(url_for('main.home'))

    return render_template('report.html', target_type='user', target=reported_user, reasons=VALID_REPORT_REASONS)


@main_bp.route('/health')
def health_check():
    """Production health check endpoint verifying database connectivity."""
    db_ok = True
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception as e:
        db_ok = False

    status_code = 200 if db_ok else 503
    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected',
        'service': 'LocalShare Community Platform'
    }), status_code
