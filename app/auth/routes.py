import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db
from app.models.user import User
from app.services.security_service import (
    require_csrf, login_required, is_rate_limited, record_failed_attempt, clear_rate_limit
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
            return render_template('register.html', name=name, email=email, location=location)

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

    return render_template('register.html')


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
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Check if account is suspended
            if user.is_suspended:
                flash('Your account has been suspended by an administrator for violating community guidelines.', 'danger')
                return render_template('login.html', email=email)

            if not user.is_active:
                flash('Your account is currently deactivated.', 'danger')
                return render_template('login.html', email=email)

            # Successful login
            clear_rate_limit(rate_key)
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['role'] = user.role
            session['location'] = user.location
            session.permanent = True

            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            record_failed_attempt(rate_key)
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


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

    return render_template('profile.html', user=user)
