from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from sqlalchemy import or_
from app.extensions import db
from app.models.post import Post, VALID_CATEGORIES, VALID_TYPES, VALID_STATUSES
from app.models.exchange import ExchangeRequest
from app.services.security_service import require_csrf, login_required
from app.services.matching_service import get_matches_for_post

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts')
def posts():
    post_type = request.args.get('type', '').strip().lower()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()
    query_text = request.args.get('q', '').strip()
    status_filter = request.args.get('status', 'open').strip().lower()
    sort_by = request.args.get('sort', 'newest').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Base query
    query = Post.query

    # Status filter
    if status_filter in VALID_STATUSES:
        query = query.filter(Post.status == status_filter)
    elif status_filter == 'all':
        pass  # no status filter
    else:
        query = query.filter(Post.status == 'open')

    # Type filter
    if post_type in VALID_TYPES:
        query = query.filter(Post.post_type == post_type)

    # Category filter
    if category in VALID_CATEGORIES:
        query = query.filter(Post.category == category)

    # Location filter
    if location:
        query = query.filter(Post.location.ilike(f'%{location}%'))

    # Keyword search (title or description)
    if query_text:
        search_filter = or_(
            Post.title.ilike(f'%{query_text}%'),
            Post.description.ilike(f'%{query_text}%')
        )
        query = query.filter(search_filter)

    # Sorting
    if sort_by == 'oldest':
        query = query.order_by(Post.created_at.asc())
    elif sort_by == 'title':
        query = query.order_by(Post.title.asc())
    else:
        query = query.order_by(Post.created_at.desc())

    # Pagination execution
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    all_posts = pagination.items

    return render_template(
        'posts.html',
        posts=all_posts,
        pagination=pagination,
        selected_type=post_type,
        selected_category=category,
        location_filter=location,
        query_text=query_text,
        status_filter=status_filter,
        sort_by=sort_by,
        categories=VALID_CATEGORIES
    )


@posts_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Check if logged-in user already has a pending exchange request for this post
    existing_request = None
    if 'user_id' in session:
        existing_request = ExchangeRequest.query.filter_by(
            post_id=post.id,
            requester_id=session['user_id']
        ).first()

    # Get smart recommendations if post is open
    recommended_matches = []
    if post.status == 'open':
        recommended_matches = get_matches_for_post(post, limit=3)

    return render_template(
        'post_detail.html',
        post=post,
        existing_request=existing_request,
        recommended_matches=recommended_matches
    )


@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@require_csrf
def new_post():
    if request.method == 'POST':
        post_type = request.form.get('post_type', '').strip().lower()
        category = request.form.get('category', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()

        errors = []
        if post_type not in VALID_TYPES:
            errors.append('Invalid post type. Choose Offer or Request.')
        if category not in VALID_CATEGORIES:
            errors.append('Please select a valid category from the list.')
        if not title or len(title) < 4 or len(title) > 200:
            errors.append('Title must be between 4 and 200 characters.')
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters long.')
        if not location or len(location) < 2 or len(location) > 120:
            errors.append('Location is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'new_post.html',
                post_type=post_type,
                category=category,
                title=title,
                description=description,
                location=location,
                categories=VALID_CATEGORIES
            )

        post = Post(
            user_id=session['user_id'],
            user_name=session['user_name'],
            post_type=post_type,
            category=category,
            title=title,
            description=description,
            location=location,
            status='open'
        )
        db.session.add(post)
        db.session.commit()

        flash('Your post was published successfully!', 'success')
        return redirect(url_for('posts.success', post_id=post.id))

    return render_template('new_post.html', categories=VALID_CATEGORIES)


@posts_bp.route('/success/<int:post_id>')
def success(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('success.html', post=post)


@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@require_csrf
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Authorization check: only author or admin
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You are not authorized to edit this post.', 'danger')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        status = request.form.get('status', post.status).strip()

        errors = []
        if category not in VALID_CATEGORIES:
            errors.append('Invalid category.')
        if not title or len(title) < 4 or len(title) > 200:
            errors.append('Title must be between 4 and 200 characters.')
        if not description or len(description) < 10:
            errors.append('Description must be at least 10 characters.')
        if not location:
            errors.append('Location is required.')
        if status not in VALID_STATUSES:
            errors.append('Invalid status.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('edit_post.html', post=post, categories=VALID_CATEGORIES)

        post.category = category
        post.title = title
        post.description = description
        post.location = location
        post.status = status
        db.session.commit()

        flash('Post updated successfully.', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    return render_template('edit_post.html', post=post, categories=VALID_CATEGORIES)


@posts_bp.route('/post/<int:post_id>/status', methods=['POST'])
@login_required
@require_csrf
def update_status(post_id):
    post = Post.query.get_or_404(post_id)

    # Authorization: author or admin
    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized to update this post.', 'danger')
        return redirect(url_for('posts.post_detail', post_id=post.id))

    new_status = request.form.get('status', '').strip().lower()
    if new_status in VALID_STATUSES:
        post.status = new_status
        db.session.commit()
        flash(f'Post status updated to {new_status.replace("_", " ")}.', 'info')
    else:
        flash('Invalid status transition.', 'danger')

    return redirect(request.referrer or url_for('posts.post_detail', post_id=post.id))


@posts_bp.route('/post/close/<int:post_id>', methods=['GET', 'POST'])
@login_required
def close_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('posts.posts'))

    post.status = 'closed'
    db.session.commit()
    flash(f'"{post.title}" has been marked as closed.', 'info')
    return redirect(request.referrer or url_for('posts.posts'))


@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@require_csrf
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized to delete this post.', 'danger')
        return redirect(url_for('posts.posts'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', 'info')
    return redirect(url_for('posts.posts'))
