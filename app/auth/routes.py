import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db
from app.models.user import User
from app.services.security_service import (
    require_csrf, login_required, is_rate_limited, record_failed_attempt, clear_rate_limit
)
from app.services.google_auth_service import (
    is_google_auth_configured, generate_google_auth_url, exchange_google_code_for_userinfo
)

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

@auth_bp.route('/register', methods=['GET', 'POST'])
@require_csrf
def register():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        location = request.form.get('location', '').strip()

        # Server-side validation
        errors = []
        if not name or len(name) < 2 or len(name) > 100:
            errors.append('Name must be between 2 and 100 characters.')
        if not email or not EMAIL_REGEX.match(email) or len(email) > 120:
            errors.append('Please provide a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one uppercase letter and one number.')
        if not location or len(location) < 2 or len(location) > 120:
            errors.append('Location is required (up to 120 characters).')

        if User.query.filter_by(email=email).first():
            errors.append('This email is already registered. Please log in.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', name=name, email=email, location=location, is_google_configured=is_google_auth_configured())

        # Create user with securely hashed password
        user = User(
            name=name,
            email=email,
            location=location,
            role='user',
            is_active=True,
            is_suspended=False
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', is_google_configured=is_google_auth_configured())


@auth_bp.route('/login', methods=['GET', 'POST'])
@require_csrf
def login():
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        client_ip = request.remote_addr or 'unknown'
        rate_key = f"{client_ip}:{email}"

        # Rate limiting check
        limited, wait_or_remaining = is_rate_limited(
            rate_key,
            max_attempts=current_app.config.get('LOGIN_RATE_LIMIT_ATTEMPTS', 5),
            window_seconds=current_app.config.get('LOGIN_RATE_LIMIT_WINDOW_SECONDS', 300)
        )
        if limited:
            flash(f'Too many failed login attempts. Please wait {wait_or_remaining} seconds before trying again.', 'danger')
            return render_template('login.html', email=email, is_google_configured=is_google_auth_configured())

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Check if account is suspended
            if user.is_suspended:
                flash('Your account has been suspended by an administrator for violating community guidelines.', 'danger')
                return render_template('login.html', email=email, is_google_configured=is_google_auth_configured())

            if not user.is_active:
                flash('Your account is currently deactivated.', 'danger')
                return render_template('login.html', email=email, is_google_configured=is_google_auth_configured())

            # Successful login
            clear_rate_limit(rate_key)
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['role'] = user.role
            session['location'] = user.location
            session['avatar_url'] = user.avatar_url
            session.permanent = True

            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            record_failed_attempt(rate_key)
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', is_google_configured=is_google_auth_configured())


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@require_csrf
def profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            name = request.form.get('name', '').strip()
            location = request.form.get('location', '').strip()

            if not name or len(name) < 2:
                flash('Name must be at least 2 characters.', 'danger')
            elif not location or len(location) < 2:
                flash('Location is required.', 'danger')
            else:
                user.name = name
                user.location = location
                session['user_name'] = name
                session['location'] = location
                db.session.commit()
                flash('Profile updated successfully.', 'success')

        elif action == 'change_password':
            current_pwd = request.form.get('current_password', '').strip()
            new_pwd = request.form.get('new_password', '').strip()
            confirm_pwd = request.form.get('confirm_password', '').strip()

            if not user.check_password(current_pwd):
                flash('Current password incorrect.', 'danger')
            elif len(new_pwd) < 6 or not any(c.isupper() for c in new_pwd) or not any(c.isdigit() for c in new_pwd):
                flash('New password must be at least 6 characters with 1 uppercase letter and 1 number.', 'danger')
            elif new_pwd != confirm_pwd:
                flash('New passwords do not match.', 'danger')
            else:
                user.set_password(new_pwd)
                db.session.commit()
                flash('Password changed successfully.', 'success')

        return redirect(url_for('auth.profile'))

    is_google_configured = is_google_auth_configured()
    return render_template('profile.html', user=user, is_google_configured=is_google_configured)


@auth_bp.route('/google')
def login_google():
    """Initiates Google OpenID Connect OAuth authorization flow."""
    if 'user_id' in session:
        return redirect(url_for('main.home'))

    if not is_google_auth_configured():
        flash(
            'Google Sign-In is not currently configured by the administrator (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required). Please use email and password to log in.',
            'info'
        )
        return redirect(url_for('auth.login'))

    auth_url, _ = generate_google_auth_url()
    if not auth_url:
        flash('Could not initialize Google authentication service.', 'danger')
        return redirect(url_for('auth.login'))

    return redirect(auth_url)


@auth_bp.route('/google/callback')
def google_callback():
    """Handles Google OAuth authorization response."""
    if not is_google_auth_configured():
        flash('Google authentication is not configured.', 'danger')
        return redirect(url_for('auth.login'))

    code = request.args.get('code')
    returned_state = request.args.get('state')

    if not code:
        err = request.args.get('error', 'Google sign-in was cancelled.')
        flash(f'Google authentication error: {err}', 'warning')
        return redirect(url_for('auth.login'))

    userinfo, err = exchange_google_code_for_userinfo(code, returned_state)
    if err or not userinfo:
        flash(err or 'Failed to authenticate with Google.', 'danger')
        return redirect(url_for('auth.login'))

    google_sub = userinfo.get('sub')
    email = userinfo.get('email', '').strip().lower()
    name = userinfo.get('name') or userinfo.get('given_name') or 'Neighbor'
    avatar = userinfo.get('picture')

    # Case 1: Account already linked via Google stable sub ID
    user = User.query.filter_by(google_id=google_sub).first()
    if user:
        if user.is_suspended:
            flash('Your account has been suspended for violating community guidelines.', 'danger')
            return redirect(url_for('auth.login'))
        if not user.is_active:
            flash('Your account is currently deactivated.', 'danger')
            return redirect(url_for('auth.login'))

        # Update avatar if available
        if avatar and not user.avatar_url:
            user.avatar_url = avatar
            db.session.commit()

        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['role'] = user.role
        session['location'] = user.location
        session['avatar_url'] = user.avatar_url
        session.permanent = True

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('main.home'))

    # Case 2: User exists with this email, but NOT linked to this Google sub ID
    existing_user_by_email = User.query.filter_by(email=email).first()
    if existing_user_by_email:
        # Crucial security requirement: Never silently link by email alone!
        flash(
            f'An account with email {email} already exists with password sign-in. '
            'To protect your account, please log in with your password first, then connect your Google identity in Profile Settings.',
            'warning'
        )
        return redirect(url_for('auth.login'))

    # Case 3: Brand new user registration via Google
    import secrets
    new_user = User(
        name=name[:100],
        email=email,
        location='Neighborhood (Set in Profile)',
        role='user',
        is_active=True,
        is_suspended=False,
        google_id=google_sub,
        avatar_url=avatar
    )
    # Set random unreachable password
    new_user.set_password(secrets.token_urlsafe(32))

    db.session.add(new_user)
    db.session.commit()

    session.clear()
    session['user_id'] = new_user.id
    session['user_name'] = new_user.name
    session['user_email'] = new_user.email
    session['role'] = new_user.role
    session['location'] = new_user.location
    session['avatar_url'] = new_user.avatar_url
    session.permanent = True

    flash(f'Welcome to LocalShare, {new_user.name}! Your account has been created with Google.', 'success')
    return redirect(url_for('main.dashboard'))


@auth_bp.route('/users/<int:user_id>')
def public_profile(user_id):
    """Public community profile with privacy protection and verified reputation."""
    user = User.query.get_or_404(user_id)
    if user.is_suspended:
        flash('This profile is unavailable.', 'warning')
        return redirect(url_for('posts.posts'))

    active_posts = user.posts.filter_by(status='open').all()
    reviews = user.reviews_received.order_by(db.desc('created_at')).limit(10).all()
    completed_handover_count = user.sent_requests.filter_by(status='completed').count()

    return render_template(
        'public_profile.html',
        member=user,
        active_posts=active_posts,
        reviews=reviews,
        completed_count=completed_handover_count
    )
