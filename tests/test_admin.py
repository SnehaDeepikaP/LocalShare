from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.report import Report
from app.models.audit import AuditLog

def test_admin_suspend_and_restore_user(admin_client, test_users):
    """Verify admin can suspend and restore a user, creating audit records."""
    bob_id = test_users['bob'].id

    # Suspend Bob
    resp_sus = admin_client.post(f'/admin/user/{bob_id}/toggle-suspend', follow_redirects=True)
    assert resp_sus.status_code == 200
    assert b'suspended' in resp_sus.data

    with admin_client.application.app_context():
        bob = User.query.get(bob_id)
        assert bob.is_suspended is True

        # Check audit log
        audit = AuditLog.query.filter_by(target_type='user', target_id=bob_id).first()
        assert audit is not None
        assert audit.action == 'suspend_user'

    # Restore Bob
    resp_res = admin_client.post(f'/admin/user/{bob_id}/toggle-suspend', follow_redirects=True)
    assert resp_res.status_code == 200
    assert b'restored' in resp_res.data

    with admin_client.application.app_context():
        bob = User.query.get(bob_id)
        assert bob.is_suspended is False


def test_admin_resolve_community_report(admin_client, test_users):
    """Verify admin can review and resolve community reports."""
    with admin_client.application.app_context():
        rep = Report(
            reporter_id=test_users['alice'].id,
            reported_user_id=test_users['bob'].id,
            reason='spam',
            details='User is posting duplicate promotional requests',
            status='open'
        )
        db.session.add(rep)
        db.session.commit()
        rep_id = rep.id

    # Admin takes corrective action
    resp = admin_client.post(f'/admin/report/{rep_id}/action', data={
        'resolution': 'action_taken',
        'action_note': 'Removed offending posts and issued warning'
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b'marked as action_taken' in resp.data

    with admin_client.application.app_context():
        updated_rep = Report.query.get(rep_id)
        assert updated_rep.status == 'action_taken'
        assert 'Removed offending posts' in updated_rep.action_taken
