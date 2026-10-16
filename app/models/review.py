from datetime import datetime, timezone
from app.extensions import db

class ExchangeReview(db.Model):
    __tablename__ = 'exchange_reviews'
    __table_args__ = (db.UniqueConstraint('exchange_id', 'reviewer_id', name='uq_exchange_reviewer'),)

    id = db.Column(db.Integer, primary_key=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id', ondelete='CASCADE'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    was_reused_or_repaired = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref=db.backref('reviews_written', lazy='dynamic'))
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref=db.backref('reviews_received', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'exchange_id': self.exchange_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else 'Member',
            'reviewee_id': self.reviewee_id,
            'rating': self.rating,
            'comment': self.comment,
            'was_reused_or_repaired': self.was_reused_or_repaired,
            'created_at': self.created_at.strftime('%b %d, %Y') if self.created_at else ''
        }

    def __repr__(self):
        return f"<ExchangeReview id={self.id} rating={self.rating} from={self.reviewer_id} to={self.reviewee_id}>"
