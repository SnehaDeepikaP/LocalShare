from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models.post import Post
from app.services.security_service import login_required
from app.services.matching_service import get_matches_for_post, get_user_dashboard_matches

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/matches')
@login_required
def matches_dashboard():
    matches = get_user_dashboard_matches(session['user_id'], limit=10)
    my_posts = Post.query.filter_by(user_id=session['user_id'], status='open').all()
    return render_template('matches.html', matches=matches, my_posts=my_posts)


@matching_bp.route('/post/<int:post_id>/matches')
def post_matches(post_id):
    post = Post.query.get_or_404(post_id)
    matches = get_matches_for_post(post, limit=6, min_score=20)
    return render_template('post_matches.html', target_post=post, matches=matches)
