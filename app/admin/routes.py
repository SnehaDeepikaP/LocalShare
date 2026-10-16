from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.report import Report, VALID_REPORT_STATUSES
from app.models.audit import AuditLog
from app.services.security_service import require_csrf, admin_required
from app.services.stats_service import get_admin_overview_stats

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_bp.route('')
@admin_required
def index():
    stats = get_admin_overview_stats()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()
    return render_template(
        'admin/index.html',
        stats=stats,
        recent_reports=recent_reports,
        recent_audits=recent_audits
    )


@admin_bp.route('/users')
@admin_required
def users():
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = User.query
    if search:
        query = query.filter((User.name.ilike(f'%{search}%')) | (User.email.ilike(f'%{search}%')))
    if status_filter == 'suspended':
        query = query.filter(User.is_suspended == True)
    elif status_filter == 'active':
        query = query.filter(User.is_suspended == False)

    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, search=search, status_filter=status_filter)


@admin_bp.route('/user/<int:user_id>/toggle-suspend', methods=['POST'])
@admin_required
@require_csrf
def toggle_suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('You cannot suspend your own administrative account.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_suspended = not user.is_suspended
    action_name = 'suspend_user' if user.is_suspended else 'restore_user'
    
    # Audit log
    audit = AuditLog(
        admin_id=session['user_id'],
        action=action_name,
        target_type='user',
        target_id=user.id,
        details=f"Admin {session.get('user_name')} {'suspended' if user.is_suspended else 'restored'} user {user.email}"
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"User {user.email} has been {'suspended' if user.is_suspended else 'restored'}.", 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/user/<int:user_id>/toggle-role', methods=['POST'])
@admin_required
@require_csrf
def toggle_role_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('You cannot alter your own admin privileges.', 'danger')
        return redirect(url_for('admin.users'))

    user.role = 'user' if user.role == 'admin' else 'admin'
    audit = AuditLog(
        admin_id=session['user_id'],
        action='change_role',
        target_type='user',
        target_id=user.id,
        details=f"Admin {session.get('user_name')} changed role of {user.email} to {user.role}"
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"User role updated to {user.role}.", 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/posts')
@admin_required
def posts():
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Post.query
    if search:
        query = query.filter((Post.title.ilike(f'%{search}%')) | (Post.description.ilike(f'%{search}%')))
    if status_filter:
        query = query.filter(Post.status == status_filter)

    posts_list = query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts_list, search=search, status_filter=status_filter)


@admin_bp.route('/post/<int:post_id>/moderate', methods=['POST'])
@admin_required
@require_csrf
def moderate_post(post_id):
    post = Post.query.get_or_404(post_id)
    action = request.form.get('action', '').strip().lower()

    if action == 'close':
        post.status = 'closed'
        audit_action = 'close_post'
        flash(f'Post "{post.title}" marked as closed.', 'info')
    elif action == 'reopen':
        post.status = 'open'
        audit_action = 'reopen_post'
        flash(f'Post "{post.title}" reopened.', 'info')
    elif action == 'delete':
        audit_action = 'delete_post'
        title = post.title
        db.session.delete(post)
        flash(f'Post "{title}" removed.', 'info')
    else:
        flash('Invalid moderation action.', 'danger')
        return redirect(url_for('admin.posts'))

    audit = AuditLog(
        admin_id=session['user_id'],
        action=audit_action,
        target_type='post',
        target_id=post_id,
        details=f"Admin {session.get('user_name')} performed {audit_action} on post ID {post_id}"
    )
    db.session.add(audit)
    db.session.commit()

    return redirect(url_for('admin.posts'))


@admin_bp.route('/reports')
@admin_required
def reports():
    status_filter = request.args.get('status', 'open').strip()
    query = Report.query
    if status_filter != 'all':
        query = query.filter(Report.status == status_filter)

    reports_list = query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports_list, status_filter=status_filter)


@admin_bp.route('/report/<int:report_id>/action', methods=['POST'])
@admin_required
@require_csrf
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    resolution = request.form.get('resolution', '').strip().lower()  # 'dismiss' or 'action_taken'
    action_note = request.form.get('action_note', '').strip()

    if resolution in ('dismissed', 'action_taken'):
        report.status = resolution
        report.action_taken = action_note or f"Marked {resolution} by admin {session.get('user_name')}"
        
        audit = AuditLog(
            admin_id=session['user_id'],
            action=f"report_{resolution}",
            target_type='report',
            target_id=report.id,
            details=f"Admin resolved report #{report.id}: {report.action_taken}"
        )
        db.session.add(audit)
        db.session.commit()
        flash(f'Report #{report.id} marked as {resolution}.', 'success')
    else:
        flash('Invalid resolution status.', 'danger')

    return redirect(url_for('admin.reports'))


@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)
