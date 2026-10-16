from datetime import datetime, timezone
from app.extensions import db

VALID_REQUEST_STATUSES = ['pending', 'accepted', 'declined', 'completed', 'cancelled']

class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.String(255), nullable=True)  # Safe optional communication info
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    response_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_accepted(self):
        return self.status == 'accepted'

    @property
    def is_completed(self):
        return self.status == 'completed'

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'requester_id': self.requester_id,
            'message': self.message,
            'contact_info': self.contact_info,
            'status': self.status,
            'response_note': self.response_note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<ExchangeRequest id={self.id} post_id={self.post_id} status='{self.status}'>"
