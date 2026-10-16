from datetime import datetime, timezone
from app.extensions import db

VALID_REPORT_REASONS = ['spam', 'inappropriate', 'scam', 'harassment', 'duplicate', 'other']
VALID_REPORT_STATUSES = ['open', 'reviewed', 'dismissed', 'action_taken']

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True, index=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    reason = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open', index=True)
    action_taken = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref='reports_against')

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'post_id': self.post_id,
            'reported_user_id': self.reported_user_id,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Report id={self.id} reason='{self.reason}' status='{self.status}'>"
