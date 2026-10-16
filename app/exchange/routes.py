from flask import Blueprint, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.post import Post
from app.models.exchange import ExchangeRequest, VALID_REQUEST_STATUSES
from app.services.security_service import require_csrf, login_required

exchange_bp = Blueprint('exchange', __name__)

@exchange_bp.route('/exchange/request/<int:post_id>', methods=['POST'])
@login_required
@require_csrf
def create_request(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session['user_id']

    # Validation: cannot request own post
    if post.user_id == user_id:
        flash('You cannot express interest in your own post.', 'warning')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    # Validation: post must be open
    if post.status != 'open':
        flash('This post is no longer accepting new exchange requests.', 'warning')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    # Validation: duplicate active request check
    existing = ExchangeRequest.query.filter_by(
        post_id=post.id,
        requester_id=user_id
    ).filter(ExchangeRequest.status.in_(['pending', 'accepted'])).first()

    if existing:
        flash('You already have an active request for this post.', 'info')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    message = request.form.get('message', '').strip()
    contact_info = request.form.get('contact_info', '').strip()

    if not message or len(message) < 5:
        flash('Please include a brief note explaining your interest (at least 5 characters).', 'danger')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    req = ExchangeRequest(
        post_id=post.id,
        requester_id=user_id,
        message=message,
        contact_info=contact_info,
        status='pending'
    )
    db.session.add(req)
    db.session.commit()

    flash('Interest request submitted! The post owner will be notified on their dashboard.', 'success')
    return redirect(url_for('posts.post_detail', post_id=post.id))


@exchange_bp.route('/exchange/<int:request_id>/respond', methods=['POST'])
@login_required
@require_csrf
def respond_request(request_id):
    req = ExchangeRequest.query.get_or_404(request_id)
    post = req.post

    # Authorization: only post owner can accept or decline
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized to manage this request.', 'danger')
        return redirect(url_for('main.dashboard'))

    action = request.form.get('action', '').strip().lower()  # 'accept' or 'decline'
    response_note = request.form.get('response_note', '').strip()

    if action == 'accept':
        req.status = 'accepted'
        req.response_note = response_note or 'Accepted! Let us coordinate the exchange details.'
        # Optionally move post to in_progress
        if post.status == 'open':
            post.status = 'in_progress'
        db.session.commit()
        flash(f'Request accepted from {req.requester.name}. Coordination details are now unlocked.', 'success')
    elif action == 'decline':
        req.status = 'declined'
        req.response_note = response_note or 'Thank you for your interest, but this item/request is no longer available.'
        db.session.commit()
        flash('Request declined.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('main.dashboard'))


@exchange_bp.route('/exchange/<int:request_id>/complete', methods=['POST'])
@login_required
@require_csrf
def complete_exchange(request_id):
    req = ExchangeRequest.query.get_or_404(request_id)
    post = req.post
    user_id = session['user_id']

    # Authorization: either post owner, requester, or admin
    if user_id != post.user_id and user_id != req.requester_id and session.get('role') != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.dashboard'))

    req.status = 'completed'
    post.status = 'completed'
    db.session.commit()

    flash('Congratulations! The community exchange has been marked as successfully completed.', 'success')
    return redirect(url_for('main.dashboard'))


@exchange_bp.route('/exchange/<int:request_id>/cancel', methods=['POST'])
@login_required
@require_csrf
def cancel_request(request_id):
    req = ExchangeRequest.query.get_or_404(request_id)

    # Authorization: only requester or admin can cancel
    if req.requester_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.dashboard'))

    req.status = 'cancelled'
    db.session.commit()
    flash('Your interest request has been cancelled.', 'info')
    return redirect(url_for('main.dashboard'))
