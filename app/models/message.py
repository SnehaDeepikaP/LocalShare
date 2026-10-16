from datetime import datetime, timezone
from app.extensions import db

class ExchangeMessage(db.Model):
    __tablename__ = 'exchange_messages'

    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    sender = db.relationship('User', backref=db.backref('sent_messages', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'exchange_id': self.exchange_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name if self.sender else 'Member',
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%b %d, %Y %I:%M %p') if self.created_at else ''
        }

    def __repr__(self):
        return f"<ExchangeMessage id={self.id} exchange_id={self.exchange_id} sender_id={self.sender_id}>"
