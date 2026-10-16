from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.post import Post
from app.models.exchange import ExchangeRequest, VALID_REQUEST_STATUSES
from app.models.message import ExchangeMessage
from app.models.review import ExchangeReview
from app.models.notification import Notification
from app.services.security_service import require_csrf, login_required

exchange_bp = Blueprint('exchange', __name__)

def create_notification(user_id, title, message, link=None):
    """Helper to dispatch in-app notifications cleanly."""
    try:
        notif = Notification(user_id=user_id, title=title, message=message, link=link)
        db.session.add(notif)
        db.session.commit()
    except Exception:
        db.session.rollback()

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
        return redirect(url_for('exchange.view_thread', request_id=existing.id))

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
    db.session.flush()

    # Automatically add the opening message into the conversation thread
    initial_msg = ExchangeMessage(
        exchange_id=req.id,
        sender_id=user_id,
        content=message
    )
    db.session.add(initial_msg)
    db.session.commit()

    # Notify post owner
    create_notification(
        user_id=post.user_id,
        title=f"New interest in {post.title[:30]}",
        message=f"{session['user_name']} sent a request: \"{message[:60]}...\"",
        link=url_for('exchange.view_thread', request_id=req.id)
    )

    flash('Interest request submitted! A private coordination thread has been opened.', 'success')
    return redirect(url_for('exchange.view_thread', request_id=req.id))


@exchange_bp.route('/exchange/<int:request_id>/thread', methods=['GET', 'POST'])
@login_required
@require_csrf
def view_thread(request_id):
    """Secure, authorized in-app message thread for an exchange request."""
    req = ExchangeRequest.query.get_or_404(request_id)
    post = req.post
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    # Strict authorization: Only requester, post owner, or admin
    if user_id != post.user_id and user_id != req.requester_id and not is_admin:
        abort(403)

    # Handle posting a new message in thread
    if request.method == 'POST':
        msg_text = request.form.get('content', '').strip()
        if not msg_text or len(msg_text) < 1 or len(msg_text) > 2000:
            flash('Message must be between 1 and 2000 characters.', 'danger')
        else:
            new_msg = ExchangeMessage(
                exchange_id=req.id,
                sender_id=user_id,
                content=msg_text
            )
            db.session.add(new_msg)
            db.session.commit()

            # Determine recipient
            recipient_id = post.user_id if user_id == req.requester_id else req.requester_id
            create_notification(
                user_id=recipient_id,
                title=f"New message from {session['user_name']}",
                message=msg_text[:70],
                link=url_for('exchange.view_thread', request_id=req.id)
            )
            flash('Message sent.', 'success')

        return redirect(url_for('exchange.view_thread', request_id=req.id))

    # Mark counterparty messages as read
    ExchangeMessage.query.filter(
        ExchangeMessage.exchange_id == req.id,
        ExchangeMessage.sender_id != user_id,
        ExchangeMessage.is_read == False
    ).update({'is_read': True})
    db.session.commit()

    messages = req.messages.order_by(ExchangeMessage.created_at.asc()).all()
    user_review = ExchangeReview.query.filter_by(exchange_id=req.id, reviewer_id=user_id).first()
    other_party = post.author if user_id == req.requester_id else req.requester

    return render_template(
        'exchange_thread.html',
        exchange=req,
        post=post,
        messages=messages,
        other_party=other_party,
        user_review=user_review
    )


@exchange_bp.route('/exchange/<int:request_id>/respond', methods=['POST'])
@login_required
@require_csrf
def respond_request(request_id):
    req = ExchangeRequest.query.get_or_404(request_id)
    post = req.post

    # Authorization: only post owner or admin can respond
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized to manage this request.', 'danger')
        return redirect(url_for('main.dashboard'))

    action = request.form.get('action', '').strip().lower()  # 'accept' or 'decline'
    response_note = request.form.get('response_note', '').strip()

    if action == 'accept':
        req.status = 'accepted'
        req.response_note = response_note or 'Accepted! Let us coordinate the exchange details.'
        if post.status == 'open':
            post.status = 'in_progress'
        db.session.commit()

        # Record acceptance as a message in thread
        accept_msg = ExchangeMessage(
            exchange_id=req.id,
            sender_id=session['user_id'],
            content=f"🤝 Request Accepted! {req.response_note}"
        )
        db.session.add(accept_msg)
        db.session.commit()

        create_notification(
            user_id=req.requester_id,
            title="Your exchange request was accepted!",
            message=f"{post.author.name} accepted your request for {post.title}.",
            link=url_for('exchange.view_thread', request_id=req.id)
        )
        flash(f'Request accepted from {req.requester.name}. Coordination details are now unlocked.', 'success')
    elif action == 'decline':
        req.status = 'declined'
        req.response_note = response_note or 'Thank you for your interest, but this item/request is no longer available.'
        db.session.commit()

        create_notification(
            user_id=req.requester_id,
            title="Exchange request update",
            message=f"Your request for {post.title} was declined.",
            link=url_for('posts.post_detail', post_id=post.id)
        )
        flash('Request declined.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('exchange.view_thread', request_id=req.id))


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

    # System message in thread
    completion_msg = ExchangeMessage(
        exchange_id=req.id,
        sender_id=user_id,
        content="🎉 The handover has been marked as successfully completed!"
    )
    db.session.add(completion_msg)
    db.session.commit()

    counterparty_id = post.user_id if user_id == req.requester_id else req.requester_id
    create_notification(
        user_id=counterparty_id,
        title="Exchange marked completed! 🌟",
        message=f"{session['user_name']} marked the exchange of {post.title} as completed. Leave a review!",
        link=url_for('exchange.view_thread', request_id=req.id)
    )

    flash('Congratulations! The community exchange has been completed. Please leave feedback below.', 'success')
    return redirect(url_for('exchange.view_thread', request_id=req.id))


@exchange_bp.route('/exchange/<int:request_id>/review', methods=['POST'])
@login_required
@require_csrf
def review_exchange(request_id):
    """Submits feedback and sustainability tracking for a completed exchange."""
    req = ExchangeRequest.query.get_or_404(request_id)
    post = req.post
    user_id = session['user_id']

    if req.status != 'completed':
        flash('Reviews can only be submitted after the exchange is completed.', 'warning')
        return redirect(url_for('exchange.view_thread', request_id=req.id))

    if user_id != post.user_id and user_id != req.requester_id:
        abort(403)

    existing = ExchangeReview.query.filter_by(exchange_id=req.id, reviewer_id=user_id).first()
    if existing:
        flash('You have already submitted a review for this exchange.', 'info')
        return redirect(url_for('exchange.view_thread', request_id=req.id))

    try:
        rating = int(request.form.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except ValueError:
        rating = 5

    comment = request.form.get('comment', '').strip()
    was_reused_or_repaired = bool(request.form.get('was_reused_or_repaired'))
    reviewee_id = post.user_id if user_id == req.requester_id else req.requester_id

    review = ExchangeReview(
        exchange_id=req.id,
        reviewer_id=user_id,
        reviewee_id=reviewee_id,
        rating=rating,
        comment=comment if comment else None,
        was_reused_or_repaired=was_reused_or_repaired
    )
    db.session.add(review)
    db.session.commit()

    create_notification(
        user_id=reviewee_id,
        title="New Community Feedback! ⭐",
        message=f"{session['user_name']} gave you a {rating}-star review for your exchange.",
        link=url_for('auth.public_profile', user_id=reviewee_id)
    )

    flash('Thank you for strengthening community trust! Your review has been recorded.', 'success')
    return redirect(url_for('exchange.view_thread', request_id=req.id))


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


@exchange_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
@require_csrf
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=session['user_id'], is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

